<#
.SYNOPSIS
    Interactive wrapper to configure and run the access-bootstrap Terraform script.

.DESCRIPTION
    This script does not provision Azure resources, so it does not prompt for a
    location or offer to create a new resource group. It only assigns roles and
    creates Entra/PIM groups scoped to an existing subscription, resource group,
    and Azure AI Foundry resource that must already exist.
#>

$ErrorActionPreference = "Stop"

Write-Host "== Terraform access bootstrap ==" -ForegroundColor Cyan

# --- Sign in ---
az account show *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Signing in to Azure..." -ForegroundColor Yellow
    az login | Out-Null
}

# --- Select subscription ---
Write-Host "`nFetching subscriptions..." -ForegroundColor Yellow
$subs = az account list --output json | ConvertFrom-Json
if (-not $subs -or $subs.Count -eq 0) {
    throw "No subscriptions found for the signed-in account."
}
for ($i = 0; $i -lt $subs.Count; $i++) {
    Write-Host "  [$i] $($subs[$i].name)  ($($subs[$i].id))"
}
$subIndex = Read-Host "`nSelect a subscription by number"
$subscription = $subs[[int]$subIndex]
az account set --subscription $subscription.id
Write-Host "Using subscription: $($subscription.name)" -ForegroundColor Green

# --- Environment name ---
$environment = Read-Host "`nEnter an environment name (e.g. hackathon, dev, poc)"
$groupPrefix = Read-Host "Enter a group name prefix (e.g. your team or org short name)"

# --- Select existing resource group ---
# No "create new resource group" option: this script only assigns access to
# resources that already exist (the Fabric capacity and/or Foundry resource).
Write-Host "`nFetching resource groups in '$($subscription.name)'..." -ForegroundColor Yellow
$rgs = az group list --output json | ConvertFrom-Json
if (-not $rgs -or $rgs.Count -eq 0) {
    throw "No resource groups found in this subscription. Create the resource group and the Fabric/Foundry resources first, then re-run this script."
}
for ($i = 0; $i -lt $rgs.Count; $i++) {
    Write-Host "  [$i] $($rgs[$i].name)"
}
$rgIndex = Read-Host "`nSelect the resource group that contains your Fabric/Foundry resources"
$resourceGroup = $rgs[[int]$rgIndex].name

# --- Foundry resource ---
Write-Host "`nFetching Azure AI Foundry / Cognitive Services resources in '$resourceGroup'..." -ForegroundColor Yellow
$foundryResources = az cognitiveservices account list --resource-group $resourceGroup --output json | ConvertFrom-Json
$foundryResourceId = $null
if ($foundryResources -and $foundryResources.Count -gt 0) {
    for ($i = 0; $i -lt $foundryResources.Count; $i++) {
        Write-Host "  [$i] $($foundryResources[$i].name)"
    }
    $foundryIndex = Read-Host "`nSelect the Foundry resource (or press Enter to skip)"
    if ($foundryIndex -ne "") {
        $foundryResourceId = $foundryResources[[int]$foundryIndex].id
    }
} else {
    Write-Host "No Foundry/Cognitive Services resources found in '$resourceGroup'." -ForegroundColor Yellow
    $foundryResourceId = Read-Host "Paste the full Foundry resource ID (or press Enter to skip)"
    if ($foundryResourceId -eq "") { $foundryResourceId = $null }
}

# --- People ---
$owners = Read-Host "`nEnter owner UPN(s), comma-separated"
$eligibleMembers = Read-Host "Enter eligible contributor UPN(s), comma-separated"
$permanentMembers = Read-Host "Enter permanent reader UPN(s), comma-separated (optional)"

function ConvertTo-TfList($csv) {
    if ([string]::IsNullOrWhiteSpace($csv)) { return "[]" }
    $items = $csv -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
    $quoted = $items | ForEach-Object { "  `"$_`"," }
    return "[`n" + ($quoted -join "`n") + "`n]"
}

# --- Write terraform.tfvars ---
$tfvarsPath = Join-Path $PSScriptRoot "terraform.tfvars"
$foundryLine = if ($foundryResourceId) { "foundry_resource_id = `"$foundryResourceId`"" } else { "# foundry_resource_id not set - Foundry roles will default to the resource-group scope" }

@"
environment         = "$environment"
subscription_id     = "$($subscription.id)"
resource_group_name = "$resourceGroup"
group_prefix        = "$groupPrefix"

$foundryLine

owners            = $(ConvertTo-TfList $owners)
eligible_members  = $(ConvertTo-TfList $eligibleMembers)
permanent_members = $(ConvertTo-TfList $permanentMembers)
"@ | Set-Content -Path $tfvarsPath -Encoding UTF8

Write-Host "`nWrote $tfvarsPath" -ForegroundColor Green

# --- Run Terraform ---
Push-Location $PSScriptRoot
try {
    terraform init
    terraform fmt -check
    terraform validate
    terraform plan -out tfplan
    $apply = Read-Host "`nReview the plan above. Apply it? (y/n)"
    if ($apply -eq "y") {
        terraform apply tfplan
    } else {
        Write-Host "Skipped apply. Re-run 'terraform apply tfplan' when ready." -ForegroundColor Yellow
    }
} finally {
    Pop-Location
}
