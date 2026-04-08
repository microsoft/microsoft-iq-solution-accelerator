# Sales & Finance Data Generation Guide

Generates realistic sales and finance data for three business domains: Camping 🏕️, Kitchen 🍳, and Ski ⛷️.

## Command Examples

```bash
# Historical data (6+ years)
python main_generate_sales.py -s 2020-01-01 -e 2026-03-31 --enable-growth --copydata .\output_copydata\data --graph --no-display

# Standard business period
python main_generate_sales.py -s 2025-01-01 -e 2026-04-30 --enable-growth --graph --copydata .\output_copydata\data

```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-s`, `--start-date` | **Required**: Start date (YYYY-MM-DD) |
| `-e`, `--end-date` | **Required**: End date (YYYY-MM-DD) |
| `--camping-only` | Generate only camping domain data |
| `--kitchen-only` | Generate only kitchen domain data |
| `--ski-only` | Generate only ski domain data |
| `--enable-growth` | Enable business growth patterns and market events |
| `--graph` | Generate monthly revenue trend graph |
| `--no-display` | Save graphs without GUI windows (for automation) |
| `--copydata <OUTPUT_DIR>` | Copy generated files to the specified directory (e.g. `.\output_copydata\data`) |



## 📁 Generated Files & Structure

### Output Directory Structure

```
output/
├── finance/
│   ├── camping/
│   │   ├── Account_Samples_Camping.csv
│   │   ├── Invoice_Samples_Camping.csv  
│   │   └── Payment_Samples_Camping.csv
│   ├── kitchen/
│   │   ├── Invoice_Samples_Kitchen.csv  
│   │   └── Payment_Samples_Kitchen.csv
│   └── ski/
│       ├── Invoice_Samples_Ski.csv
│       └── Payment_Samples_Ski.csv
├── sales/
│   ├── camping/
│   │   ├── Order_Samples_Camping.csv
│   │   ├── OrderLine_Samples_Camping.csv
│   │   └── OrderPayment_Camping.csv
│   ├── kitchen/
│   │   ├── Order_Samples_Kitchen.csv
│   │   ├── OrderLine_Samples_Kitchen.csv
│   │   └── OrderPayment_Kitchen.csv
│   └── ski/
│       ├── Order_Samples_Ski.csv
│       ├── OrderLine_Samples_Ski.csv
│       └── OrderPayment_Ski.csv
├── sample_sales_data_summary.md
└── revenue_trend_graph_[daterange].png (with --graph)
```

## 🏗️ Copy to Destination (with --copydata)

The `--copydata <OUTPUT_DIR>` option copies files from **both** the `output/` and `input/` directories to the specified destination, making them ready for Microsoft Fabric lakehouse integration or any other downstream use.

### What gets copied

| Source | Files | Destination |
|--------|-------|-------------|
| `output/` (all subfolders) | All generated `*.csv` files | `<OUTPUT_DIR>/` (structure preserved) |
| `output/` | `sample_sales_data_summary.md` | `<OUTPUT_DIR>/` |
| `input/` | `Product_Samples_*.csv`, `ProductCategory_Samples_*.csv` (9 files) | `<OUTPUT_DIR>/product/` |
| `input/` | `Customer_Samples.csv`, `CustomerAccount_Samples.csv`, `CustomerRelationshipType_Samples.csv`, `CustomerTradeName_Samples.csv`, `Location_Samples.csv` | `<OUTPUT_DIR>/customer/` |

### Copied Directory Structure
```
<OUTPUT_DIR>/
├── finance/
│   ├── camping/ → [All camping finance CSV files]
│   ├── kitchen/ → [All kitchen finance CSV files]
│   └── ski/     → [All ski finance CSV files]
├── sales/
│   ├── camping/ → [All camping sales CSV files]
│   ├── kitchen/ → [All kitchen sales CSV files]
│   └── ski/     → [All ski sales CSV files]
├── product/     → [9 product & category CSV files from input/]
├── customer/    → [5 customer & location CSV files from input/]
└── sample_sales_data_summary.md
```