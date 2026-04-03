# Quick deploy script using existing resource group and image
param(
    [string]$ResourceGroup = "rg-solo3iqtest",
    [switch]$SkipBuild
)

Write-Host "🚀 Quick WorkIQ MCP Deployment to $ResourceGroup" -ForegroundColor Green

# Set environment variables
$env:AZURE_RESOURCE_GROUP = $ResourceGroup
$env:WORKIQ_USER = "gpickett@microsoft.com" 
$env:ACR_NAME = "gpickettacr"

# Check if resource group exists
Write-Host "📋 Checking resource group..." -ForegroundColor Blue
$rgExists = az group show --name $ResourceGroup --query "name" -o tsv 2>$null
if (-not $rgExists) {
    Write-Host "❌ Resource group '$ResourceGroup' not found!" -ForegroundColor Red
    Write-Host "Available resource groups:" -ForegroundColor Yellow
    az group list --query "[].name" -o table
    exit 1
}

Write-Host "✅ Resource group '$ResourceGroup' found" -ForegroundColor Green

if ($SkipBuild) {
    Write-Host "⚡ Skipping build - using existing image" -ForegroundColor Cyan
    
    # Deploy directly with existing image
    $AcrName = $env:ACR_NAME
    $WorkiqUser = $env:WORKIQ_USER
    
    Write-Host "🌐 Deploying Container Apps infrastructure..." -ForegroundColor Blue
    $deploymentResult = az deployment group create `
      --resource-group $ResourceGroup `
      --template-file infra/deploy_workiq_mcp_container.bicep `
      --parameters `
        containerImage="$AcrName.azurecr.io/workiq-mcp:latest" `
        workiqUser="$WorkiqUser" `
      --query "properties.outputs" `
      --output json | ConvertFrom-Json

    Write-Host "✅ WorkIQ MCP Server deployment complete!" -ForegroundColor Green
    Write-Host "🔗 MCP Server URL: $($deploymentResult.containerAppUrl.value)" -ForegroundColor Yellow
    Write-Host "📧 Configured for user: $WorkiqUser" -ForegroundColor Yellow

    # Save URL for agent configuration
    @{
        mcp_server_url = $deploymentResult.containerAppUrl.value
        workiq_user = $WorkiqUser
        deployment_time = Get-Date
    } | ConvertTo-Json | Out-File "workiq_mcp_config.json"

    Write-Host "💾 Configuration saved to workiq_mcp_config.json" -ForegroundColor Cyan
} else {
    # Run the full deployment
    Write-Host "🏗️ Starting full deployment..." -ForegroundColor Blue
    .\deploy_workiq_mcp.ps1 -ResourceGroup $ResourceGroup
}