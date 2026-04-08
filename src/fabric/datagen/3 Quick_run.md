# Quick Run Examples 

## Prerequisites  
Ensure configuration files exist in `input/` directory:
- `suppliers.json` - Supplier master data
- `warehouses.json` - Warehouse locations and details

```bash
# Program location
cd src\datagen
```

## PowerShell Orchestrator (Runs Both Sequentially and Automatically)

**Interactive Mode** - Simplest approach:

```powershell
cd src\datagen
.\datagen.ps1
```

## Run Separate Processes 

### Sales and Finance Data (Long History)
```bash
python main_generate_sales.py -s 2020-01-01 -e 2026-03-31 --enable-growth --copydata .\output_copydata\data --graph --no-display
```

### Supply Chain Data (Recent Period)

**Auto-Scale (Recommended)** - Analyzes recent sales data automatically:

```bash
python main_generate_supplychain.py -s 2025-01-01 -e 2026-03-31 --auto-scale --copydata .\output_copydata\data --graph --no-display
```

**Manual Parameters** - If you want to produce independent data without sales history:
```bash
python main_generate_supplychain.py -s 2025-01-01 -e 2026-03-31 --num-orders 125 --num-transactions 2000 --copydata .\output_copydata\data --graph --no-display
```

