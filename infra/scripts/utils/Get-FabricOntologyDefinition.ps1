<#
.SYNOPSIS
    Get Microsoft Fabric Ontology Definition using REST API

.DESCRIPTION
    This script retrieves and decodes Microsoft Fabric Ontology definitions using the Fabric REST API.
    It handles Azure CLI authentication, retrieves the ontology name, and downloads the definition to a
    folder named [ontologyName].Ontology. The script decodes the Base64 payload to provide readable
    ontology configuration including entity types, their definitions, and other components.

    Note: This API is blocked for an ontology with an encrypted sensitivity label.
    Note: Ontology item is currently in Preview.

.PARAMETER WorkspaceId
    The workspace ID (GUID) containing the ontology

.PARAMETER OntologyId
    The ontology ID (GUID) to retrieve

.PARAMETER FolderPath
    Path to save the decoded definition files (defaults to "src/fabric/definitions/[ontologyName].Ontology" relative to repository root)

.PARAMETER CustomOntologyName
    Optional custom ontology name that replaces the retrieved name for folder naming. If provided, skips the metadata retrieval and uses this value to name the folder as [CustomOntologyName].Ontology

.PARAMETER Format
    Optional format parameter for the ontology definition (as supported by the API)

.EXAMPLE
    .\Get-FabricOntologyDefinition.ps1 -WorkspaceId "aaaabbbb-0000-cccc-1111-dddd2222eeee" -OntologyId "bbbbcccc-1111-dddd-2222-eeee3333ffff"
    
    Retrieves the ontology definition and saves it to src/fabric/definitions/[OntologyName].Ontology

.EXAMPLE
    .\Get-FabricOntologyDefinition.ps1 -WorkspaceId "aaaabbbb-0000-cccc-1111-dddd2222eeee" -OntologyId "bbbbcccc-1111-dddd-2222-eeee3333ffff" -CustomOntologyName "MyCustomOntology"
    
    Uses the custom name "MyCustomOntology" to create MyCustomOntology.Ontology folder, replacing the retrieved name

.EXAMPLE
    .\Get-FabricOntologyDefinition.ps1 -WorkspaceId "aaaabbbb-0000-cccc-1111-dddd2222eeee" -OntologyId "bbbbcccc-1111-dddd-2222-eeee3333ffff" -FolderPath "C:\temp\ontology"
    
    Retrieves the ontology definition and saves it to the specified custom folder path

.NOTES
    Requires Azure Developer CLI (azd) or Azure CLI (az) to be installed and logged in with appropriate permissions.
    The script will try azd first, then fall back to az if azd is not available.
    
    To authenticate:
    - Run 'azd auth login' for Azure Developer CLI, or
    - Run 'az login' for Azure CLI

    Required Scopes:
    - Item.ReadWrite.All

    Required Permissions:
    - Read and write permissions for the ontology

.LINK
    https://learn.microsoft.com/en-us/rest/api/fabric/ontology/items/get-ontology
    https://learn.microsoft.com/en-us/rest/api/fabric/ontology/items/get-ontology-definition
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')]
    [string]$OntologyId,

    [Parameter(Mandatory = $false)]
    [string]$FolderPath = $null,

    [Parameter(Mandatory = $false)]
    [string]$CustomOntologyName = $null,

    [Parameter(Mandatory = $false)]
    [string]$Format,

    [Parameter(Mandatory = $false)]
    [int]$TimeoutSeconds = 240
)

# Global variables
$script:ApiUrl = "https://api.fabric.microsoft.com/v1"
$script:ResourceUrl = "https://api.fabric.microsoft.com"
$script:AccessToken = $null
$script:TokenExpiry = $null

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARNING", "ERROR")]
        [string]$Level = "INFO"
    )

    $icon = switch ($Level) {
        "ERROR" { "❌" }
        "WARNING" { "⚠️" }
        default { "ℹ️" }
    }

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "$icon [$timestamp] $Message" -ForegroundColor $(
        switch ($Level) {
            "ERROR" { "Red" }
            "WARNING" { "Yellow" }
            default { "White" }
        }
    )
}

function Get-AuthToken {
    <#
    .SYNOPSIS
        Get or refresh authentication token for Fabric API from azd or az CLI
    #>

    try {
        # Check if we need to refresh the token (refresh 5 minutes before expiry)
        $currentTime = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

        if (-not $script:AccessToken -or ($script:TokenExpiry -and $currentTime -gt ($script:TokenExpiry - 300))) {
            $tokenData = $null
            $authMethod = $null

            # Try Azure Developer CLI (azd) first
            try {
                Write-Log "Attempting to get authentication token from Azure Developer CLI (azd)"
                $azdTokenResponse = azd auth token --scope $script:ResourceUrl --output json 2>$null
                
                if ($LASTEXITCODE -eq 0 -and $azdTokenResponse) {
                    $tokenData = $azdTokenResponse | ConvertFrom-Json
                    
                    # azd returns token and expiresOn
                    if ($tokenData.token) {
                        $script:AccessToken = $tokenData.token
                        $authMethod = "azd"
                        
                        # Parse expiry time
                        if ($tokenData.expiresOn) {
                            $expiryDateTime = [DateTime]::Parse($tokenData.expiresOn)
                            $script:TokenExpiry = [DateTimeOffset]::new($expiryDateTime).ToUnixTimeSeconds()
                        }
                        else {
                            # Default to 1 hour if no expiry provided
                            $script:TokenExpiry = $currentTime + 3600
                        }
                    }
                }
            }
            catch {
                Write-Log "Azure Developer CLI (azd) not available or failed: $($_.Exception.Message)" "WARNING"
            }

            # Fall back to Azure CLI (az) if azd didn't work
            if (-not $authMethod) {
                try {
                    Write-Log "Attempting to get authentication token from Azure CLI (az)"
                    $azTokenResponse = az account get-access-token --resource $script:ResourceUrl --query "{accessToken:accessToken,expiresOn:expiresOn}" --output json 2>$null

                    if ($LASTEXITCODE -eq 0 -and $azTokenResponse) {
                        $tokenData = $azTokenResponse | ConvertFrom-Json
                        $script:AccessToken = $tokenData.accessToken
                        $authMethod = "az"

                        # Parse expiry time (Azure CLI returns ISO 8601 format)
                        $expiryDateTime = [DateTime]::Parse($tokenData.expiresOn)
                        $script:TokenExpiry = [DateTimeOffset]::new($expiryDateTime).ToUnixTimeSeconds()
                    }
                }
                catch {
                    Write-Log "Azure CLI (az) authentication failed: $($_.Exception.Message)" "ERROR"
                }
            }

            if (-not $authMethod) {
                throw "Authentication failed with both azd and az. Please run 'azd auth login' or 'az login' first."
            }

            Write-Log "Authentication successful using $authMethod"
        }

        return $script:AccessToken
    }
    catch {
        throw "Authentication failed: $($_.Exception.Message)"
    }
}

function Invoke-FabricApiRequest {
    <#
    .SYNOPSIS
        Make HTTP request to Fabric API with error handling and authentication
    #>
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [object]$Body = $null,
        [hashtable]$Headers = @{},
        [int]$TimeoutSec = $TimeoutSeconds,
        [int]$MaxRetries = 3
    )

    $fullUrl = "$script:ApiUrl/$($Uri.TrimStart('/'))"
    $retryCount = 0

    do {
        try {
            Write-Log "Making $Method request to $fullUrl $(if ($retryCount -gt 0) { "(attempt $($retryCount + 1))" })"

            # Prepare headers with authentication
            $requestHeaders = @{
                'Content-Type'  = 'application/json; charset=utf-8'
                'Authorization' = "Bearer $(Get-AuthToken)"
            }

            # Add custom headers
            foreach ($key in $Headers.Keys) {
                $requestHeaders[$key] = $Headers[$key]
            }

            # Prepare request parameters
            $requestParams = @{
                Uri             = $fullUrl
                Method          = $Method
                Headers         = $requestHeaders
                TimeoutSec      = $TimeoutSec
                UseBasicParsing = $true
            }

            if ($Body) {
                if ($Body -is [string]) {
                    $requestParams.Body = $Body
                }
                else {
                    $requestParams.Body = $Body | ConvertTo-Json -Depth 10 -Compress
                }
            }

            $response = Invoke-WebRequest @requestParams

            # Log request ID if available
            $requestId = $response.Headers['requestId']
            if ($requestId) {
                Write-Log "Request ID: $requestId"
            }

            # Handle different status codes
            switch ($response.StatusCode) {
                200 {
                    Write-Log "Request completed successfully"
                    return $response
                }
                202 {
                    $retryAfterHeader = if ($response.Headers['Retry-After']) { [int]([string]$response.Headers['Retry-After']) } else { $null }
                    $retryMsg = if ($retryAfterHeader) { " (server suggests retry after $retryAfterHeader seconds)" } else { "" }
                    Write-Log "Long-running operation detected$retryMsg"
                    return $response
                }
                429 {
                    # Rate limiting - retry with exponential backoff
                    $retryAfter = if ($response.Headers['Retry-After']) {
                        [int]([string]$response.Headers['Retry-After'])
                    }
                    else {
                        [Math]::Min(60, [Math]::Pow(2, $retryCount))
                    }

                    $retryAfter = [Math]::Min($retryAfter, 300)  # Cap at 5 minutes

                    Write-Log "Rate limit exceeded. Retrying in $retryAfter seconds... (attempt $($retryCount + 1)/$MaxRetries)" "WARNING"
                    Start-Sleep -Seconds $retryAfter
                    $retryCount++
                    continue
                }
                default {
                    $errorMsg = "API request failed with status $($response.StatusCode)"

                    try {
                        $errorResponse = $response.Content | ConvertFrom-Json
                        Write-Log "Error response: $($errorResponse | ConvertTo-Json -Depth 5)" "ERROR"

                        if ($errorResponse.error) {
                            $errorMsg += ": $($errorResponse.error.message)"
                        }
                    }
                    catch {
                        $errorMsg += ": $($response.Content.Substring(0, [Math]::Min(500, $response.Content.Length)))"
                    }

                    throw $errorMsg
                }
            }
        }
        catch {
            if ($_.Exception -is [System.Net.WebException] -and $_.Exception.Response.StatusCode -eq 429 -and $retryCount -lt $MaxRetries) {
                # Handle rate limiting in older PowerShell versions
                $retryAfter = 60
                Write-Log "Rate limit exceeded. Retrying in $retryAfter seconds... (attempt $($retryCount + 1)/$MaxRetries)" "WARNING"
                Start-Sleep -Seconds $retryAfter
                $retryCount++
                continue
            }

            throw "Request failed: $($_.Exception.Message)"
        }
    } while ($retryCount -lt $MaxRetries)

    throw "Maximum retries ($MaxRetries) exceeded"
}

function ConvertFrom-Base64 {
    <#
    .SYNOPSIS
        Decode Base64 string to UTF-8 text
    #>
    param(
        [string]$Base64String
    )

    try {
        $bytes = [System.Convert]::FromBase64String($Base64String)
        return [System.Text.Encoding]::UTF8.GetString($bytes)
    }
    catch {
        throw "Failed to decode Base64 string: $($_.Exception.Message)"
    }
}

function Get-OntologyMetadata {
    <#
    .SYNOPSIS
        Get Ontology metadata including name from Fabric API
    #>

    try {
        $uri = "workspaces/$WorkspaceId/ontologies/$OntologyId"
        
        Write-Log "Retrieving ontology metadata"
        $response = Invoke-FabricApiRequest -Uri $uri -Method "GET"
        
        if ($response.StatusCode -eq 200) {
            $ontologyData = $response.Content | ConvertFrom-Json
            Write-Log "Retrieved ontology: $($ontologyData.displayName)"
            return $ontologyData
        }
        else {
            throw "Unexpected response status: $($response.StatusCode)"
        }
    }
    catch {
        throw "Failed to get ontology metadata: $($_.Exception.Message)"
    }
}

function Get-OntologyDefinition {
    <#
    .SYNOPSIS
        Get and decode Ontology definition from Fabric API
    #>

    try {
        # Build URI with optional format parameter
        $uri = "workspaces/$WorkspaceId/ontologies/$OntologyId/getDefinition"
        if ($Format) {
            $uri += "?format=$Format"
        }

        # Make initial API request
        $response = Invoke-FabricApiRequest -Uri $uri -Method "POST"

        # Always expect 202 for long-running operation
        if ($response.StatusCode -ne 202) {
            throw "Unexpected response status: $($response.StatusCode)"
        }

        # Poll for completion
        $location = [string]$response.Headers['Location']
        $retryAfter = if ($response.Headers['Retry-After']) { [int]([string]$response.Headers['Retry-After']) } else { 20 }
        
        Write-Log "Polling every $retryAfter seconds (typical operation completes in 20-60 seconds)"
        
        do {
            Start-Sleep -Seconds $retryAfter
            
            $statusResponse = Invoke-WebRequest -Uri $location -Headers @{
                'Authorization' = "Bearer $(Get-AuthToken)"
            } -UseBasicParsing
            
            $operationStatus = $statusResponse.Content | ConvertFrom-Json
            
            if ($operationStatus.status -eq "Succeeded") {
                # Retrieve result from Location header
                $resultLocation = [string]$statusResponse.Headers['Location']
                
                $response = Invoke-WebRequest -Uri $resultLocation -Headers @{
                    'Authorization' = "Bearer $(Get-AuthToken)"
                } -UseBasicParsing
                
                break
            }
            elseif ($operationStatus.status -eq "Failed") {
                throw "Operation failed: $($operationStatus.error | ConvertTo-Json -Compress)"
            }
        } while ($true)


        # Parse and validate response
        $responseData = $response.Content | ConvertFrom-Json
        
        if (-not $responseData.definition -or -not $responseData.definition.parts) {
            throw "Invalid response format: missing definition or parts"
        }

        Write-Log "Retrieved ontology definition with $($responseData.definition.parts.Count) part(s)"

        # Decode all parts
        $decodedParts = @{}

        foreach ($part in $responseData.definition.parts) {
            if ($part.payloadType -eq "InlineBase64") {
                $decodedParts[$part.path] = ConvertFrom-Base64 -Base64String $part.payload
            }
        }

        Write-Log "Successfully decoded ontology definition"

        # Save to files
        if ($FolderPath) {
            if (-not (Test-Path $FolderPath)) {
                New-Item -ItemType Directory -Path $FolderPath -Force | Out-Null
            }

            foreach ($partPath in $decodedParts.Keys) {
                $filePath = Join-Path $FolderPath $partPath
                $fileDir = Split-Path -Parent $filePath
                
                if (-not (Test-Path $fileDir)) {
                    New-Item -ItemType Directory -Path $fileDir -Force | Out-Null
                }

                if ($partPath -like "*.json" -and -not $decodedParts[$partPath].StartsWith("[")) {
                    $jsonContent = $decodedParts[$partPath] | ConvertFrom-Json
                    $jsonContent | ConvertTo-Json -Depth 10 | Set-Content -Path $filePath -Encoding UTF8 -Force
                }
                else {
                    $decodedParts[$partPath] | Set-Content -Path $filePath -Encoding UTF8 -Force
                }
            }

            Write-Log "Saved $($decodedParts.Count) files to $FolderPath"
        }

        # Return the decoded parts
        return $decodedParts
    }
    catch {
        throw "Failed to get ontology definition: $($_.Exception.Message)"
    }
}

# Main execution
try {
    # Determine ontology name
    if ($CustomOntologyName) {
        Write-Log "Using custom ontology name: $CustomOntologyName"
        $ontologyName = $CustomOntologyName
    }
    else {
        Write-Log "Retrieving ontology metadata: $OntologyId from workspace: $WorkspaceId"
        # Get ontology metadata to retrieve the name
        $ontologyMetadata = Get-OntologyMetadata
        $ontologyName = $ontologyMetadata.displayName
    }
    
    # Calculate default folder path if not provided
    if (-not $FolderPath) {
        $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
        $RepoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ScriptDir))
        $definitionsPath = Join-Path $RepoRoot "src" | Join-Path -ChildPath "fabric" | Join-Path -ChildPath "definitions"
        $FolderPath = Join-Path $definitionsPath "$ontologyName.Ontology"
    }

    Write-Log "Retrieving ontology definition for: $ontologyName"
    Write-Log "Output folder: $FolderPath"

    # Get ontology definition
    $ontologyDefinition = Get-OntologyDefinition

    Write-Log "Ontology definition retrieved and saved successfully"
}
catch {
    Write-Log "Script execution failed: $($_.Exception.Message)" "ERROR"
    exit 1
}

Write-Log "Script completed successfully"
