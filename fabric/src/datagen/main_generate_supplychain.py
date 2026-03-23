"""
Supply Chain Data Generation - Main Orchestrator

This is the main entry point for generating complete supply chain datasets.
Coordinates the generation of:
- Supplier master data and relationships
- Inventory levels and warehouse management  
- Purchase orders and procurement process
- Supply chain events and disruption scenarios

Similar to main_generate_sales.py, this orchestrates the full process.
"""

import argparse
import sys
import shutil
import os
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.ticker import FuncFormatter
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("📊 Matplotlib not available. Install with: pip install matplotlib")
    print("   Graphing feature will be disabled.")

import json

def load_warehouse_display_names(input_path):
    """Load warehouse display names from warehouses.json configuration."""
    config_file = input_path / "warehouses.json"
    
    if not config_file.exists():
        # Fallback to hardcoded values if config file doesn't exist
        return {
            'Main': 'Kansas City, MO',
            'Backup': 'Memphis, TN', 
            'Regional': 'Atlanta, GA'
        }
        
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Create mapping from WarehouseID to DisplayName
        return {wh['WarehouseID']: wh['DisplayName'] for wh in config['warehouses']}
    except Exception as e:
        print(f"⚠️ Error loading warehouses.json: {e}")
        # Return fallback values
        return {
            'Main': 'Kansas City, MO',
            'Backup': 'Memphis, TN', 
            'Regional': 'Atlanta, GA'
        }

# Import our generators
from generate_suppliers import SupplierDataGenerator
from generate_inventory import InventoryDataGenerator


def generate_warehouses_csv(input_path, output_path, end_date_str):
    """Generate Warehouses.csv from warehouses.json configuration."""
    import pandas as pd
    from datetime import datetime, timedelta
    import random
    
    config_file = input_path / "warehouses.json"
    warehouses_output_dir = output_path / "inventory"
    warehouses_output_dir.mkdir(parents=True, exist_ok=True)
    
    if not config_file.exists():
        print("⚠️ warehouses.json not found, skipping Warehouses.csv generation")
        return False
        
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        warehouses_data = []
        # Use end_date as base for warehouse creation dates
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        # Warehouses created 30-180 days before end of period with some randomization
        created_date_base = end_date - timedelta(days=random.randint(30, 180))
        last_updated_base = end_date - timedelta(days=random.randint(1, 30))
        
        for warehouse in config['warehouses']:
            # Flatten the nested structure for CSV format
            record = {
                'WarehouseID': warehouse['WarehouseID'],
                'WarehouseName': warehouse['WarehouseName'], 
                'DisplayName': warehouse['DisplayName'],
                'Type': warehouse['Type'],
                'Status': warehouse['Status'],
                'Location': warehouse['Location'],
                
                # Address fields
                'AddressStreet': warehouse['Address']['Street'],
                'AddressCity': warehouse['Address']['City'],
                'AddressState': warehouse['Address']['State'], 
                'AddressZipCode': warehouse['Address']['ZipCode'],
                'AddressCountry': warehouse['Address']['Country'],
                
                # Contact fields
                'Phone': warehouse['ContactInfo']['Phone'],
                'Email': warehouse['ContactInfo']['Email'],
                'ManagerName': warehouse['ContactInfo']['Manager'],
                'ManagerEmail': warehouse['ContactInfo']['ManagerEmail'],
                
                # Operational fields
                'Priority': warehouse['Capacity']['Priority'],
                'MaxCapacity': warehouse['Capacity']['MaxCapacity'],
                'OperatingHours': warehouse['Operations']['OperatingHours'],
                'StaffCount': warehouse['Operations']['StaffCount'],
                'AutomationLevel': warehouse['Operations']['AutomationLevel'],
                'DeliveryName': warehouse['DeliveryName'],
                
                # System fields - add small random variance per warehouse
                'CreatedBy': warehouse.get('CreatedBy', 'system'),
                'CreatedDate': (created_date_base + timedelta(hours=random.randint(-24, 24))).strftime('%Y-%m-%d'),
                'LastUpdated': (last_updated_base + timedelta(hours=random.randint(-12, 12))).strftime('%Y-%m-%d')
            }
            warehouses_data.append(record)
            
        # Create DataFrame and save to CSV
        df_warehouses = pd.DataFrame(warehouses_data)
        warehouses_csv_path = warehouses_output_dir / "Warehouses.csv"
        df_warehouses.to_csv(warehouses_csv_path, index=False)
        
        print(f"✅ Generated: Warehouses.csv ({len(warehouses_data)} warehouses)")
        return True
        
    except Exception as e:
        print(f"❌ Error generating Warehouses.csv: {e}")
        return False


def calculate_optimal_parameters(start_date, end_date):
    """Calculate optimal purchase orders and transactions based on existing sales data."""
    
    base_path = Path(__file__).parent
    output_path = base_path / "output"
    
    # Default fallback values
    recommended_orders = 30
    recommended_transactions = 500
    sales_info = "No sales data found"
    
    try:
        # Load sales data from all categories
        total_sales_lines = 0
        total_orders = 0
        categories_found = []
        
        for category in ['camping', 'kitchen', 'ski']:
            sales_path = output_path / "sales" / category
            if sales_path.exists():
                # Count order lines
                orderline_files = list(sales_path.glob("*OrderLine*.csv"))
                order_files = list(sales_path.glob("*Order*.csv"))
                
                for file_path in orderline_files:
                    if file_path.exists():
                        try:
                            df = pd.read_csv(file_path)
                            # Filter by date range if OrderDate column exists
                            if 'OrderDate' in df.columns:
                                df['OrderDate'] = pd.to_datetime(df['OrderDate'])
                                start_dt = pd.to_datetime(start_date)
                                end_dt = pd.to_datetime(end_date)
                                df_filtered = df[(df['OrderDate'] >= start_dt) & (df['OrderDate'] <= end_dt)]
                                total_sales_lines += len(df_filtered)
                            else:
                                total_sales_lines += len(df)
                            categories_found.append(category.title())
                        except Exception as e:
                            print(f"⚠️  Could not read {file_path}: {e}")
                
                for file_path in order_files:
                    if file_path.exists() and 'OrderLine' not in str(file_path) and 'OrderPayment' not in str(file_path):
                        try:
                            df = pd.read_csv(file_path)
                            # Filter by date range if OrderDate column exists
                            if 'OrderDate' in df.columns:
                                df['OrderDate'] = pd.to_datetime(df['OrderDate'])
                                start_dt = pd.to_datetime(start_date)
                                end_dt = pd.to_datetime(end_date)
                                df_filtered = df[(df['OrderDate'] >= start_dt) & (df['OrderDate'] <= end_dt)]
                                total_orders += len(df_filtered)
                            else:
                                total_orders += len(df)
                        except Exception as e:
                            print(f"⚠️  Could not read {file_path}: {e}")
        
        if total_sales_lines > 0:
            # Calculate recommendations based on sales volume
            # Purchase Orders: ~1 PO per 400-500 line items, minimum 20, maximum 200
            recommended_orders = max(20, min(200, int(total_sales_lines / 450)))
            
            # Inventory Transactions: 2-3x sales volume, with reasonable limits
            days_in_range = (datetime.strptime(end_date, '%Y-%m-%d').date() - 
                           datetime.strptime(start_date, '%Y-%m-%d').date()).days
            max_daily_transactions = 15  # Cap at 15 transactions per day
            calculated_transactions = min(total_sales_lines * 2, days_in_range * max_daily_transactions)
            recommended_transactions = max(200, calculated_transactions)
            
            # Sales info summary
            categories_str = ", ".join(set(categories_found))
            sales_info = f"{total_sales_lines:,} line items from {total_orders:,} orders ({categories_str})"
            
        else:
            print("⚠️  No sales data found in output directory. Using default parameters.")
            sales_info = "No sales data found - using defaults"
            
    except Exception as e:
        print(f"⚠️  Error analyzing sales data: {e}")
        sales_info = f"Error reading sales data: {e}"
    
    return recommended_orders, recommended_transactions, sales_info


def generate_summary_report(results, args):
    """Generate a comprehensive summary markdown report."""
    
    # Calculate totals
    total_records = 0
    supplier_totals = {}
    inventory_totals = {}
    
    if 'suppliers' in results:
        supplier_results = results['suppliers']
        supplier_totals = {
            'suppliers': len(supplier_results['suppliers']),
            'product_suppliers': len(supplier_results['product_suppliers']),
            'supply_chain_events': len(supplier_results['supply_chain_events'])
        }
        total_records += sum(supplier_totals.values())
    
    if 'inventory' in results:
        inventory_results = results['inventory']
        inventory_totals = {
            'inventory': len(inventory_results['inventory']),
            'purchase_orders': len(inventory_results['purchase_orders']),
            'purchase_order_items': len(inventory_results['purchase_order_items']),
            'inventory_transactions': len(inventory_results['inventory_transactions']),
            'demand_forecasts': len(inventory_results.get('demand_forecasts', []))
        }
        total_records += sum(inventory_totals.values())
    
    # Load actual supplier data for analysis
    suppliers_info = "Not generated"
    if 'suppliers' in results:
        df_suppliers = results['suppliers']['suppliers']
        primary_count = len(df_suppliers[df_suppliers['SupplierType'] == 'Primary'])
        backup_count = len(df_suppliers[df_suppliers['SupplierType'] == 'Secondary'])
        suppliers_info = f"{primary_count} Primary, {backup_count} Backup"
    
    # Get sales integration info
    sales_integration = "Not analyzed"
    if 'inventory' in results:
        # Try to get sales data count from the generator
        try:
            base_path = Path(__file__).parent
            output_path = base_path / "output"
            
            sales_count = 0
            for category in ['camping', 'kitchen', 'ski']:
                sales_path = output_path / "sales" / category
                if sales_path.exists():
                    orderline_files = list(sales_path.glob("*OrderLine*.csv"))
                    for file_path in orderline_files:
                        if file_path.exists():
                            try:
                                df = pd.read_csv(file_path)
                                sales_count += len(df)
                            except:
                                pass
            
            if sales_count > 0:
                sales_integration = f"Connected to {sales_count:,} sales line items"
        except:
            sales_integration = "Sales data processed"
    
    # Generate the summary content
    duration_days = (datetime.strptime(args.end_date, '%Y-%m-%d').date() - 
                    datetime.strptime(args.start_date, '%Y-%m-%d').date()).days
    
    summary_content = f"""# Supply Chain Data Generation Summary

**Date Range**: {args.start_date} to {args.end_date}  
**Duration**: {duration_days} days  
**Integration**: {sales_integration}

## 🏭 Generation Overview

### **Total Summary**
- **Total Records Generated**: {total_records:,}
- **Suppliers**: {supplier_totals.get('suppliers', 0)} suppliers with backup relationships
- **Product-Supplier Mappings**: {supplier_totals.get('product_suppliers', 0)} relationships
- **Inventory Records**: {inventory_totals.get('inventory', 0)} stock locations
- **Purchase Orders**: {inventory_totals.get('purchase_orders', 0)} procurement orders  
- **PO Line Items**: {inventory_totals.get('purchase_order_items', 0)} order details
- **Inventory Transactions**: {inventory_totals.get('inventory_transactions', 0)} movement records
- **Demand Forecasts**: {inventory_totals.get('demand_forecasts', 0)} predictive analytics records
- **Supply Chain Events**: {supplier_totals.get('supply_chain_events', 0)} disruption scenarios

### **Supplier Network**

| Supplier Type | Configuration | Lead Time Strategy |
|---------------|---------------|-------------------|
| 🏢 Primary | Category-specific suppliers | 7-21 days (optimized) |  
| 🔄 Backup | Multi-category coverage | 14-35 days (resilience) |

### **Domain Coverage**

| Product Category | Primary Supplier | Backup Coverage | Integration Status |
|------------------|------------------|-----------------|-------------------|
| 🏕️ Camping | Contoso Camping Equipment | Worldwide Importers | ✅ Connected |
| 🍳 Kitchen | Contoso Kitchen | Worldwide Importers | ✅ Connected |  
| ⛷️ Ski | Contoso Ski Equipment | Worldwide + Fabrikam | ✅ Connected |

## 📦 Inventory Intelligence

### **Stock Management Ready**
- **Sales-Driven Levels**: Real sales transaction analysis for realistic inventory
- **Safety Stock Calculations**: 2-4 weeks average demand coverage  
- **Reorder Points**: Automatic replenishment triggers configured
- **Multi-Warehouse**: Main, Backup, and Regional distribution centers
- **Real-Time Status**: Active, LowStock, OutOfStock, Excess classifications

### **Procurement Operations**
- **Purchase Orders**: {inventory_totals.get('purchase_orders', 0)} orders spanning 90-day historical period
- **Supplier Integration**: Direct mapping to product catalog and lead times
- **Order Status Tracking**: Draft → Sent → Confirmed → InTransit → Delivered
- **Cost Management**: Wholesale pricing 60-80% of retail with supplier variations

### **Transaction Audit Trail**  
- **Complete Visibility**: {inventory_totals.get('inventory_transactions', 0)} inventory movements across all transaction types
- **Receipt Tracking**: Purchase order receipts with reference numbers
- **Sales Integration**: Outbound movements linked to customer orders
- **Adjustments**: Cycle counts, transfers, damages, returns all tracked
- **Financial Impact**: Unit costs and total values for all movements

## 🚨 Supply Chain Risk Management

### **Disruption Modeling**
- **Event Types**: Weather, Political, Economic, Pandemic, Transport, Supplier
- **Geographic Coverage**: Local, Regional, National, Global impact zones  
- **Severity Levels**: Low → Medium → High → Critical classifications
- **Status Tracking**: Active → Monitoring → Resolved workflow
- **Impact Assessment**: Supplier downtime, delays, cost increases, availability

### **Recovery Planning**
- **Multi-Tier Suppliers**: {suppliers_info} supplier relationships
- **Lead Time Buffers**: Variable delivery windows with reliability scoring
- **Emergency Orders**: Priority processing for critical stock situations
- **Mitigation Actions**: Alternative sourcing, expedited shipping, transfers

## 🎯 Key Business Benefits

### **Analytical Capabilities**
- **Demand Forecasting**: Sales velocity analysis drives inventory planning
- **Supplier Performance**: Lead time tracking and reliability scoring  
- **Cost Optimization**: Wholesale vs retail margin analysis across suppliers
- **Risk Assessment**: Supply chain vulnerability identification and mitigation

### **Operational Excellence**  
- **Inventory Optimization**: Right-sized stock levels based on actual demand
- **Procurement Efficiency**: Automated reorder triggers and supplier selection
- **Financial Control**: Complete cost tracking from wholesale to retail
- **Compliance Ready**: Full audit trail for inventory movements and relationships

### **Data Integration**
- **Customer→Sales→Inventory**: Complete order fulfillment visibility
- **Supplier→Purchase→Receipt**: End-to-end procurement lifecycle  
- **Product→Category→Supplier**: Comprehensive product sourcing intelligence
- **Finance→Cost→Margin**: Complete financial supply chain analysis

## 📋 Generated Files

### **Supplier Data** (`output/suppliers/`)
- `Suppliers.csv` - {supplier_totals.get('suppliers', 0)} supplier records with backup relationships
- `ProductSuppliers.csv` - {supplier_totals.get('product_suppliers', 0)} product-to-supplier mappings with pricing
- `SupplyChainEvents.csv` - {supplier_totals.get('supply_chain_events', 0)} disruption events and scenarios

### **Inventory Data** (`output/inventory/`)  
- `Inventory.csv` - {inventory_totals.get('inventory', 0)} current stock levels across warehouses
- `InventoryTransactions.csv` - {inventory_totals.get('inventory_transactions', 0)} complete movement audit trail
- `PurchaseOrders.csv` - {inventory_totals.get('purchase_orders', 0)} procurement orders with supplier details  
- `PurchaseOrderItems.csv` - {inventory_totals.get('purchase_order_items', 0)} line items with specifications
- `DemandForecast.csv` - {inventory_totals.get('demand_forecasts', 0)} predictive analytics with seasonal patterns

## 🚀 Next Steps

### **Microsoft Fabric Integration**
1. **Schema Creation**: Execute `model_suppliers.ipynb` and `model_inventory.ipynb`
2. **Data Loading**: Import CSV files using Files → Tables pattern  
3. **Analytics Setup**: Connect Power BI for supply chain dashboards

### **Advanced Analytics Opportunities**
- **Inventory Optimization**: ABC analysis and demand forecasting models
- **Supplier Scorecarding**: Performance metrics and vendor management  
- **Risk Analytics**: Supply chain vulnerability mapping and scenario planning
- **Cost Management**: Margin analysis and procurement savings opportunities

---

*Generated by Supply Chain Data Generator v1.0*  
*Generation Parameters: {args.num_orders} orders, {args.num_transactions} transactions, {args.num_events} events*  
*Integration Status: ✅ Sales Data Connected*  
*Business Realism: ✅ Demand-Driven Inventory*  
*Ready for Analytics: ✅ Full Schema Support*"""

    # Write the summary file
    base_path = Path(__file__).parent
    output_path = base_path / "output"
    summary_file = output_path / "sample_supplychain_data_summary.md"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"\n📋 Summary report generated: {summary_file}")
    return summary_file


def print_banner():
    """Print startup banner."""
    print("=" * 70)
    print("🏭 SUPPLY CHAIN DATA GENERATOR")
    print("=" * 70)
    print("Generating comprehensive supply chain datasets for eCommerce business")
    print("Integrates with existing sales data for realistic inventory patterns")
    print()


def print_summary(results):
    """Print generation summary."""
    print("\n" + "=" * 70)
    print("📊 SUPPLY CHAIN GENERATION SUMMARY")
    print("=" * 70)
    
    # Supplier data
    if 'suppliers' in results:
        supplier_results = results['suppliers']
        print("\n🏭 SUPPLIER DATA:")
        print(f"   • Suppliers: {len(supplier_results['suppliers'])} records")
        print(f"   • Product-Supplier Mappings: {len(supplier_results['product_suppliers'])} records")
        print(f"   • Supply Chain Events: {len(supplier_results['supply_chain_events'])} records")
    
    # Inventory data  
    if 'inventory' in results:
        inventory_results = results['inventory']
        print("\n📦 INVENTORY DATA:")
        print(f"   • Inventory Records: {len(inventory_results['inventory'])} records")
        print(f"   • Purchase Orders: {len(inventory_results['purchase_orders'])} records")
        print(f"   • Purchase Order Items: {len(inventory_results['purchase_order_items'])} records")
        print(f"   • Inventory Transactions: {len(inventory_results['inventory_transactions'])} records")
    
    print("\n💾 OUTPUT LOCATIONS:")
    print(f"   • Supplier Data: output/suppliers/")
    print(f"   • Inventory Data: output/inventory/")
    
    print("\n🎯 NEXT STEPS:")
    print("   1. Review generated CSV files")
    print("   2. Load data into Microsoft Fabric using schema notebooks")
    print("   3. Run analytics on complete supply chain dataset")
    print("\n" + "=" * 70)


def generate_graph(results, args):
    """Generate intuitive supply chain analytics dashboard with business-focused insights"""
    if not MATPLOTLIB_AVAILABLE:
        print("⚠️  Graphing skipped - matplotlib not available. Install with: pip install matplotlib")
        return
    
    print("📊 Generating intuitive supply chain analytics dashboard...")
    
    base_path = Path(__file__).parent
    output_path = base_path / "output"
    
    try:
        # Load data for graphing
        inventory_path = output_path / "inventory"
        suppliers_path = output_path / "supplychain"
        
        # Check if data exists
        if not inventory_path.exists() or not suppliers_path.exists():
            print("⚠️  No supply chain data found for graphing. Generate data first.")
            return
        
        # Create subplot layout (2x3 grid) with 5 tiles + 1 empty
        fig, axes = plt.subplots(2, 3, figsize=(24, 14))
        ax1, ax2, ax3 = axes[0, 0], axes[0, 1], axes[0, 2]
        ax4, ax5, ax6 = axes[1, 0], axes[1, 1], axes[1, 2]
        fig.suptitle(f'Supply Chain Business Dashboard\n{args.start_date} to {args.end_date}', 
                     fontsize=18, fontweight='bold', y=0.96)
        
        # Tile 1: Recent Sales (Last 6 Months)
        _create_recent_sales_chart(ax1, output_path, args)
        
        # Tile 2: Demand Forecast (Next 3 Months) 
        _create_demand_forecast_chart(ax2, inventory_path)
        
        # Tile 6: Empty (reserved for future expansion)
        ax6.text(0.5, 0.5, 'Reserved for\nFuture Analytics', ha='center', va='center', 
                transform=ax6.transAxes, fontsize=14, style='italic', alpha=0.5)
        ax6.set_title('Future Expansion', fontsize=14, fontweight='bold', pad=20)
        ax6.axis('off')  # Clean empty tile
        
# Tile 3: Warehouse Capacity Utilization (Business Critical)
        inventory_levels_file = inventory_path / "Inventory.csv"
        if inventory_levels_file.exists():
            df_inventory = pd.read_csv(inventory_levels_file)
            
            # Load warehouse configuration for display names
            warehouse_display_names = load_warehouse_display_names(Path(__file__).parent / "input")
            
            # Calculate capacity utilization by warehouse
            warehouse_stats = df_inventory.groupby('WarehouseLocation').agg({
                'CurrentStock': 'sum',
                'MaxStockLevel': 'sum',
                'ReorderPoint': 'sum',
                'SafetyStockLevel': 'sum'
            }).round(0)
            
            # Calculate utilization percentage
            warehouse_stats['Utilization'] = (warehouse_stats['CurrentStock'] / warehouse_stats['MaxStockLevel'] * 100).round(1)
            
            # Convert warehouse names to display names for chart
            display_locations = [warehouse_display_names.get(loc, loc) for loc in warehouse_stats.index.tolist()]
            utilizations = warehouse_stats['Utilization'].tolist()
            
            # Color code by utilization level (Red: >90%, Yellow: 70-90%, Green: <70%)
            colors = ['#DC143C' if u > 90 else '#FFD700' if u > 70 else '#32CD32' for u in utilizations]
            
            bars = ax3.barh(display_locations, utilizations, color=colors, alpha=0.8, height=0.6)
            
            # Add percentage labels on bars
            for i, (bar, util) in enumerate(zip(bars, utilizations)):
                ax3.text(util + 2, i, f'{util:.1f}%', va='center', fontweight='bold', fontsize=12)
            
            # Add capacity zones
            ax3.axvline(x=70, color='orange', linestyle='--', alpha=0.7, linewidth=2, label='High Utilization')
            ax3.axvline(x=90, color='red', linestyle='--', alpha=0.7, linewidth=2, label='Critical Capacity')
            
            ax3.set_title('Warehouse Capacity Utilization', fontsize=14, fontweight='bold', pad=20)
            ax3.set_xlabel('Capacity Utilization (%)', fontsize=12)
            ax3.set_xlim(0, 105)
            ax3.legend(loc='lower right', fontsize=10)
            ax3.grid(True, alpha=0.2, axis='x')
        
        # Graph 3: Stock Health by Category (Actionable Insights)
        if inventory_levels_file.exists():
            # Create stock health analysis
            df_inventory['StockHealth'] = 'Unknown'
            df_inventory.loc[df_inventory['CurrentStock'] == 0, 'StockHealth'] = 'Out of Stock'
            df_inventory.loc[
                (df_inventory['CurrentStock'] > 0) & 
                (df_inventory['CurrentStock'] <= df_inventory['SafetyStockLevel']), 
                'StockHealth'
            ] = '⚠️  Low Stock'
            df_inventory.loc[
                (df_inventory['CurrentStock'] > df_inventory['SafetyStockLevel']) & 
                (df_inventory['CurrentStock'] <= df_inventory['ReorderPoint']), 
                'StockHealth'
            ] = 'Reorder Soon'
            df_inventory.loc[
                (df_inventory['CurrentStock'] > df_inventory['ReorderPoint']) & 
                (df_inventory['CurrentStock'] < df_inventory['MaxStockLevel'] * 0.9), 
                'StockHealth'
            ] = 'Healthy Stock'
            df_inventory.loc[
                df_inventory['CurrentStock'] >= df_inventory['MaxStockLevel'] * 0.9, 
                'StockHealth'
            ] = 'High Stock'
            
            # Count products by health status
            health_counts = df_inventory['StockHealth'].value_counts()
            
            # Define colors for each health status
            health_colors = {
                'Out of Stock': '#DC143C',
                '⚠️  Low Stock': '#FF8C00', 
                'Reorder Soon': '#FFD700',
                'Healthy Stock': '#32CD32',
                'High Stock': '#4169E1'
            }
            
            colors = [health_colors.get(status, '#808080') for status in health_counts.index]
            
            # Create horizontal bar chart for better readability
            bars = ax4.barh(range(len(health_counts)), health_counts.values, color=colors, alpha=0.8)
            
            # Add count labels
            for i, (bar, count) in enumerate(zip(bars, health_counts.values)):
                ax4.text(count + max(health_counts.values) * 0.01, i, f'{count}', 
                        va='center', fontweight='bold', fontsize=12)
            
            ax4.set_yticks(range(len(health_counts)))
            ax4.set_yticklabels(health_counts.index, fontsize=11)
            ax4.set_title('Inventory Health Status', fontsize=14, fontweight='bold', pad=20)
            ax4.set_xlabel('Number of Products', fontsize=12)
            ax4.grid(True, alpha=0.2, axis='x')
        
        # Graph 4: Supplier Performance Matrix (Simplified for POC)
        suppliers_file = suppliers_path / "Suppliers.csv"
        if suppliers_file.exists():
            df_suppliers = pd.read_csv(suppliers_file)
            
            # Filter suppliers with reliability >= 80 for POC
            df_suppliers_filtered = df_suppliers[df_suppliers['ReliabilityScore'] >= 80]
            
            if len(df_suppliers_filtered) > 0:
                # Create meaningful supplier analysis
                def clean_supplier_name(name):
                    if 'Contoso' in name:
                        clean_name = name.replace(' Equipment', '').replace(' Ltd', '').replace(' Co.', '')
                        parts = clean_name.strip().split()
                        return ' '.join(parts[:2])  # "Contoso Camping", "Contoso Kitchen", etc.
                    else:
                        return ' '.join(name.split()[:2])
                
                df_suppliers_filtered['CleanName'] = df_suppliers_filtered['SupplierName'].apply(clean_supplier_name)
                
                # Calculate supplier risk (inverse of reliability, scaled by lead time)
                df_suppliers_filtered['RiskScore'] = (100 - df_suppliers_filtered['ReliabilityScore']) + (df_suppliers_filtered['LeadTimeDays'] / 2)
                
                # Create performance matrix without quadrant labels
                risk_scores = df_suppliers_filtered['RiskScore']
                reliability_scores = df_suppliers_filtered['ReliabilityScore']
                
                # Color by supplier type and size by lead time impact
                colors = ['red' if x == 'Secondary' else 'blue' for x in df_suppliers_filtered['SupplierType']]
                sizes = [max(50, 200 - lt*3) for lt in df_suppliers_filtered['LeadTimeDays']]  # Larger dot = faster delivery
                
                scatter = ax5.scatter(risk_scores, reliability_scores, c=colors, s=sizes, alpha=0.7, edgecolors='black')
                
                # Add supplier name labels (simple and clean)
                for i, row in df_suppliers_filtered.iterrows():
                    ax5.annotate(row['CleanName'], (row['RiskScore'], row['ReliabilityScore']), 
                               xytext=(5, 5), textcoords='offset points', fontsize=10,
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='gray'))
                
                ax5.set_xlabel('Risk Score (Lower is Better)', fontsize=12)
                ax5.set_ylabel('Reliability Score (Higher is Better)', fontsize=12)
                ax5.set_title('Supplier Performance Matrix', fontsize=14, fontweight='bold', pad=20)
                
                # Simple legend - just Primary vs Backup
                from matplotlib.patches import Patch
                legend_elements = [
                    Patch(facecolor='blue', label='Primary Supplier'),
                    Patch(facecolor='red', label='Secondary Supplier')
                ]
                ax5.legend(handles=legend_elements, loc='lower left', fontsize=10)
                ax5.grid(True, alpha=0.2)
            else:
                ax5.text(0.5, 0.5, 'No suppliers meet\nreliability criteria (≥80%)', 
                        ha='center', va='center', transform=ax5.transAxes, fontsize=14)
                ax5.set_title('Supplier Performance Matrix', fontsize=14, fontweight='bold', pad=20)
            ax5.grid(True, alpha=0.2)
        
        # Add overall business insights text box
        fig.text(0.02, 0.02, 
                'Business Insights: Monitor red zones for immediate action. '
                'Strategic suppliers (top-left) should handle 70%+ of volume. '
                'High utilization warehouses need expansion planning.',
                fontsize=10, style='italic', 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.3))
        
        plt.tight_layout(rect=[0, 0.05, 1, 0.94])  # Leave space for suptitle and insights
        
        # Save the graph
        graph_file = output_path / "supply_chain_data.png"
        plt.savefig(graph_file, dpi=150, bbox_inches='tight', facecolor='white')
        
        # Generate comprehensive business summary statistics  
        print(f"✅ Professional supply chain dashboard saved: {graph_file}")
        print(f"📊 Business Analytics Summary:")
        
        # Enhanced transaction analysis with timeline coverage
        inventory_transactions_file = inventory_path / "InventoryTransactions.csv"
        if inventory_transactions_file.exists():
            df_transactions = pd.read_csv(inventory_transactions_file)
            df_transactions['TransactionDate'] = pd.to_datetime(df_transactions['TransactionDate'])
            
            total_transactions = len(df_transactions)
            total_quantity_moved = df_transactions['Quantity'].abs().sum()
            date_range_days = (df_transactions['TransactionDate'].max() - df_transactions['TransactionDate'].min()).days
            daily_avg_transactions = total_transactions / max(date_range_days, 1)
            
            # Calculate flow balance
            inflow_total = df_transactions[df_transactions['Quantity'] > 0]['Quantity'].sum()
            outflow_total = abs(df_transactions[df_transactions['Quantity'] < 0]['Quantity'].sum())
            net_flow = inflow_total - outflow_total
            
            print(f"   📈 Total Inventory Transactions: {total_transactions:,} over {date_range_days} days")
            print(f"   🔄 Daily Transaction Average: {daily_avg_transactions:.1f} transactions")
            print(f"   📦 Total Inflow: {inflow_total:,} units | Outflow: {outflow_total:,} units")
            print(f"   💰 Net Inventory Change: {net_flow:+,} units ({'Growth' if net_flow > 0 else 'Reduction'})")
        
        # Purchase order insights
        purchase_orders_file = inventory_path / "PurchaseOrders.csv"
        if purchase_orders_file.exists():
            df_orders = pd.read_csv(purchase_orders_file)
            total_orders = len(df_orders)
            avg_order_value = df_orders['TotalOrderValue'].mean() if 'TotalOrderValue' in df_orders.columns else 0
            total_procurement_value = df_orders['TotalOrderValue'].sum() if 'TotalOrderValue' in df_orders.columns else 0
            
            print(f"   📝 Purchase Orders: {total_orders} totaling ${total_procurement_value:,.2f}")
            print(f"   💵 Average Order Value: ${avg_order_value:,.2f}")
        
        # Warehouse utilization insights
        if inventory_levels_file.exists():
            total_stock = df_inventory['CurrentStock'].sum()
            total_capacity = df_inventory['MaxStockLevel'].sum()
            overall_utilization = (total_stock / total_capacity * 100) if total_capacity > 0 else 0
            
            out_of_stock = df_inventory[df_inventory['Status'] == 'OutOfStock']
            low_stock = df_inventory[df_inventory['Status'] == 'LowStock'] 
            critical_items = len(out_of_stock) + len(low_stock)
            healthy_items = len(df_inventory[df_inventory['Status'] == 'Active'])
            
            print(f"   🏭 Overall Capacity Utilization: {overall_utilization:.1f}%")
            print(f"   ⚠️  Items Needing Attention: {critical_items} | ✅ Healthy Items: {healthy_items}")
        
        # Supplier performance insights (filtered for POC)
        if suppliers_file.exists():
            df_suppliers = pd.read_csv(suppliers_file)
            
            # Filter suppliers with reliability >= 80 for POC
            df_suppliers_filtered = df_suppliers[df_suppliers['ReliabilityScore'] >= 80]
            
            if len(df_suppliers_filtered) > 0:
                avg_reliability = df_suppliers_filtered['ReliabilityScore'].mean()
                avg_lead_time = df_suppliers_filtered['LeadTimeDays'].mean()
                
                # Recalculate for filtered suppliers
                df_suppliers_filtered['RiskScore'] = (100 - df_suppliers_filtered['ReliabilityScore']) + (df_suppliers_filtered['LeadTimeDays'] / 2)
                reliability_mid = df_suppliers_filtered['ReliabilityScore'].median()
                risk_mid = df_suppliers_filtered['RiskScore'].median()
                
                strategic_suppliers = len(df_suppliers_filtered[
                    (df_suppliers_filtered['ReliabilityScore'] > reliability_mid) & 
                    (df_suppliers_filtered['RiskScore'] < risk_mid)
                ])
                
                print(f"   🎯 Supplier Performance: {avg_reliability:.1f}% avg reliability, {avg_lead_time:.1f} days avg lead time")
                print(f"   ⭐ Quality Suppliers (≥80% reliability): {len(df_suppliers_filtered)} of {len(df_suppliers)} total")
            else:
                print(f"   ⚠️  No suppliers meet reliability threshold (≥80%)")
        
        print(f"\n🚀 Dashboard shows {date_range_days}-day business timeline with actionable insights!")
        
        # Display the graph (only if not running in automation mode)
        if not args.no_display:
            plt.show()
        
    except Exception as e:
        print(f"❌ Error generating supply chain dashboard: {e}")
        print("   Make sure matplotlib and pandas are installed: pip install matplotlib pandas")


def copy_data_to_dest_path(output_dest_path):
    """Copy generated supply chain data files to the specified destination directory with proper folder structure."""
    
    print("\n📁 Copying data files to output directory...")
    
    # Define source and destination paths
    current_dir = Path(__file__).parent
    output_dir = current_dir / "output"
    infra_dir = Path(output_dest_path).resolve()
    
    try:
        # Create destination directory if it doesn't exist
        infra_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy suppliers files to supplychain subfolder
        suppliers_src = output_dir / "supplychain"
        suppliers_dest = infra_dir / "supplychain"
        if suppliers_src.exists():
            suppliers_dest.mkdir(exist_ok=True)
            for file_path in suppliers_src.glob("*.csv"):
                dest_file = suppliers_dest / file_path.name
                shutil.copy2(file_path, dest_file)
                print(f"✅ Copied: {file_path.name} → supplychain/")
        
        # Copy inventory files to inventory subfolder
        inventory_src = output_dir / "inventory" 
        inventory_dest = infra_dir / "inventory"
        if inventory_src.exists():
            inventory_dest.mkdir(exist_ok=True)
            for file_path in inventory_src.glob("*.csv"):
                dest_file = inventory_dest / file_path.name
                shutil.copy2(file_path, dest_file)
                print(f"✅ Copied: {file_path.name} → inventory/")
        
        # Copy summary file to infra/data root
        summary_src = output_dir / "sample_supplychain_data_summary.md"
        if summary_src.exists():
            summary_dest = infra_dir / "sample_supplychain_data_summary.md"
            shutil.copy2(summary_src, summary_dest)
            print(f"✅ Copied: sample_supplychain_data_summary.md → data/")
        
        print(f"📁 All files organized in: {infra_dir}")
        
    except Exception as e:
        print(f"❌ Error copying files: {e}")
        print("   Make sure the destination directory is accessible")


def _create_recent_sales_chart(ax, output_path, args):
    """Create a simple recent sales trend chart (last 6 months)"""
    all_sales = []
    
    for category in ['camping', 'kitchen', 'ski']:
        try:
            orders_file = output_path / "sales" / category / f"Order_Samples_{category.capitalize()}.csv"
            order_lines_file = output_path / "sales" / category / f"OrderLine_Samples_{category.capitalize()}.csv"
            
            if orders_file.exists() and order_lines_file.exists():
                df_orders = pd.read_csv(orders_file)
                df_order_lines = pd.read_csv(order_lines_file)
                
                if 'OrderID' in df_orders.columns and 'OrderDate' in df_orders.columns:
                    df_sales = pd.merge(df_orders[['OrderID', 'OrderDate']], 
                                      df_order_lines[['OrderID', 'Quantity']], 
                                      on='OrderID', how='inner')
                    if len(df_sales) > 0:
                        df_sales['OrderDate'] = pd.to_datetime(df_sales['OrderDate'])
                        all_sales.append(df_sales)
        except Exception:
            continue
    
    if all_sales:
        combined_sales = pd.concat(all_sales, ignore_index=True)
        
        # Calculate trend start (last 6 months) but ensure we start from beginning of a complete month
        raw_trend_start = pd.Timestamp(args.end_date) - pd.DateOffset(months=6)
        
        # Ensure we don't go before the actual start date
        bounded_trend_start = max(pd.Timestamp(args.start_date), raw_trend_start)
        
        # Round to the beginning of the month to avoid partial month bias
        trend_start = bounded_trend_start.replace(day=1)
        
        # If rounding creates a date before our data period, use the actual start date
        if trend_start < pd.Timestamp(args.start_date):
            trend_start = pd.Timestamp(args.start_date)
        
        print(f"📊 Recent Sales Trend period: {trend_start.strftime('%Y-%m-%d')} to {args.end_date}")
        
        sales_period = combined_sales[
            (combined_sales['OrderDate'] >= trend_start) & 
            (combined_sales['OrderDate'] <= pd.Timestamp(args.end_date))
        ].copy()
        
        sales_period['Month'] = sales_period['OrderDate'].dt.to_period('M')
        monthly_sales = sales_period.groupby('Month')['Quantity'].sum()
        
        months = list(monthly_sales.index)
        values = list(monthly_sales.values)
        
        # Simple trend line - no special handling, all dates are equal
        ax.plot(range(len(months)), values, color='#2E8B57', linewidth=3, marker='o', markersize=6)
        ax.fill_between(range(len(months)), 0, values, color='#2E8B57', alpha=0.3)
        
        ax.set_title('Recent Sales Trend', fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Units Sold', fontsize=12)
        ax.set_xlabel('Month', fontsize=12)
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels([m.end_time.strftime('%Y-%m') for m in months], rotation=45)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
        ax.grid(True, alpha=0.2)
    else:
        ax.text(0.5, 0.5, 'No sales data available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Recent Sales Trend (No Data)', fontsize=14, fontweight='bold')


def _create_demand_forecast_chart(ax, inventory_path):
    """Create a simple demand forecast chart (next 3 months)"""
    demand_forecast_file = inventory_path / "DemandForecast.csv"
    
    if demand_forecast_file.exists():
        try:
            df_forecast = pd.read_csv(demand_forecast_file)
            df_forecast['ForecastDate'] = pd.to_datetime(df_forecast['ForecastDate'])
            df_forecast['Month'] = df_forecast['ForecastDate'].dt.to_period('M')
            
            # Filter to monthly forecasts only
            monthly_forecasts = df_forecast[df_forecast['ForecastPeriod'] == 'Monthly'].copy()
            forecast_by_month = monthly_forecasts.groupby('Month')['PredictedDemand'].sum()
            
            months = list(forecast_by_month.index)[:3]  # Next 3 months
            values = [forecast_by_month.get(m, 0) for m in months]
            
            # Simple forecast line
            ax.plot(range(len(months)), values, color='#4169E1', linewidth=3, marker='s', markersize=6)
            ax.fill_between(range(len(months)), 0, values, color='#4169E1', alpha=0.3)
            
            ax.set_title('Demand Forecast', fontsize=14, fontweight='bold', pad=20)
            ax.set_ylabel('Predicted Demand', fontsize=12)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels([m.end_time.strftime('%Y-%m') for m in months], rotation=45)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
            ax.grid(True, alpha=0.2)
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Forecast error: {str(e)}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Demand Forecast (Error)', fontsize=14, fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'Forecast data not available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Demand Forecast (No Data)', fontsize=14, fontweight='bold')


def main():
    """Main function to orchestrate supply chain data generation."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Generate comprehensive supply chain data for eCommerce business',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_generate_supplychain.py -s 2025-01-01 -e 2026-04-30
  python main_generate_supplychain.py -s 2025-01-01 -e 2026-03-02 --inventory-only --num-orders 50
  python main_generate_supplychain.py -s 2025-01-01 -e 2026-04-30 --auto-scale  # Auto-calculate based on sales data
  python main_generate_supplychain.py -s 2025-01-01 -e 2026-04-30 --auto-scale --graph
  python main_generate_supplychain.py -s 2025-01-01 -e 2026-04-30 --graph --num-orders 25 --num-transactions 800
        """
    )
    
    parser.add_argument(
        '-s', '--start-date',
        type=str,
        required=True,
        help='Start date for analysis (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '-e', '--end-date', 
        type=str,
        required=True,
        help='End date for analysis (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--inventory-only',
        action='store_true',
        help='Generate only inventory data (requires existing supplier data)'
    )
    
    parser.add_argument(
        '--num-orders',
        type=int,
        default=30,
        help='Number of purchase orders to generate (default: 30)'
    )
    
    parser.add_argument(
        '--num-transactions',
        type=int, 
        default=500,  # Increased default for better timeline coverage
        help='Number of inventory transactions to generate (default: 500, auto-scales with timeline)'
    )
    
    parser.add_argument(
        '--num-events',
        type=int,
        default=15, 
        help='Number of supply chain events to generate (default: 15)'
    )
    
    parser.add_argument(
        '--graph',
        action='store_true',
        help='Generate supply chain analytics graph (requires matplotlib: pip install matplotlib)'
    )
    
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Save graphs without displaying (for automation)'
    )
    
    parser.add_argument(
        '--auto-scale',
        action='store_true',
        help='Auto-calculate optimal purchase orders and transactions based on existing sales data'
    )
    
    parser.add_argument(
        '--copydata',
        type=str,
        metavar='OUTPUT_DIR',
        help='Copy generated data files to the specified output directory'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Auto-scale parameters if requested
    if args.auto_scale:
        print("🚀 Auto-scaling enabled - analyzing existing sales data...")
        print("-" * 60)
        
        calculated_orders, calculated_transactions, sales_summary = calculate_optimal_parameters(
            args.start_date, args.end_date
        )
        
        print(f"📈 Sales Analysis: {sales_summary}")
        print(f"📊 Calculated Parameters:")
        print(f"   • Purchase Orders: {calculated_orders} (was {args.num_orders})")
        print(f"   • Inventory Transactions: {calculated_transactions:,} (was {args.num_transactions})")
        
        # Use calculated values
        args.num_orders = calculated_orders
        args.num_transactions = calculated_transactions
        
        print("✅ Using auto-calculated parameters\n")
    else:
        print(f"📄 Using manual parameters: {args.num_orders} orders, {args.num_transactions} transactions\n")
    
    try:
        results = {}
        
        # Phase 1: Supplier Data Generation
        if not args.inventory_only:
            print("🏭 Phase 1: Generating Supplier Foundation...")
            print("-" * 50)
            
            supplier_generator = SupplierDataGenerator()
            supplier_results = supplier_generator.generate_all_supplier_data(
                start_date=datetime.strptime(args.start_date, '%Y-%m-%d'),
                end_date=datetime.strptime(args.end_date, '%Y-%m-%d'),
                num_events=args.num_events
            )
            results['suppliers'] = supplier_results
            
            print("✅ Phase 1 completed successfully!")
        
        # Phase 2: Inventory Data Generation
        print("\n📦 Phase 2: Generating Inventory Intelligence...")
        print("-" * 50)
        
        # First, generate warehouse master data from configuration
        current_dir = Path(__file__).parent
        input_dir = current_dir / "input"
        output_dir = current_dir / "output"
        
        print("🏭 Generating warehouse master data...")
        warehouse_success = generate_warehouses_csv(input_dir, output_dir, args.end_date)
        if warehouse_success:
            print("   └─ Warehouse configuration loaded and CSV generated")
        
        inventory_generator = InventoryDataGenerator(
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        inventory_results = inventory_generator.generate_all_inventory_data(
            num_orders=args.num_orders,
            num_transactions=args.num_transactions
        )
        results['inventory'] = inventory_results
        
        print("✅ Phase 2 completed successfully!")
        
        # Generate summary report
        summary_file = generate_summary_report(results, args)
        
        # Generate analytics graph if requested
        if args.graph:
            generate_graph(results, args)
        
        # Copy data files if requested
        if args.copydata:
            copy_data_to_dest_path(args.copydata)
        
        # Print final summary
        print_summary(results)
        
        print("🎉 Supply chain data generation completed successfully!")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        print("Make sure you have:")
        print("   • suppliers.json in input/ directory")
        print("   • warehouses.json in input/ directory")
        print("   • Product sample files in input/ directory") 
        print("   • Generated sales data (for inventory analysis)")
        return 1
        
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        print("\nFor help, run: python main_generate_supplychain.py --help")
        return 1


if __name__ == "__main__":
    sys.exit(main())