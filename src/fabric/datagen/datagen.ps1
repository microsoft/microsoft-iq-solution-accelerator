#!/usr/bin/env powershell
<#
.SYNOPSIS
    Comprehensive Data Generation Orchestrator
    
.DESCRIPTION
    Interactive data generation workflow that guides you through:
    1. Generates realistic sales data across all product categories  
    2. Auto-scales and generates inventory data based on sales volume
    3. Integrates sales patterns with inventory management and procurement
    
    Simply run: .\Run-DataGeneration.ps1
    The script will ask for dates and options with sensible defaults.
    
.EXAMPLE
    .\Run-DataGeneration.ps1
    # Interactive mode with guided prompts and smart defaults
    
.NOTES
    Authors: Doc Gail Zhou and GitHub Copilot
    Date: March 6, 2026
    Requires: Python 3.x with required packages (pandas, numpy, matplotlib)
#>

# No parameters needed - fully interactive!
param()

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = 'Continue'

# Set UTF-8 encoding for better emoji support
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Color functions for better output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Info { Write-ColorOutput Cyan $args }  
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }

# Banner
Write-Host @"
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                        🏢 COMPREHENSIVE DATA GENERATION SUITE 🏢                    ║
║                                                                                      ║
║  🏭 Phase 1: Sales Data Generation (All Product Categories)                         ║
║  📦 Phase 2: Inventory Data Generation (Auto-Scaled to Sales Volume)                ║
║                                                                                      ║
║  📊 Generates: Sales → Orders → Inventory → Purchase Orders                         ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host ""

# Validate date format function
function Test-DateFormat {
    param([string]$Date)
    try {
        $parsedDate = [DateTime]::ParseExact($Date, "yyyy-MM-dd", $null)
        return $true
    } catch {
        return $false
    }
}

# Calculate smart defaults for two-phase generation
$DefaultSalesStartDate = "2025-01-01"  # default start date for sales data
$DefaultSalesEndDate = "2026-04-30"    # default end date for sales data
$DefaultInventoryStartDate = "2025-07-01" # default start date for inventory data
$DefaultInventoryEndDate = "2026-04-30"   # default end date for inventory data

# Helper: calculate human-readable duration label from two date strings
function Get-DurationLabel($startStr, $endStr) {
    $s = [DateTime]::ParseExact($startStr, "yyyy-MM-dd", $null)
    $e = [DateTime]::ParseExact($endStr,   "yyyy-MM-dd", $null)
    $totalMonths = ($e.Year - $s.Year) * 12 + $e.Month - $s.Month
    if ($totalMonths -ge 12) {
        $years  = [Math]::Floor($totalMonths / 12)
        $months = $totalMonths % 12
        if ($months -eq 0) { return "$years yr" }
        return "$years yr $months mo"
    }
    return "$totalMonths months"
}

# Interactive configuration with smart defaults
Write-Info "📅 Two-Phase Data Generation Configuration"
Write-Host "   Let's set up your business data simulation with smart defaults!" -ForegroundColor Gray
Write-Host ""

Write-Host "   🎯 Two-Phase Strategy:" -ForegroundColor Yellow
Write-Host "   • 📈 Sales Data: Long history for trend analysis" -ForegroundColor Gray
Write-Host "   • 📦 Inventory Data: Recent period for current operations" -ForegroundColor Gray
Write-Host ""

# Date range input with defaults
$salesLabel  = Get-DurationLabel $DefaultSalesStartDate  $DefaultSalesEndDate
$inventoryLabel = Get-DurationLabel $DefaultInventoryStartDate $DefaultInventoryEndDate
Write-Host "📅 Date Range Setup:" -ForegroundColor Cyan
Write-Host "   📈 Sales Data Default: $DefaultSalesStartDate to $DefaultSalesEndDate ($salesLabel)" -ForegroundColor Green
Write-Host "   📦 Inventory Data Default: $DefaultInventoryStartDate to $DefaultInventoryEndDate ($inventoryLabel)" -ForegroundColor Green
Write-Host ""

$UseDefaults = Read-Host "   Use default date ranges? (Press Enter for YES, or type 'no')"
if ($UseDefaults -eq "" -or $UseDefaults -eq "Y" -or $UseDefaults -eq "y") {
    $SalesStartDate = $DefaultSalesStartDate
    $SalesEndDate = $DefaultSalesEndDate
    $InventoryStartDate = $DefaultInventoryStartDate
    $InventoryEndDate = $DefaultInventoryEndDate
    Write-Host "   ✅ Using defaults:" -ForegroundColor Green
    Write-Host "      Sales:  $SalesStartDate to $SalesEndDate ($salesLabel)" -ForegroundColor White
    Write-Host "      Inventory: $InventoryStartDate to $InventoryEndDate ($inventoryLabel)" -ForegroundColor White
} else {
    Write-Host "   📝 Custom date ranges:" -ForegroundColor Yellow
    Write-Host ""
    
    # Get sales start date
    Write-Host "   📈 Sales Data Period:" -ForegroundColor Cyan
    do {
        $SalesStartDate = Read-Host "      Sales start date (YYYY-MM-DD)"
        if (-not (Test-DateFormat $SalesStartDate)) {
            Write-Warning "      ⚠️  Invalid date format. Please use YYYY-MM-DD format."
            $SalesStartDate = $null
        }
    } while (-not $SalesStartDate)
    
    # Get sales end date  
    do {
        $SalesEndDate = Read-Host "      Sales end date (YYYY-MM-DD)"
        if (-not (Test-DateFormat $SalesEndDate)) {
            Write-Warning "      ⚠️  Invalid date format. Please use YYYY-MM-DD format."
            $SalesEndDate = $null
        } else {
            # Validate end date is after start date
            $salesStartDt = [DateTime]::ParseExact($SalesStartDate, "yyyy-MM-dd", $null)
            $salesEndDt = [DateTime]::ParseExact($SalesEndDate, "yyyy-MM-dd", $null)
            if ($salesEndDt -le $salesStartDt) {
                Write-Warning "      ⚠️  End date must be after start date."
                $SalesEndDate = $null
            }
        }
    } while (-not $SalesEndDate)
    
    Write-Host ""
    
    # Get inventory start date
    Write-Host "   📦 Inventory Data Period:" -ForegroundColor Blue
    do {
        $InventoryStartDate = Read-Host "      Inventory data start date (YYYY-MM-DD)"
        if (-not (Test-DateFormat $InventoryStartDate)) {
            Write-Warning "      ⚠️  Invalid date format. Please use YYYY-MM-DD format."
            $InventoryStartDate = $null
        }
    } while (-not $InventoryStartDate)
    
    # Get inventory end date  
    do {
        $InventoryEndDate = Read-Host "      Inventory data end date (YYYY-MM-DD)"
        if (-not (Test-DateFormat $InventoryEndDate)) {
            Write-Warning "      ⚠️  Invalid date format. Please use YYYY-MM-DD format."
            $InventoryEndDate = $null
        } else {
            # Validate end date is after start date
            $inventoryStartDt = [DateTime]::ParseExact($InventoryStartDate, "yyyy-MM-dd", $null)
            $inventoryEndDt = [DateTime]::ParseExact($InventoryEndDate, "yyyy-MM-dd", $null)
            if ($inventoryEndDt -le $inventoryStartDt) {
                Write-Warning "      ⚠️  End date must be after start date."
                $InventoryEndDate = $null
            }
        }
    } while (-not $InventoryEndDate)
}

Write-Host ""

# Feature options with smart defaults
Write-Host "🚀 Generation Features:" -ForegroundColor Cyan

# Business growth (default: Yes)
$GrowthInput = Read-Host "   Enable business growth patterns? (Press Enter for YES, or type 'no')"
$EnableGrowth = ($GrowthInput -eq "" -or $GrowthInput -eq "Y" -or $GrowthInput -eq "y")

# Analytics graphs (default: Yes)  
$GraphsInput = Read-Host "   Generate analytics graphs? (Press Enter for YES, or type 'no')"
$GenerateGraphs = ($GraphsInput -eq "" -or $GraphsInput -eq "Y" -or $GraphsInput -eq "y")

# Copy data to user-specified output folder
$CopyInput = Read-Host "   Copy generated data to a destination folder? (Press Enter for YES, or type 'no')"
$CopyData = ($CopyInput -eq "" -or $CopyInput -eq "Y" -or $CopyInput -eq "y" -or $CopyInput -eq "yes")

if ($CopyData) {
    $DefaultCopyPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "output_copydata" "data"
    $CopyPathInput = Read-Host "   Output folder path (press Enter for default: $DefaultCopyPath)"
    if ($CopyPathInput -eq "") {
        $CopyDataPath = $DefaultCopyPath
    } else {
        $CopyDataPath = $CopyPathInput
    }
}

# Calculate durations
$salesStartDt = [DateTime]::ParseExact($SalesStartDate, "yyyy-MM-dd", $null) 
$salesEndDt = [DateTime]::ParseExact($SalesEndDate, "yyyy-MM-dd", $null)
$salesDuration = ($salesEndDt - $salesStartDt).Days

$inventoryStartDt = [DateTime]::ParseExact($InventoryStartDate, "yyyy-MM-dd", $null) 
$inventoryEndDt = [DateTime]::ParseExact($InventoryEndDate, "yyyy-MM-dd", $null)
$inventoryDuration = ($inventoryEndDt - $inventoryStartDt).Days

Write-Host ""
Write-Info "🗓️  Final Configuration:"
Write-Host "   📈 Sales Data Period:" -ForegroundColor Cyan
Write-Host "     • Start Date: $SalesStartDate" -ForegroundColor White
Write-Host "     • End Date:   $SalesEndDate" -ForegroundColor White  
Write-Host "     • Duration:   $salesDuration days" -ForegroundColor White
Write-Host "   📦 Inventory Data Period:" -ForegroundColor Blue
Write-Host "     • Start Date: $InventoryStartDate" -ForegroundColor White
Write-Host "     • End Date:   $InventoryEndDate" -ForegroundColor White  
Write-Host "     • Duration:   $inventoryDuration days" -ForegroundColor White
Write-Host "   ⚙️  Generation Options:" -ForegroundColor Yellow
Write-Host "     • Growth:     $(if($EnableGrowth) {'Enabled ✅'} else {'Disabled'})" -ForegroundColor White
Write-Host "     • Graphs:     $(if($GenerateGraphs) {'Enabled ✅'} else {'Disabled'})" -ForegroundColor White
Write-Host "     • Copy Data:  $(if($CopyData) {"Enabled ✅ → $CopyDataPath"} else {'Disabled'})" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Starting data generation..." -ForegroundColor Green
Write-Host ""

# Change to script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

try {
    # Phase 1: Sales Data Generation
    Write-Host "🏭 PHASE 1: SALES DATA GENERATION" -ForegroundColor Green -BackgroundColor Black
    Write-Host "═" * 80 -ForegroundColor Green
    
    Write-Info "   Generating comprehensive sales data for all product categories..."
    Write-Info "   • 🏕️  Camping products"
    Write-Info "   • 🍳 Kitchen products"  
    Write-Info "   • ⛷️  Ski products"
    Write-Host ""
    
    # Build sales command
    $SalesArgs = @(
        "main_generate_sales.py"
        "-s", $SalesStartDate
        "-e", $SalesEndDate
    )
    
    if ($EnableGrowth) { $SalesArgs += "--enable-growth" }
    if ($GenerateGraphs) { 
        $SalesArgs += "--graph"
        $SalesArgs += "--no-display"  # Prevent GUI windows in automation
    }
    if ($CopyData) { $SalesArgs += "--copydata"; $SalesArgs += $CopyDataPath }
    
    Write-Host "   Executing: python $($SalesArgs -join ' ')" -ForegroundColor Gray
    Write-Host ""
    
    # Set UTF-8 encoding for Python output
    $env:PYTHONIOENCODING = "utf-8"
    
    # Execute sales generation
    $SalesResult = & python -X utf8 @SalesArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Sales data generation failed with exit code $LASTEXITCODE"
    }
    
    Write-Host ""
    Write-Success "✅ Phase 1 completed successfully!"
    Write-Host ""
    
    Write-Host "📦 PHASE 2: INVENTORY DATA GENERATION (AUTO-SCALED)" -ForegroundColor Blue -BackgroundColor Black
    Write-Host "═" * 80 -ForegroundColor Blue
    
    Write-Info "   Auto-scaling inventory parameters based on sales volume..."
    Write-Info "   • 🏭 Suppliers & product-supplier relationships"
    Write-Info "   • 📦 Inventory levels based on sales velocity"
    Write-Info "   • 📋 Purchase orders scaled to sales demand"
    Write-Info "   • 🔄 Inventory transactions (2-3x sales volume)"
    Write-Info "   • 🚨 Supplier risk events & inventory scenarios"
    Write-Host ""
    
    # Build inventory command with auto-scale
    $InventoryArgs = @(
        "main_generate_inventory.py"
        "-s", $InventoryStartDate
        "-e", $InventoryEndDate
        "--auto-scale"
    )
    
    if ($GenerateGraphs) { 
        $InventoryArgs += "--graph"
        $InventoryArgs += "--no-display"  # Prevent GUI windows in automation
    }
    if ($CopyData) { $InventoryArgs += "--copydata"; $InventoryArgs += $CopyDataPath }
    
    Write-Host "   Executing: python $($InventoryArgs -join ' ')" -ForegroundColor Gray
    Write-Host ""
    
    # Ensure UTF-8 encoding for inventory generation
    $env:PYTHONIOENCODING = "utf-8"
    
    # Execute inventory generation
    $InventoryResult = & python -X utf8 @InventoryArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Inventory data generation failed with exit code $LASTEXITCODE"
    }
    
    Write-Host ""
    Write-Success "✅ Phase 2 completed successfully!"
    Write-Host ""
    
    # Phase 3: Integration Summary
    Write-Host "🔗 PHASE 3: DATA INTEGRATION SUMMARY" -ForegroundColor Magenta -BackgroundColor Black  
    Write-Host "═" * 80 -ForegroundColor Magenta
    
    # Display summary information
    Write-Info "   📊 Generated comprehensive business dataset:"
    Write-Host ""
    
    # Check if summary files exist and display key metrics
    $SalesSummary = "output\sample_sales_data_summary.md"
    $InventorySummary = "output\sample_inventory_data_summary.md" 
    
    if (Test-Path $SalesSummary) {
        $SalesContent = Get-Content $SalesSummary -Raw
        if ($SalesContent -match "Total Orders.*?(\d{1,3}(?:,\d{3})*)" ) {
            Write-Host "   🛒 Total Sales Orders: $($Matches[1])" -ForegroundColor White
        }
        if ($SalesContent -match "Order Lines.*?(\d{1,3}(?:,\d{3})*)" ) {
            Write-Host "   📝 Total Line Items: $($Matches[1])" -ForegroundColor White
        }
        if ($SalesContent -match "Total Sales Value.*?\`$(\d+(?:,\d{3})*(?:\.\d{2})?)" ) {
            Write-Host "   💰 Total Sales Value: `$$($Matches[1])" -ForegroundColor White
        }
    }
    
    if (Test-Path $InventorySummary) {
        $InventoryContent = Get-Content $InventorySummary -Raw  
        if ($InventoryContent -match "Purchase Orders.*?(\d+)" ) {
            Write-Host "   📋 Purchase Orders: $($Matches[1])" -ForegroundColor White
        }
        if ($InventoryContent -match "Inventory Transactions.*?(\d{1,3}(?:,\d{3})*)" ) {
            Write-Host "   🔄 Inventory Transactions: $($Matches[1])" -ForegroundColor White
        }
        if ($InventoryContent -match "Suppliers.*?(\d+)" ) {
            Write-Host "   🏭 Suppliers: $($Matches[1])" -ForegroundColor White
        }
    }
    
    Write-Host ""
    Write-Info "   📁 Output locations:"
    Write-Host "     • Sales data: output/sales/[camping|kitchen|ski]/" -ForegroundColor Gray
    Write-Host "     • Finance data: output/finance/[camping|kitchen|ski]/" -ForegroundColor Gray
    Write-Host "     • Inventory data: output/inventory/" -ForegroundColor Gray  
    
    if ($GenerateGraphs) {
        Write-Host "     • Analytics graphs: output/*.png" -ForegroundColor Gray
    }
    
    if ($CopyData) {
        Write-Host "     • Copied to: $CopyDataPath" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "🎉 DATA GENERATION COMPLETED SUCCESSFULLY!" -ForegroundColor Green -BackgroundColor Black
    Write-Host "═" * 80 -ForegroundColor Green
    Write-Host ""
    Write-Success "✨ Your integrated business dataset is ready for analysis!"
    Write-Host "   Sales: $salesDuration days | Inventory: $inventoryDuration days | Sales → Inventory → Analytics" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ ERROR DURING GENERATION" -ForegroundColor Red -BackgroundColor Black  
    Write-Host "═" * 80 -ForegroundColor Red
    Write-Error "   $($_.Exception.Message)"
    Write-Host ""
    Write-Warning "💡 Troubleshooting tips:"
    Write-Host "   • Ensure Python 3.x is installed and in PATH"
    Write-Host "   • Install required packages: pip install pandas numpy matplotlib" 
    Write-Host "   • Check input files exist in input/ directory"
    Write-Host "   • Verify date format (YYYY-MM-DD)"
    Write-Host ""
    exit 1
}