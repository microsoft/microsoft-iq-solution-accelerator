# Smart Data Generation Suite

### ✨ Auto-Scale Supply Chain Parameters
The supply chain generator automatically calculates optimal parameters based on your sales data.

> **Required Parameters**: All commands require explicit start and end date parameters (`-s` and `-e`) to ensure deterministic, reproducible results.

```bash
python main_generate_supplychain.py --auto-scale -s 2025-01-01 -e 2026-03-31 --copydata .\output_copydata\data
```

**What the --auto-scale does:**

- Analyzes existing sales data from `output/` directory
- Calculates optimal purchase orders (~1 PO per 400-500 line items)  
- Scales inventory transactions (2-3x sales volume)
- Displays calculated vs default parameters
- Uses intelligent date range filtering

### 🎯 PowerShell Orchestration Script
The PowerShell script handles the complete workflow automatically:

## PowerShell Script (Recommended)
**`datagen.ps1`** - Interactive workflow with guided prompts

**Date Range Coordination**: For optimal integration, use the same end date (`-e`) for both sales and supply chain generation. Start dates can differ - sales generation can begin earlier to provide sufficient historical data for supply chain auto-scaling analysis. 

```powershell
# Interactive mode (prompts for dates and options)
.\datagen.ps1
```

## Workflow
1. **Sales Generation**: Creates comprehensive sales data across all categories
2. **Auto-Scale Analysis**: Analyzes sales volume and calculates optimal supply chain parameters  
3. **Supply Chain Generation**: Creates inventory, purchase orders, and transactions scaled to sales
4. **Integration**: Links sales patterns with supply chain operations

## Example Output
```
🚀 Auto-scaling enabled - analyzing existing sales data...
────────────────────────────────────────────────────────────────
📈 Sales Analysis: 50,504 line items from 18,669 orders (Camping, Kitchen, Ski)
📊 Calculated Parameters:
   • Purchase Orders: 112 (was 30)
   • Inventory Transactions: 6,825 (was 500)
✅ Using auto-calculated parameters
```

## Manual Parameter Override
You can override auto-calculated parameters with specific values:
```bash
# Custom parameters with required date range
python main_generate_supplychain.py -s 2025-01-01 -e 2026-03-31 --num-orders 50 --num-transactions 800

# Full manual control with additional options
python main_generate_supplychain.py -s 2025-01-01 -e 2026-03-31 --num-orders 125 --num-transactions 2000 --copydata .\output_copydata\data --graph --no-display
```

## Benefits
- **Realistic Scaling**: Supply chain data matches actual sales volume
- **Time Saving**: No manual parameter calculation needed
- **Integrated Workflow**: One command generates complete business dataset  
- **Intelligent Defaults**: Falls back gracefully when sales data is not available
- **Deterministic Results**: Same input parameters always produce identical outputs
- **Date Consistency**: All generated data uses the specified date range exclusively