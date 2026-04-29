<#
.SYNOPSIS
    Get Microsoft Fabric Notebook Job Instances using REST API

.DESCRIPTION
    This script retrieves and displays Fabric Notebook job instances using the Fabric REST API.
    It handles Azure CLI authentication and lists all job instances for a specified notebook,
    displaying detailed information about each job instance including status, start/end times,
    and failure details if applicable.

.PARAMETER WorkspaceId
    The workspace ID (GUID) containing the notebook

.PARAMETER NotebookId
    The notebook ID (GUID) to retrieve job instances for

.PARAMETER TimeoutSeconds
    Timeout in seconds for API requests (defaults to 240)

.EXAMPLE
    .\Get-NotebookJobError.ps1 -WorkspaceId "aaaabbbb-0000-cccc-1111-dddd2222eeee" -NotebookId "bbbbcccc-1111-dddd-2222-eeee3333ffff"
    
    Retrieves and displays all job instances for the specified notebook

.NOTES
    Requires Azure Developer CLI (azd) or Azure CLI (az) to be installed and logged in with appropriate permissions.
    The script will try azd first, then fall back to az if azd is not available.
    
    To authenticate:
    - Run 'azd auth login' for Azure Developer CLI, or
    - Run 'az login' for Azure CLI

    Required Scopes:
    - Item.Read.All or Item.ReadWrite.All

    Required Permissions:
    - Read permissions for the notebook

.LINK
    https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/list-item-job-instances
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')]
    [string]$NotebookId,

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

function Get-NotebookJobInstances {
    <#
    .SYNOPSIS
        Get Notebook job instances from Fabric API
    #>

    try {
        $uri = "workspaces/$WorkspaceId/items/$NotebookId/jobs/instances"
        
        Write-Log "Retrieving notebook job instances"
        $response = Invoke-FabricApiRequest -Uri $uri -Method "GET"
        
        if ($response.StatusCode -eq 200) {
            $jobData = $response.Content | ConvertFrom-Json
            
            if ($jobData.value -and $jobData.value.Count -gt 0) {
                Write-Log "Retrieved $($jobData.value.Count) job instance(s)"
                return $jobData.value
            }
            else {
                Write-Log "No job instances found for this notebook" "WARNING"
                return @()
            }
        }
        else {
            throw "Unexpected response status: $($response.StatusCode)"
        }
    }
    catch {
        throw "Failed to get notebook job instances: $($_.Exception.Message)"
    }
}

function Format-JobInstance {
    <#
    .SYNOPSIS
        Format and display job instance details
    #>
    param(
        [object]$JobInstance,
        [int]$Index
    )

    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "Job Instance #$Index" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    
    Write-Host "Job ID:           " -NoNewline -ForegroundColor Gray
    Write-Host $JobInstance.id
    
    Write-Host "Job Type:         " -NoNewline -ForegroundColor Gray
    Write-Host $JobInstance.jobType
    
    Write-Host "Invoke Type:      " -NoNewline -ForegroundColor Gray
    Write-Host $JobInstance.invokeType
    
    Write-Host "Status:           " -NoNewline -ForegroundColor Gray
    $statusColor = switch ($JobInstance.status) {
        "Completed" { "Green" }
        "Failed" { "Red" }
        "InProgress" { "Yellow" }
        "NotStarted" { "Gray" }
        "Deduped" { "Magenta" }
        default { "White" }
    }
    Write-Host $JobInstance.status -ForegroundColor $statusColor
    
    if ($JobInstance.startTimeUtc) {
        Write-Host "Start Time:       " -NoNewline -ForegroundColor Gray
        Write-Host $JobInstance.startTimeUtc
    }
    
    if ($JobInstance.endTimeUtc) {
        Write-Host "End Time:         " -NoNewline -ForegroundColor Gray
        Write-Host $JobInstance.endTimeUtc
    }
    
    if ($JobInstance.failureReason) {
        Write-Host "Failure Reason:   " -NoNewline -ForegroundColor Gray
        Write-Host $JobInstance.failureReason -ForegroundColor Red
    }
    
    if ($JobInstance.rootActivityId) {
        Write-Host "Root Activity ID: " -NoNewline -ForegroundColor Gray
        Write-Host $JobInstance.rootActivityId
    }
}

# Main execution
try {
    Write-Log "Retrieving job instances for notebook: $NotebookId in workspace: $WorkspaceId"
    
    # Get job instances
    $jobInstances = Get-NotebookJobInstances
    
    if ($jobInstances.Count -eq 0) {
        Write-Log "No job instances to display"
    }
    else {
        # Display each job instance
        for ($i = 0; $i -lt $jobInstances.Count; $i++) {
            Format-JobInstance -JobInstance $jobInstances[$i] -Index ($i + 1)
        }
        
        Write-Host ""
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host "Total Job Instances: $($jobInstances.Count)" -ForegroundColor Cyan
        Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    }
    
    Write-Log "Script completed successfully"
}
catch {
    Write-Log "Script execution failed: $($_.Exception.Message)" "ERROR"
    exit 1
}
