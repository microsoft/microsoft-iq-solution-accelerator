#!/usr/bin/env python3
"""
Sample Data Generation Orchestrator
===================================

Generates realistic sales and finance data for three product categories:
🏕️  Camping → Microsoft Fabric channel → camping/
🍳 Kitchen → Azure Databricks channel → kitchen/  
⛷️  Ski → Winter Sports channel → ski/

Each generates: Orders, OrderLines, OrderPayments, Invoices, Payments, Accounts

Usage:
  python main_generate_sales.py                                    # Default: 1 year of data, all domains
  python main_generate_sales.py -s 2025-01-01 -e 2025-12-31      # Custom date range, all domains
  python main_generate_sales.py --start-date 2024-01-01 --camping-only  # Camping domain only
  python main_generate_sales.py --help                            # Show all options

Author: GitHub Copilot
Date: January 14, 2026
"""

import sys
import argparse
import shutil
import glob
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.ticker import FuncFormatter
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("📊 Matplotlib not available. Install with: pip install matplotlib")
    print("   Graphing feature will be disabled.")

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import the generator functions
from generate_camping_orders import generate_camping_orders
from generate_kitchen_orders import generate_kitchen_orders  
from generate_ski_orders import generate_ski_orders

def parse_date(date_string):
    """Parse date string in various formats"""
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y%m%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_string}. Use format YYYY-MM-DD")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate Sample Data for All Product Categories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Examples (using short options):
  python main_generate_sales.py                           # All data, full date range
  python main_generate_sales.py -s 2024-01-01             # All data from 2024
  python main_generate_sales.py -s 2025-01-01 -e 2025-12-31  # All data for 2025
  python main_generate_sales.py -s 2024-06-01 -e 2024-06-30 --camping-only
  python main_generate_sales.py --enable-growth            # Enable business growth patterns
  python main_generate_sales.py --graph                    # Generate revenue trend graph
  python main_generate_sales.py --enable-growth --graph    # Growth patterns with visualization

Generates data for three channels:
  🏕️  Camping   → camping/     (Microsoft Fabric)
  🍳 Kitchen   → kitchen/      (Azure Databricks) 
  ⛷️  Ski       → ski/         (Winter Sports)
  
Business Growth Features (--enable-growth):
  • Three-phase continuous growth pattern (Growth → Sustained → Explosive)
  • Market events (Black Friday, Christmas, Memorial Day)
  • Customer tier amplification (VIP customers respond more to trends)
  • Enhanced for Camping & Kitchen domains (Ski remains baseline)
        """
    )
    
    parser.add_argument(
        '-s', '--start-date',
        type=str,
        required=True,
        help='Start date (YYYY-MM-DD). Required.'
    )
    
    parser.add_argument(
        '-e', '--end-date', 
        type=str,
        required=True,
        help='End date (YYYY-MM-DD). Required.'
    )
    
    parser.add_argument(
        '--camping-only',
        action='store_true',
        help='Generate only camping orders (Fabric channel)'
    )
    
    parser.add_argument(
        '--kitchen-only', 
        action='store_true',
        help='Generate only kitchen orders (Databricks channel)'
    )
    
    parser.add_argument(
        '--ski-only',
        action='store_true', 
        help='Generate only ski orders (Winter Sports channel)'
    )
    
    parser.add_argument(
        '--enable-growth',
        action='store_true', 
        help='Enable business growth patterns and market events (experimental)'
    )
    
    parser.add_argument(
        '--graph',
        action='store_true', 
        help='Generate revenue trend graph (requires matplotlib: pip install matplotlib)'
    )
    
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Save graphs without displaying (for automation)'
    )
    
    parser.add_argument(
        '--copydata',
        type=str,
        metavar='OUTPUT_DIR',
        help='Copy generated files to the specified output directory'
    )
    
    return parser.parse_args()

def generate_summary_file(start_date, end_date, camping_stats, kitchen_stats, ski_stats, run_camping, run_kitchen, run_ski):
    """Generate comprehensive summary file with current run statistics"""
    from datetime import datetime
    
    base_path = Path(__file__).parent
    output_dir = base_path / "output"
    summary_file = output_dir / "sample_sales_data_summary.md"
    
    # Calculate totals
    total_orders = 0
    total_lines = 0
    total_sales_payments = 0
    total_invoices = 0
    total_finance_payments = 0
    total_accounts = 0
    total_sales_value = 0.0
    
    # Collect domain statistics
    domains = []
    
    if run_camping and camping_stats:
        total_orders += camping_stats['orders']
        total_lines += camping_stats['order_lines']
        total_sales_payments += camping_stats['sales_payments']
        total_invoices += camping_stats['invoices']
        total_finance_payments += camping_stats['finance_payments']
        total_accounts += camping_stats['accounts']
        total_sales_value += camping_stats.get('total_value', 0)
        domains.append({
            'name': 'Camping',
            'emoji': '🏕️',
            'orders': camping_stats['orders'],
            'value': camping_stats.get('total_value', 0),
            'avg_order': camping_stats.get('total_value', 0) / camping_stats['orders'] if camping_stats['orders'] > 0 else 0
        })
    
    if run_kitchen and kitchen_stats:
        total_orders += kitchen_stats['orders']
        total_lines += kitchen_stats['order_lines']
        total_sales_payments += kitchen_stats['sales_payments']
        total_invoices += kitchen_stats['invoices']
        total_finance_payments += kitchen_stats['finance_payments']
        total_accounts += kitchen_stats['accounts']
        total_sales_value += kitchen_stats.get('total_value', 0)
        domains.append({
            'name': 'Kitchen',
            'emoji': '🍳',
            'orders': kitchen_stats['orders'],
            'value': kitchen_stats.get('total_value', 0),
            'avg_order': kitchen_stats.get('total_value', 0) / kitchen_stats['orders'] if kitchen_stats['orders'] > 0 else 0
        })
    
    if run_ski and ski_stats:
        total_orders += ski_stats['orders']
        total_lines += ski_stats['order_lines']
        total_sales_payments += ski_stats['sales_payments']
        total_invoices += ski_stats['invoices']
        total_finance_payments += ski_stats['finance_payments']
        total_accounts += ski_stats['accounts']
        total_sales_value += ski_stats.get('total_value', 0)
        domains.append({
            'name': 'Ski',
            'emoji': '⛷️',
            'orders': ski_stats['orders'],
            'value': ski_stats.get('total_value', 0),
            'avg_order': ski_stats.get('total_value', 0) / ski_stats['orders'] if ski_stats['orders'] > 0 else 0
        })
    
    # Generate summary content
    generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary_content = f"""# Sales Data Generation Summary

**Generated**: {generation_time}  
**Date Range**: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}  
**Duration**: {(end_date - start_date).days + 1} days

## 📊 Generation Overview

### **Total Summary**
- **Orders**: {total_orders:,}
- **Order Lines**: {total_lines:,}
- **Sales Payments**: {total_sales_payments:,}
- **Invoices**: {total_invoices:,}
- **Finance Payments**: {total_finance_payments:,}
- **Customer Accounts**: {total_accounts:,}
- **Total Sales Value**: ${total_sales_value:,.2f}

### **Domain Performance**

| Domain | Orders | Total Sales | Avg Order Value |
|--------|--------|-------------|----------------|
"""
    
    for domain in domains:
        summary_content += f"| {domain['emoji']} {domain['name']} | {domain['orders']:,} | ${domain['value']:,.2f} | ${domain['avg_order']:.2f} |\n"
    
    summary_content += f"""

## 🎯 Key Metrics

### **Business Intelligence Ready**
- **Comprehensive Dataset**: {(end_date - start_date).days + 1} days of realistic business data
- **Multi-Domain Coverage**: {len(domains)} product categories with seasonal patterns
- **Customer Hierarchy**: 513 customers across Individual, Business, and Government segments
- **Financial Completeness**: Full order-to-payment lifecycle with invoicing

### **Data Volume**
- **Average Orders per Day**: {total_orders / max((end_date - start_date).days + 1, 1):.1f}
- **Average Order Value**: ${total_sales_value / max(total_orders, 1):.2f}
- **Order Line Items**: {total_lines / max(total_orders, 1):.1f} items per order average
- **Customer Coverage**: {total_accounts} accounts across all domains
"""
    
    # Write summary file
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        print(f"\n📋 Generated summary file: {summary_file}")
    except Exception as e:
        print(f"❌ Failed to generate summary file: {e}")

def copy_csv_files(output_dest_path):
    """Copy CSV files from input and output folders to the specified destination directory"""
    print("\n" + "=" * 60)
    print("📁 COPYING CSV FILES TO OUTPUT DIRECTORY")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    
    # Define source and destination paths
    input_source = base_path / "input"
    output_source = base_path / "output"
    output_dest = Path(output_dest_path).resolve()
    
    # Ensure destination directories exist
    output_dest.mkdir(parents=True, exist_ok=True)
    
    copied_files = 0
    
    # Copy CSV files from output (recursively)
    print(f"📂 Copying CSV files from output folder to {output_dest}...")
    output_csv_files = glob.glob(str(output_source / "**" / "*.csv"), recursive=True)
    for csv_file in output_csv_files:
        src_file = Path(csv_file)
        # Preserve the folder structure under output
        rel_path = src_file.relative_to(output_source)
        dest_file = output_dest / rel_path
        
        # Ensure destination subdirectory exists
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(src_file, dest_file)
            print(f"   ✅ {rel_path} → {dest_file}")
            copied_files += 1
        except Exception as e:
            print(f"   ❌ Failed to copy {rel_path}: {e}")
    
    # Copy summary markdown file to destination root
    summary_file = output_source / "sample_sales_data_summary.md"
    if summary_file.exists():
        dest_summary = output_dest / "sample_sales_data_summary.md"
        try:
            shutil.copy2(summary_file, dest_summary)
            print(f"\n📋 Copying summary file...")
            print(f"   ✅ sample_sales_data_summary.md → {dest_summary}")
            copied_files += 1
        except Exception as e:
            print(f"   ❌ Failed to copy summary file: {e}")
    
    # Copy product files to infra/data/product/
    product_dest = output_dest / "product"
    product_dest.mkdir(parents=True, exist_ok=True)
    
    product_files = [
        "ProductCategory_Samples.csv",
        "ProductCategory_Samples_Camping.csv", 
        "ProductCategory_Samples_Combined.csv",
        "ProductCategory_Samples_Kitchen.csv",
        "ProductCategory_Samples_Ski.csv",
        "Product_Samples_Camping.csv",
        "Product_Samples_Combined.csv",
        "Product_Samples_Kitchen.csv",
        "Product_Samples_Ski.csv"
    ]
    
    print(f"\n📦 Copying product files to {product_dest.resolve()}...")
    for file_name in product_files:
        src_file = input_source / file_name
        if src_file.exists():
            dest_file = product_dest / file_name
            try:
                shutil.copy2(src_file, dest_file)
                print(f"   ✅ {file_name} → product/")
                copied_files += 1
            except Exception as e:
                print(f"   ❌ Failed to copy {file_name}: {e}")
    
    # Copy customer files to infra/data/customer/
    customer_dest = output_dest / "customer"
    customer_dest.mkdir(parents=True, exist_ok=True)
    
    customer_files = [
        "CustomerAccount_Samples.csv",
        "CustomerRelationshipType_Samples.csv",
        "CustomerTradeName_Samples.csv", 
        "Customer_Samples.csv",
        "Location_Samples.csv"
    ]
    
    print(f"\n👥 Copying customer files to {customer_dest.resolve()}...")
    for file_name in customer_files:
        src_file = input_source / file_name
        if src_file.exists():
            dest_file = customer_dest / file_name
            try:
                shutil.copy2(src_file, dest_file)
                print(f"   ✅ {file_name} → customer/")
                copied_files += 1
            except Exception as e:
                print(f"   ❌ Failed to copy {file_name}: {e}")
    
    print(f"\n📊 File Copy Summary: {copied_files} files copied successfully")
    print("=" * 60)

def generate_revenue_graph(start_date, end_date, run_camping, run_kitchen, run_ski, no_display=False):
    """Generate revenue trend graph from generated CSV data"""
    if not MATPLOTLIB_AVAILABLE:
        print("⚠️  Graphing skipped - matplotlib not available. Install with: pip install matplotlib")
        return
    
    print("📊 Generating revenue trend graph...")
    
    base_path = Path(__file__).parent
    output_dir = base_path / "output"
    
    all_orders = []
    domain_colors = {'Camping': '#228B22', 'Kitchen': '#FF6347', 'Ski': '#4169E1'}
    
    try:
        # Load order data from each domain
        if run_camping:
            camping_file = output_dir / "sales" / "camping" / "Order_Samples_Camping.csv"
            if camping_file.exists():
                df = pd.read_csv(camping_file)
                df['Domain'] = 'Camping'
                df['Color'] = domain_colors['Camping']
                all_orders.append(df[['OrderDate', 'OrderTotal', 'Domain', 'Color']])
        
        if run_kitchen:
            kitchen_file = output_dir / "sales" / "kitchen" / "Order_Samples_Kitchen.csv"
            if kitchen_file.exists():
                df = pd.read_csv(kitchen_file)
                df['Domain'] = 'Kitchen'
                df['Color'] = domain_colors['Kitchen']
                all_orders.append(df[['OrderDate', 'OrderTotal', 'Domain', 'Color']])
        
        if run_ski:
            ski_file = output_dir / "sales" / "ski" / "Order_Samples_Ski.csv"
            if ski_file.exists():
                df = pd.read_csv(ski_file)
                df['Domain'] = 'Ski'
                df['Color'] = domain_colors['Ski']
                all_orders.append(df[['OrderDate', 'OrderTotal', 'Domain', 'Color']])
        
        if not all_orders:
            print("⚠️  No order data found for graphing")
            return
        
        # Combine all order data
        combined_df = pd.concat(all_orders, ignore_index=True)
        combined_df['OrderDate'] = pd.to_datetime(combined_df['OrderDate'])
        
        # Create monthly period for grouping
        combined_df['Month'] = combined_df['OrderDate'].dt.to_period('M')
        
        # Group by month and domain for monthly revenue
        monthly_revenue = combined_df.groupby(['Month', 'Domain'])['OrderTotal'].sum().reset_index()
        monthly_revenue['Month'] = monthly_revenue['Month'].dt.to_timestamp()  # Convert back to datetime
        
        # Create the graph with monthly data
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
        fig.suptitle(f'Monthly Sales Revenue Trends - {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}', 
                     fontsize=16, fontweight='bold')
        
        # Top chart: Individual domain trends
        for domain in monthly_revenue['Domain'].unique():
            domain_data = monthly_revenue[monthly_revenue['Domain'] == domain]
            line_style = '--' if domain in ['Kitchen', 'Ski'] else '-'  # Dashed for domains without growth patterns
            ax1.plot(domain_data['Month'], domain_data['OrderTotal'], 
                    label=f'{domain}{"*" if domain == "Camping" else ""}', 
                    color=domain_colors[domain], linewidth=3, marker='o', markersize=5, linestyle=line_style)
        
        ax1.set_title('Monthly Revenue by Domain (* = Business Growth Enabled)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Monthly Revenue ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Bottom chart: Total combined revenue with trend line
        total_monthly = combined_df.groupby('Month')['OrderTotal'].sum().reset_index()
        total_monthly['Month'] = total_monthly['Month'].dt.to_timestamp()
        
        ax2.fill_between(total_monthly['Month'], total_monthly['OrderTotal'], 
                        alpha=0.3, color='purple', label='Total Monthly Revenue')
        ax2.plot(total_monthly['Month'], total_monthly['OrderTotal'], 
                color='purple', linewidth=3, marker='o', markersize=5)
        
        # Add trend line for growth pattern visualization
        if len(total_monthly) >= 3:
            z = np.polyfit(range(len(total_monthly)), total_monthly['OrderTotal'], 2)  # Quadratic fit
            p = np.poly1d(z)
            trend_line = p(range(len(total_monthly)))
            ax2.plot(total_monthly['Month'], trend_line, 
                    color='red', linewidth=2, linestyle='--', alpha=0.8, 
                    label='Growth Trend (3-Phase Pattern)')
        
        ax2.set_title('Total Monthly Revenue with Growth Trend Analysis', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Monthly Revenue ($)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        
        # Format x-axis dates for monthly view
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save the graph
        graph_file = output_dir / "revenue_trend_graph.png"
        plt.savefig(graph_file, dpi=150, bbox_inches='tight')
        
        # Show summary statistics (now monthly-based)
        total_revenue = combined_df['OrderTotal'].sum()
        avg_monthly_revenue = total_monthly['OrderTotal'].mean()
        max_monthly_revenue = total_monthly['OrderTotal'].max()
        
        # Growth pattern analysis (only for domains with growth enabled)
        growth_analysis = ""
        camping_data = monthly_revenue[monthly_revenue['Domain'] == 'Camping']
        if not camping_data.empty and len(camping_data) >= 6:  # Need enough data for analysis
            first_third = camping_data.head(len(camping_data)//3)['OrderTotal'].mean()
            middle_third = camping_data.iloc[len(camping_data)//3:2*len(camping_data)//3]['OrderTotal'].mean()
            last_third = camping_data.tail(len(camping_data)//3)['OrderTotal'].mean()
            
            growth_analysis = f"""
📊 Business Growth Pattern Analysis (Camping Domain):
   Phase 1 Average: ${first_third:,.2f}/month
   Phase 2 Average: ${middle_third:,.2f}/month  
   Phase 3 Average: ${last_third:,.2f}/month
   Phase 2 vs Phase 1: {((middle_third/first_third-1)*100):+.1f}%
   Phase 3 vs Phase 2: {((last_third/middle_third-1)*100):+.1f}%"""
        
        print(f"✅ Revenue graph saved: {graph_file}")
        print(f"📈 Revenue Statistics:")
        print(f"   Total Revenue: ${total_revenue:,.2f}")
        print(f"   Average Monthly: ${avg_monthly_revenue:,.2f}")
        print(f"   Peak Monthly: ${max_monthly_revenue:,.2f}")
        print(growth_analysis)
        
        # Display the graph (only if not running in automation mode)
        if not no_display:
            plt.show()
        
    except Exception as e:
        print(f"❌ Error generating revenue graph: {e}")
        print("   Make sure matplotlib and pandas are installed: pip install matplotlib pandas")

def main():
    """Main orchestrator function"""
    
    args = parse_arguments()
    
    # Parse required date range
    start_date = parse_date(args.start_date)
    end_date = parse_date(args.end_date)
    
    # Validate date range
    if start_date >= end_date:
        raise ValueError(f"Start date ({start_date.date()}) must be before end date ({end_date.date()})")
    
    print("🎯 Sample Data Generation Orchestrator")
    print("=" * 50)
    print(f"📅 Date Range: {start_date.date()} to {end_date.date()}")
    
    if args.enable_growth:
        print("📈 Business Growth Patterns: ENABLED")
        print("   • Three-phase growth simulation")
        print("   • Market event simulation (Black Friday, Christmas, etc.)")
        print("   • Customer tier amplification")
    else:
        print("📊 Standard Data Generation: ENABLED")
        print("   • Use --enable-growth for realistic business patterns")
    
    # Determine which generators to run
    run_camping = not (args.kitchen_only or args.ski_only) or args.camping_only
    run_kitchen = not (args.camping_only or args.ski_only) or args.kitchen_only  
    run_ski = not (args.camping_only or args.kitchen_only) or args.ski_only
    
    generators_to_run = []
    if run_camping:
        generators_to_run.append("🏕️  Camping")
    if run_kitchen:
        generators_to_run.append("🍳 Kitchen")
    if run_ski:
        generators_to_run.append("⛷️  Ski")
    
    print(f"🔄 Generating data for: {', '.join(generators_to_run)}")
    print()
    
    total_orders = 0
    total_lines = 0
    total_sales_payments = 0
    total_invoices = 0
    total_finance_payments = 0
    total_accounts = 0
    
    try:
        # Generate camping product orders (Fabric channel)
        if run_camping:
            print("=" * 60)
            camping_stats = generate_camping_orders(start_date, end_date, 100000, args.enable_growth)
            total_orders += camping_stats['orders']
            total_lines += camping_stats['order_lines'] 
            total_sales_payments += camping_stats['sales_payments']
            total_invoices += camping_stats['invoices']
            total_finance_payments += camping_stats['finance_payments']
            total_accounts += camping_stats['accounts']
            print()
        
        # Generate kitchen product orders (Databricks channel)  
        if run_kitchen:
            print("=" * 60)
            kitchen_stats = generate_kitchen_orders(start_date, end_date, 200000, args.enable_growth)
            total_orders += kitchen_stats['orders']
            total_lines += kitchen_stats['order_lines']
            total_sales_payments += kitchen_stats['sales_payments']
            total_invoices += kitchen_stats['invoices']
            total_finance_payments += kitchen_stats['finance_payments']
            total_accounts += kitchen_stats['accounts']
            print()
        
        # Generate ski product orders (Winter Sports channel)
        if run_ski:
            print("=" * 60)
            ski_stats = generate_ski_orders(start_date, end_date, 300000)  
            total_orders += ski_stats['orders']
            total_lines += ski_stats['order_lines']
            total_sales_payments += ski_stats['sales_payments']
            total_invoices += ski_stats['invoices']
            total_finance_payments += ski_stats['finance_payments']
            total_accounts += ski_stats['accounts']
            print()
        
        # Summary
        print("=" * 60)
        print("🎉 ALL SAMPLE DATA GENERATION COMPLETE!")
        print("=" * 60)
        print(f"📊 Total Summary:")
        print(f"   Orders: {total_orders:,}")
        print(f"   Order Lines: {total_lines:,}")
        print(f"   Sales Payments: {total_sales_payments:,}")
        print(f"   Invoices: {total_invoices:,}")
        print(f"   Finance Payments: {total_finance_payments:,}")
        print(f"   Customer Accounts: {total_accounts:,}")
        print()
        print("📁 Output Locations:")
        if run_camping:
            print("   🏕️  Camping Sales: src/data_simulator/output/camping/sales/")
            print("   🏕️  Camping Finance: src/data_simulator/output/camping/finance/")
        if run_kitchen:
            print("   🍳 Kitchen Sales: src/data_simulator/output/kitchen/sales/")
            print("   🍳 Kitchen Finance: src/data_simulator/output/kitchen/finance/")
        if run_ski:
            print("   ⛷️  Ski Sales: src/data_simulator/output/ski/sales/")
            print("   ⛷️  Ski Finance: src/data_simulator/output/ski/finance/")
        
        # Generate summary file with current run statistics
        generate_summary_file(start_date, end_date, 
                             camping_stats if run_camping else None,
                             kitchen_stats if run_kitchen else None, 
                             ski_stats if run_ski else None,
                             run_camping, run_kitchen, run_ski)
        
        # Generate revenue graph if requested
        if args.graph:
            print("\n" + "="*60)
            generate_revenue_graph(start_date, end_date, run_camping, run_kitchen, run_ski, args.no_display)
        
        # Copy CSV files to user-specified output directory (if requested)
        if args.copydata:
            copy_csv_files(args.copydata)
        
    except Exception as e:
        print(f"❌ Error during generation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()