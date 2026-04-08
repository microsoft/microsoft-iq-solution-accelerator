#!/usr/bin/env python3
"""
Ski Product Data Generator - Winter Sports Channel
=================================================

Generates realistic sales & finance data for ski equipment:
⛷️  Highly seasonal (peak winter, off-season summer)
👥 Customer segmentation (Federal orders rare - not government need)
💰 Simplified pricing (no discounts), highest average order values

Usage:
  python generate_ski_orders.py -s 2025-01-01 -e 2025-12-31

Outputs 6 CSV files:
Sales: Order, OrderLine, OrderPayment → sales/ski/
Finance: Invoice, Payment, Account → finance/ski/

Author: GitHub Copilot  
Date: January 14, 2026
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid
import os
import argparse
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.absolute()
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output" / "sales" / "ski"
FINANCE_OUTPUT_DIR = BASE_DIR / "output" / "finance" / "ski"

# Input file paths
CUSTOMER_FILE = INPUT_DIR / "Customer_Samples.csv"
ACCOUNT_FILE = INPUT_DIR / "CustomerAccount_Samples.csv"
PRODUCT_FILE = INPUT_DIR / "Product_Samples_Ski.csv"
LOCATION_FILE = INPUT_DIR / "Location_Samples.csv"

# Output file paths - Sales
ORDER_FILE = OUTPUT_DIR / "Order_Samples_Ski.csv"
ORDERLINE_FILE = OUTPUT_DIR / "OrderLine_Samples_Ski.csv"
ORDERPAYMENT_FILE = OUTPUT_DIR / "OrderPayment_Ski.csv"

# Output file paths - Finance
INVOICE_FILE = FINANCE_OUTPUT_DIR / "Invoice_Samples_Ski.csv"
PAYMENT_FILE = FINANCE_OUTPUT_DIR / "Payment_Samples_Ski.csv"
ACCOUNT_FIN_FILE = FINANCE_OUTPUT_DIR / "Account_Samples_Ski.csv"

# Data generation parameters
# Remove default dates - require user to specify
# DEFAULT_START_DATE = datetime(2020, 1, 1)
# DEFAULT_END_DATE = datetime(2026, 1, 12)  # Default end date
ORDER_NUMBER_START = 300000  # Different from other channels

# Customer hierarchy structure matching schema
CUSTOMER_HIERARCHY = {
    'Individual': {
        'Standard': (1, 2),   # 1-2 orders
        'Premium': (2, 4),    # 2-4 orders
        'VIP': (3, 7)         # 3-7 orders
    },
    'Business': {
        'SMB': (2, 5),        # Small/Medium Business: 2-5 orders
        'Premier': (4, 9),    # Premier Business: 4-9 orders
        'Partner': (5, 12)    # Partner Business: 5-12 orders (highest)
    },
    'Government': {
        'Federal': (0, 1),    # Federal Government: 0-1 orders (ski equipment not common)
        'State': (1, 2),      # State Government: 1-2 orders
        'Local': (1, 2)       # Local Government: 1-2 orders
    }
}

# Flatten hierarchy for backwards compatibility and easier selection
SEGMENT_ORDER_FREQ = {}
for customer_type, relationships in CUSTOMER_HIERARCHY.items():
    for relationship_type, freq_range in relationships.items():
        SEGMENT_ORDER_FREQ[relationship_type] = freq_range

# Ski product preferences by season (winter sports are highly seasonal)
SEASONAL_PREFERENCES = {
    "winter": {301: 0.25, 302: 0.1, 303: 0.2, 304: 0.1, 305: 0.15, 306: 0.08, 307: 0.05, 308: 0.02, 309: 0.03, 310: 0.02},  # Peak ski season
    "fall": {301: 0.15, 302: 0.05, 303: 0.25, 304: 0.08, 305: 0.2, 306: 0.1, 307: 0.05, 308: 0.1, 309: 0.01, 310: 0.01},   # Equipment prep season
    "spring": {301: 0.1, 302: 0.08, 303: 0.1, 304: 0.05, 305: 0.1, 306: 0.05, 307: 0.02, 308: 0.3, 309: 0.1, 310: 0.1},   # Maintenance season
    "summer": {301: 0.05, 302: 0.02, 303: 0.05, 304: 0.02, 305: 0.03, 306: 0.03, 307: 0.1, 308: 0.4, 309: 0.25, 310: 0.05}  # Off-season maintenance/storage
}

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
        description='Generate Ski Product Orders for Winter Sports Channel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Examples:
  python generate_ski_orders.py                        # Full date range
  python generate_ski_orders.py -s 2025-01-01         # From 2025
  python generate_ski_orders.py -s 2024-06-01 -e 2024-12-31
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
        '--order-start', 
        type=int,
        default=ORDER_NUMBER_START,
        help=f'Starting order number. Default: {ORDER_NUMBER_START}'
    )
    
    return parser.parse_args()

def random_date(start, end):
    """Generate a random datetime between start and end"""
    delta = end - start
    int_delta = delta.days
    random_day = random.randrange(int_delta)
    return start + timedelta(days=random_day)

def get_season(date):
    """Determine season from date for ski product preferences"""
    month = date.month
    if month in [12, 1, 2]:
        return "winter"  # Peak ski season
    elif month in [3, 4, 5]:
        return "spring"  # End of season, maintenance
    elif month in [6, 7, 8]:
        return "summer"  # Off-season, storage, maintenance
    else:
        return "fall"    # Pre-season, equipment purchase

def get_customer_type_from_relationship(relationship_type):
    """Get CustomerTypeId from CustomerRelationshipTypeId"""
    for customer_type, relationships in CUSTOMER_HIERARCHY.items():
        if relationship_type in relationships:
            return customer_type
    return 'Individual'  # fallback

def pick_payment_method():
    """Select payment method with realistic distribution for winter sports"""
    return random.choices(
        ["VISA", "MC", "AmEx", "Discover", "PayPal"],
        weights=[0.30, 0.25, 0.20, 0.10, 0.15]  # Higher AmEx usage in sports, PayPal adjusted
    )[0]

def pick_order_status():
    """Select order status with realistic distribution"""
    return random.choices(
        ["Completed", "Pending", "Cancelled", "Shipped"],
        weights=[0.75, 0.10, 0.05, 0.10]
    )[0]

def select_products_by_season(products_df, order_date, num_products):
    """Select ski products based on seasonal winter sports preferences"""
    season = get_season(order_date)
    season_weights = SEASONAL_PREFERENCES[season]
    
    # Add season weight to products based on their category
    products_with_weights = []
    for _, product in products_df.iterrows():
        category_id = int(product['ProductCategoryID'])
        weight = season_weights.get(category_id, 0.01)
        products_with_weights.extend([product] * int(weight * 100))
    
    # Randomly select from weighted list
    if len(products_with_weights) >= num_products:
        return random.sample(products_with_weights, num_products)
    else:
        # If not enough weighted products, fill with random selection
        selected = products_with_weights[:]
        remaining = num_products - len(selected)
        additional = products_df.sample(n=remaining).to_dict('records')
        selected.extend(additional)
        return selected

def calculate_discount(unit_price, customer_segment, quantity):
    """No discounts applied - simplified pricing"""
    return 0.0

def generate_ski_orders(start_date, end_date, order_start_number):
    """Generate ski product orders and finance data for winter sports channel"""
    
    print("⛷️  Generating Ski Product Orders for Winter Sports Channel")
    print("=" * 64)
    print(f"📅 Date Range: {start_date.date()} to {end_date.date()}")
    print(f"📊 Order Number Start: S{order_start_number}")
    
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FINANCE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load input data
    print("\n📂 Loading input data...")
    df_customer = pd.read_csv(CUSTOMER_FILE)
    df_account = pd.read_csv(ACCOUNT_FILE)
    df_product = pd.read_csv(PRODUCT_FILE)
    
    # Filter accounts to Ski channel only
    df_winter_accounts = df_account[df_account['CustomerAccountName'] == 'Ski'].copy()
    
    print(f"   Customers: {len(df_customer):,}")
    print(f"   Ski Accounts: {len(df_winter_accounts):,}")
    print(f"   Ski Products: {len(df_product):,}")
    
    # Initialize data containers
    orders = []
    orderlines = []
    orderpayments = []
    invoices = []
    payments = []
    accounts = []
    
    order_id_set = set()
    order_number_counter = order_start_number
    
    print("\n🎯 Generating orders and order lines...")
    
    # Generate orders for each customer with ski accounts
    customers_with_winter = df_customer[
        df_customer['CustomerID'].isin(df_winter_accounts['CustomerID'])
    ]
    
    for idx, customer in customers_with_winter.iterrows():
        if idx > 0 and idx % 100 == 0:
            print(f"   Processed {idx}/{len(customers_with_winter)} customers...")
        
        customer_id = customer['CustomerID']
        customer_segment = customer.get('CustomerRelationshipTypeID', 'Standard')
        customer_type = get_customer_type_from_relationship(customer_segment)
        
        # Get customer's account (randomly pick if they have multiple)
        customer_accounts = df_winter_accounts[df_winter_accounts['CustomerID'] == customer_id]
        if customer_accounts.empty:
            continue
            
        account = customer_accounts.sample(n=1).iloc[0]
        account_id = account['CustomerAccountID']
        
        # Determine number of orders for this customer (ski equipment tends to be purchased less frequently)
        freq_range = SEGMENT_ORDER_FREQ.get(customer_segment, (1, 2))
        num_orders = random.randint(freq_range[0], freq_range[1])
        
        for _ in range(num_orders):
            # Generate unique order ID
            order_id = str(uuid.uuid4())
            while order_id in order_id_set:
                order_id = str(uuid.uuid4())
            order_id_set.add(order_id)
            
            # Order details
            order_number = f"S{order_number_counter}"
            order_number_counter += 1
            order_date = random_date(start_date, end_date)
            order_status = pick_order_status()
            payment_method = pick_payment_method()
            
            # Generate order lines (1-4 products per order for ski equipment)
            num_lines = random.randint(1, 4)
            selected_products = select_products_by_season(df_product, order_date, num_lines)
            
            subtotal = 0
            total_tax = 0
            
            for line_num, product in enumerate(selected_products, start=1):
                if isinstance(product, dict):
                    # Already a dict from season selection
                    prod_data = product
                else:
                    # Convert Series to dict
                    prod_data = product
                
                product_id = prod_data['ProductID']
                product_name = prod_data['ProductName']
                unit_price = float(prod_data['ListPrice'])
                quantity = random.randint(1, 2)  # Ski equipment typically 1-2 items (expensive)
                
                discount = calculate_discount(unit_price, customer_segment, quantity)
                line_total = round((unit_price * quantity) - discount, 2)
                tax = round(line_total * 0.0875, 2)  # Typical sales tax rate
                
                subtotal += line_total
                total_tax += tax
                
                orderlines.append({
                    "OrderID": order_id,
                    "OrderLineNumber": line_num,
                    "ProductID": product_id,
                    "ProductName": product_name,
                    "Quantity": quantity,
                    "UnitPrice": unit_price,
                    "LineTotal": line_total,
                    "DiscountAmount": discount,
                    "TaxAmount": tax
                })
            
            order_total = round(subtotal + total_tax, 2)
            
            # Create order record
            orders.append({
                "OrderID": order_id,
                "SalesChannelID": account['CustomerAccountName'],
                "OrderNumber": order_number,
                "CustomerID": customer_id,
                "CustomerAccountID": account_id,
                "OrderDate": order_date.date(),
                "OrderStatus": order_status,
                "SubTotal": round(subtotal, 2),
                "TaxAmount": round(total_tax, 2),
                "OrderTotal": order_total,
                "PaymentMethod": payment_method,
                "IsoCurrencyCode": "USD",
                "CreatedBy": "SampleGen"
            })
            
            # Create payment record
            orderpayments.append({
                "OrderID": order_id,
                "PaymentMethod": payment_method,
                "TransactionID": str(uuid.uuid4())
            })
            
            # Generate finance data for this order
            invoice_id = f"INV-{order_id}"
            invoice_number = f"I{order_number}"
            
            # Invoice date is next day after order
            invoice_date = order_date + timedelta(days=1)
            due_date = invoice_date + timedelta(days=30)
            
            # Create invoice record
            invoices.append({
                "InvoiceID": invoice_id,
                "InvoiceNumber": invoice_number,
                "CustomerID": customer_id,
                "OrderID": order_id,
                "InvoiceDate": invoice_date.date(),
                "DueDate": due_date.date(),
                "SubTotal": round(subtotal, 2),
                "TaxAmount": round(total_tax, 2),
                "TotalAmount": order_total,
                "InvoiceStatus": "Paid",  # eCommerce simplification - immediate payment
                "CreatedBy": "SampleGen"
            })
            
            # Create payment record (immediate payment for eCommerce)
            finance_payment_id = f"PAY-{order_id}"
            payments.append({
                "PaymentID": finance_payment_id,
                "InvoiceID": invoice_id,
                "CustomerID": customer_id,
                "PaymentDate": invoice_date.date(),
                "PaymentAmount": order_total,
                "PaymentMethod": payment_method,
                "PaymentStatus": "Completed",
                "CreatedBy": "SampleGen"
            })
    
    # Generate customer accounts for finance (Ski channel)
    print("\n🏦 Generating customer accounts for finance...")
    ski_customers = df_account[df_account['CustomerAccountName'] == 'Ski']['CustomerID'].unique()
    for customer_id in ski_customers:
        account_id = f"ACCT-Ski-{customer_id}"
        accounts.append({
            "AccountID": account_id,
            "AccountNumber": f"ACC-{customer_id}-Ski",
            "CustomerID": customer_id,
            "AccountType": "Receivable",
            "AccountStatus": "Active",
            "CreatedDate": start_date.date(),
            "ClosedDate": "",  # Empty string for active accounts
            "Balance": 0.0,  # Zero balance since payments are immediate
            "Currency": "USD",
            "Description": f"Accounts Receivable for Customer {customer_id} - Ski Channel",
            "CreatedBy": "SampleGen"
        })

    print(f"\\n📊 Generation Summary:")
    print(f"   Orders: {len(orders):,}")
    print(f"   Order Lines: {len(orderlines):,}")
    print(f"   Sales Payments: {len(orderpayments):,}")
    print(f"   Invoices: {len(invoices):,}")
    print(f"   Finance Payments: {len(payments):,}")
    print(f"   Customer Accounts: {len(accounts):,}")
    
    # Write output files (overwrite existing)
    print("\n💾 Writing output files...")
    print("   📝 Overwriting any existing files...")
    
    # Sales files
    pd.DataFrame(orders).to_csv(ORDER_FILE, index=False)
    print(f"   ✅ {ORDER_FILE}")
    
    pd.DataFrame(orderlines).to_csv(ORDERLINE_FILE, index=False)
    print(f"   ✅ {ORDERLINE_FILE}")
    
    pd.DataFrame(orderpayments).to_csv(ORDERPAYMENT_FILE, index=False)
    print(f"   ✅ {ORDERPAYMENT_FILE}")
    
    # Finance files
    pd.DataFrame(invoices).to_csv(INVOICE_FILE, index=False)
    print(f"   ✅ {INVOICE_FILE}")
    
    pd.DataFrame(payments).to_csv(PAYMENT_FILE, index=False)
    print(f"   ✅ {PAYMENT_FILE}")
    
    pd.DataFrame(accounts).to_csv(ACCOUNT_FIN_FILE, index=False)
    print(f"   ✅ {ACCOUNT_FIN_FILE}")
    
    print(f"\\n🎉 Ski product sales & finance data generation complete!")
    print(f"   Sales output: {OUTPUT_DIR}")
    print(f"   Finance output: {FINANCE_OUTPUT_DIR}")
    
    # Display sample statistics
    orders_df = pd.DataFrame(orders)
    print(f"\n📈 Statistics:")
    print(f"   Date range: {orders_df['OrderDate'].min()} to {orders_df['OrderDate'].max()}")
    print(f"   Total order value: ${orders_df['OrderTotal'].sum():,.2f}")
    print(f"   Average order value: ${orders_df['OrderTotal'].mean():.2f}")
    print(f"   Order status distribution:")
    for status, count in orders_df['OrderStatus'].value_counts().items():
        print(f"     {status}: {count:,} ({count/len(orders_df)*100:.1f}%)")
    
    # Return statistics for main orchestrator
    return {
        'orders': len(orders),
        'order_lines': len(orderlines),
        'sales_payments': len(orderpayments),
        'invoices': len(invoices),
        'finance_payments': len(payments),
        'accounts': len(accounts),
        'total_value': orders_df['OrderTotal'].sum()
    }

def main():
    """Main function for standalone execution"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Parse required date range
    start_date = parse_date(args.start_date)
    end_date = parse_date(args.end_date)
    
    # Validate date range
    if start_date >= end_date:
        raise ValueError(f"Start date ({start_date.date()}) must be before end date ({end_date.date()})")
    
    # Call the generator function
    generate_ski_orders(start_date, end_date, args.order_start)

if __name__ == "__main__":
    # Set random seed for reproducible results
    random.seed(42)
    np.random.seed(42)
    
    main()