# Supply Chain Data Generation Guide

Generates supplier management and inventory data with purchase orders and supply chain events.

## Command Examples

```bash
# Standard generation with auto-scaling
python main_generate_supplychain.py -s 2025-01-01 -e 2026-03-31 --auto-scale --graph --copydata .\output_copydata\data --no-display

# Manual parameters
python main_generate_supplychain.py -s 2025-01-01 -e 2026-03-31 --num-orders 30 --num-transactions 500 --graph --no-display

# Inventory only (requires existing supplier data)
python main_generate_supplychain.py -s 2025-01-01 -e 2026-03-31 --inventory-only --graph --no-display
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-s`, `--start-date` | **Required**: Start date (YYYY-MM-DD) |
| `-e`, `--end-date` | **Required**: End date (YYYY-MM-DD) |
| `--auto-scale` | Auto-calculate parameters based on existing sales data |
| `--graph` | Generate supply chain analytics dashboard |
| `--no-display` | Save graphs without GUI windows (for automation) |
| `--copydata <OUTPUT_DIR>` | Copy generated files to the specified directory (e.g. `.\output_copydata\data`) |
| `--num-orders` | Number of purchase orders (default: 30) |
| `--num-transactions` | Number of inventory transactions (default: 500) |
| `--inventory-only` | Generate only inventory data (requires existing supplier data) |
| `--num-events` | Number of supply chain events (default: 15) |

## 📁 Generated Files & Structure

### Output Directory Structure
```
output/
├── supplychain/
│   ├── Suppliers.csv
│   ├── ProductSuppliers.csv
│   └── SupplyChainEvents.csv
├── inventory/
│   ├── Warehouses.csv
│   ├── Inventory.csv
│   ├── InventoryTransactions.csv
│   ├── PurchaseOrders.csv
│   ├── PurchaseOrderItems.csv
│   └── DemandForecast.csv
└── sample_supplychain_data_summary.md
```

### Copy to Destination (with --copydata)
```
<OUTPUT_DIR>/
├── supplychain/       # Generated supplier data (mirrors output structure)
├── inventory/         # Generated inventory data (mirrors output structure)
└── *.md              # Summary reports
```

### Required Input Files
- `input/suppliers.json` - Supplier configuration
- `input/warehouses.json` - Warehouse configuration
- Some products intentionally set to low-stock scenarios for realism

