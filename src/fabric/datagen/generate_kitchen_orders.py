#!/usr/bin/env python3
"""
Kitchen Product Data Generator
==============================

Generates realistic sales & finance data for kitchen products:
🍳 Holiday seasonality (more bakeware/coffee makers in winter)
👥 Customer segmentation with enhanced frequencies for revenue visibility  
💰 Boosted order sizes with 2x revenue multiplier (avg $560+)
📈 Business growth patterns enabled (3-phase growth simulation)

Usage:
  python generate_kitchen_orders.py -s 2025-01-01 -e 2025-12-31
  python generate_kitchen_orders.py --enable-growth  # Enable growth patterns

Outputs 6 CSV files:
Sales: Order, OrderLine, OrderPayment → sales/kitchen/
Finance: Invoice, Payment, Account → finance/kitchen/

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
import business_growth_logic

# Configuration
BASE_DIR = Path(__file__).parent.absolute()
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output" / "sales" / "kitchen"
FINANCE_OUTPUT_DIR = BASE_DIR / "output" / "finance" / "kitchen"

# Input file paths
CUSTOMER_FILE = INPUT_DIR / "Customer_Samples.csv"
ACCOUNT_FILE = INPUT_DIR / "CustomerAccount_Samples.csv"
PRODUCT_FILE = INPUT_DIR / "Product_Samples_Kitchen.csv"
LOCATION_FILE = INPUT_DIR / "Location_Samples.csv"

# Output file paths - Sales
ORDER_FILE = OUTPUT_DIR / "Order_Samples_Kitchen.csv"
ORDERLINE_FILE = OUTPUT_DIR / "OrderLine_Samples_Kitchen.csv"
ORDERPAYMENT_FILE = OUTPUT_DIR / "OrderPayment_Kitchen.csv"

# Output file paths - Finance
INVOICE_FILE = FINANCE_OUTPUT_DIR / "Invoice_Samples_Kitchen.csv"
PAYMENT_FILE = FINANCE_OUTPUT_DIR / "Payment_Samples_Kitchen.csv"
ACCOUNT_FIN_FILE = FINANCE_OUTPUT_DIR / "Account_Samples_Kitchen.csv"

# Data generation parameters
# Remove default dates - require user to specify
# DEFAULT_START_DATE = datetime(2020, 1, 1)
# DEFAULT_END_DATE = datetime(2026, 1, 12)  # Default end date
ORDER_NUMBER_START = 200000  # Different from camping orders

# Customer hierarchy structure matching schema
CUSTOMER_HIERARCHY = {
    'Individual': {
        'Standard': (2, 6),   # 2-6 orders (doubled for revenue boost)
        'Premium': (4, 10),   # 4-10 orders (doubled)
        'VIP': (8, 20)        # 8-20 orders (doubled)
    },
    'Business': {
        'SMB': (6, 14),       # Small/Medium Business: 6-14 orders (doubled)
        'Premier': (10, 24),  # Premier Business: 10-24 orders (doubled)
        'Partner': (12, 30)   # Partner Business: 12-30 orders (doubled for highest)
    },
    'Government': {
        'Federal': (4, 8),    # Federal Government: 4-8 orders (doubled)
        'State': (2, 6),      # State Government: 2-6 orders (doubled)
        'Local': (2, 6)       # Local Government: 2-6 orders (doubled)
    }
}

# Flatten hierarchy for backwards compatibility and easier selection
SEGMENT_ORDER_FREQ = {}
for customer_type, relationships in CUSTOMER_HIERARCHY.items():
    for relationship_type, freq_range in relationships.items():
        SEGMENT_ORDER_FREQ[relationship_type] = freq_range

# Kitchen product preferences by category (more appliances in certain seasons)
CATEGORY_PREFERENCES = {
    "holiday": {201: 0.25, 202: 0.15, 203: 0.15, 204: 0.15, 205: 0.05, 206: 0.1, 207: 0.15},  # Coffee makers, serving dishes, bakeware higher
    "summer": {201: 0.15, 202: 0.1, 203: 0.2, 204: 0.2, 205: 0.2, 206: 0.05, 207: 0.05, 208: 0.05}, # Ice cream, serving dishes
    "fall": {201: 0.2, 202: 0.15, 203: 0.1, 204: 0.1, 205: 0.03, 206: 0.15, 207: 0.2, 208: 0.07}, # Baking season
    "spring": {201: 0.2, 202: 0.15, 203: 0.15, 204: 0.1, 205: 0.05, 206: 0.15, 207: 0.1, 208: 0.1}  # General cooking
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
        description='Generate Kitchen Product Orders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Examples:
  python generate_kitchen_orders.py                    # Full date range
  python generate_kitchen_orders.py -s 2025-01-01     # From 2025
  python generate_kitchen_orders.py -s 2024-06-01 -e 2024-12-31
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
    
    parser.add_argument(
        '--enable-growth',
        action='store_true',
        help='Enable business growth patterns (3-phase growth simulation)'
    )
    
    return parser.parse_args()

def random_date(start, end):
    """Generate a random datetime between start and end"""
    delta = end - start
    int_delta = delta.days
    random_day = random.randrange(int_delta)
    return start + timedelta(days=random_day)

def get_season(date):
    """Determine season from date for kitchen product preferences"""
    month = date.month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "holiday"  # Winter = holiday season for kitchen items

def get_customer_type_from_relationship(relationship_type):
    """Get CustomerTypeId from CustomerRelationshipTypeId"""
    for customer_type, relationships in CUSTOMER_HIERARCHY.items():
        if relationship_type in relationships:
            return customer_type
    return 'Individual'  # fallback

def pick_payment_method():
    """Select payment method with realistic distribution"""
    return random.choices(
        ["VISA", "MC", "AmEx", "Discover", "PayPal"],
        weights=[0.35, 0.25, 0.15, 0.10, 0.10]
    )[0]

def pick_order_status():
    """Select order status with realistic distribution"""
    return random.choices(
        ["Completed", "Pending", "Cancelled", "Shipped"],
        weights=[0.75, 0.10, 0.05, 0.10]
    )[0]

def select_products_by_season(products_df, order_date, num_products):
    """Select kitchen products based on seasonal preferences"""
    season = get_season(order_date)
    season_weights = CATEGORY_PREFERENCES.get(season, CATEGORY_PREFERENCES["spring"])
    
    # Add season weight to products based on their category
    products_with_weights = []
    for _, product in products_df.iterrows():
        category_id = int(product['ProductCategoryID'])
        weight = season_weights.get(category_id, 0.05)
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

def generate_kitchen_orders(start_date, end_date, order_start_number, enable_growth=False):
    """Generate kitchen product orders and finance data"""
    
    print("🍳 Generating Kitchen Product Orders")
    print("=" * 64)
    print(f"📅 Date Range: {start_date.date()} to {end_date.date()}")
    print(f"📊 Order Number Start: D{order_start_number}")
    if enable_growth:
        print("📈 Business Growth Patterns: ENABLED")
        print("   • Three-phase growth simulation")
        print("   • Market event simulation (Black Friday, Christmas, etc.)")
        print("   • Customer tier amplification")
    
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FINANCE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load input data
    print("\n📂 Loading input data...")
    df_customer = pd.read_csv(CUSTOMER_FILE)
    df_account = pd.read_csv(ACCOUNT_FILE)
    df_product = pd.read_csv(PRODUCT_FILE)
    
    # Filter accounts to Kitchen channel only
    df_kitchen_accounts = df_account[df_account['CustomerAccountName'] == 'Kitchen'].copy()
    
    print(f"   Customers: {len(df_customer):,}")
    print(f"   Kitchen Accounts: {len(df_kitchen_accounts):,}")
    print(f"   Kitchen Products: {len(df_product):,}")
    
    # Initialize data containers
    orders = []
    orderlines = []
    orderpayments = []
    invoices = []
    payments = []
    accounts = []
    
    order_id_set = set()
    order_number_counter = order_start_number
    
    print("\n🎯 Generating orders with business growth patterns..." if enable_growth else "\n🎯 Generating orders and order lines...")
    
    # Generate orders for each customer with Kitchen account
    customers_with_kitchen = df_customer[
        df_customer['CustomerID'].isin(df_kitchen_accounts['CustomerID'])
    ]
    
    # Initialize business growth tracking
    growth_stats = {
        'phase1_orders': 0, 'phase2_orders': 0, 'phase3_orders': 0,
        'market_events': {}
    }
    
    if enable_growth:
        # Month-by-month generation for visible growth patterns
        current_date = start_date.replace(day=1)
        
        for idx, customer in customers_with_kitchen.iterrows():
            if idx > 0 and idx % 50 == 0:
                print(f"   Processed {idx}/{len(customers_with_kitchen)} customers...")
            
            customer_id = customer['CustomerID']
            customer_segment = customer.get('CustomerRelationshipTypeID', 'Standard')
            customer_type = get_customer_type_from_relationship(customer_segment)
            
            # Get customer's Kitchen account
            kitchen_account = df_kitchen_accounts[df_kitchen_accounts['CustomerID'] == customer_id].iloc[0]
            account_id = kitchen_account['CustomerAccountID']
            
            # Determine base number of orders for this customer
            freq_range = SEGMENT_ORDER_FREQ.get(customer_segment, (1, 3))
            base_num_orders = random.randint(freq_range[0], freq_range[1])
            
            # Generate orders month by month for growth pattern visibility
            current_month = start_date.replace(day=1)
            while current_month <= end_date:
                next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
                month_end = min(next_month - timedelta(days=1), end_date)
                
                # Calculate business growth multiplier for this month
                month_mid = current_month + timedelta(days=15)  # Mid-month
                freq_multiplier, size_multiplier, debug_info = business_growth_logic.calculate_order_adjustments(
                    month_mid, start_date, end_date, customer_segment) if enable_growth else (1.0, 1.0, "No growth")
                
                # Calculate month frequency (orders per month)
                monthly_frequency = (base_num_orders / ((end_date - start_date).days / 30.44)) * freq_multiplier
                
                # Generate orders for this month based on frequency
                if monthly_frequency >= 1:
                    orders_this_month = int(monthly_frequency)
                    # Add chance for extra order
                    if random.random() < (monthly_frequency - orders_this_month):
                        orders_this_month += 1
                else:
                    # Low frequency - use probability
                    orders_this_month = 1 if random.random() < monthly_frequency else 0
                
                for _ in range(orders_this_month):
                    # Generate unique order ID
                    order_id = str(uuid.uuid4())
                    while order_id in order_id_set:
                        order_id = str(uuid.uuid4())
                    order_id_set.add(order_id)
                    
                    # Order details
                    order_number = f"D{order_number_counter}"
                    order_number_counter += 1
                    
                    # Random date within the month
                    days_in_month = (month_end - current_month).days + 1
                    random_day = random.randint(0, days_in_month - 1)
                    order_date = current_month + timedelta(days=random_day)
                    
                    order_status = pick_order_status()
                    payment_method = pick_payment_method()
                    
                    # Get exact multipliers for this specific date
                    if enable_growth:
                        freq_mult_exact, size_mult_exact, debug_exact = business_growth_logic.calculate_order_adjustments(
                            order_date, start_date, end_date, customer_segment)
                        
                        # Extract event name for tracking
                        event_name = business_growth_logic.get_market_event_multiplier(order_date)[0]
                        if event_name != "Normal":
                            growth_stats['market_events'][event_name] = growth_stats['market_events'].get(event_name, 0) + 1
                    else:
                        size_mult_exact = 1.0
                    
                    # Generate order lines (2-4 products per order for kitchen items - boosted for revenue)
                    base_num_lines = random.randint(2, 4)  # Increased from 1-2 to 2-4
                    num_lines = max(1, int(base_num_lines * size_mult_exact)) if enable_growth else base_num_lines
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
                        
                        # Apply size multiplier to quantity and boost revenue
                        base_quantity = random.randint(2, 4)  # Kitchen items boosted to 2-4 items
                        quantity = max(1, int(base_quantity * size_mult_exact)) if enable_growth else base_quantity
                        
                        # Apply 2x revenue multiplier for kitchen domain visibility
                        revenue_multiplier = 2.0
                        boosted_unit_price = unit_price * revenue_multiplier
                        
                        discount = calculate_discount(boosted_unit_price, customer_segment, quantity)
                        line_total = round((boosted_unit_price * quantity) - discount, 2)
                        tax = round(line_total * 0.06, 2)  # 6% sales tax rate
                        
                        subtotal += line_total
                        total_tax += tax
                        
                        orderlines.append({
                            "OrderID": order_id,
                            "OrderLineNumber": line_num,
                            "ProductID": product_id,
                            "ProductName": product_name,
                            "Quantity": quantity,
                            "UnitPrice": boosted_unit_price,  # Use boosted price
                            "LineTotal": line_total,
                            "DiscountAmount": discount,
                            "TaxAmount": tax
                        })
                    
                    order_total = round(subtotal + total_tax, 2)
                    
                    # Track phase statistics
                    if enable_growth:
                        phase, _ = business_growth_logic.calculate_business_phase(order_date, start_date, end_date)
                        if phase == 1:
                            growth_stats['phase1_orders'] += 1
                        elif phase == 2:
                            growth_stats['phase2_orders'] += 1
                        elif phase == 3:
                            growth_stats['phase3_orders'] += 1
                    
                    # Create order record
                    orders.append({
                        "OrderID": order_id,
                        "SalesChannelID": kitchen_account['CustomerAccountName'],
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
                        "InvoiceStatus": "Issued",
                        "CreatedBy": "SampleGen"
                    })
                    
                    # Create payment record (immediate payment - eCommerce model)
                    payment_id = str(uuid.uuid4())
                    payments.append({
                        "PaymentID": payment_id,
                        "InvoiceID": invoice_id,
                        "CustomerID": customer_id,
                        "PaymentDate": order_date.date(),
                        "PaymentAmount": order_total,
                        "PaymentMethod": payment_method,
                        "PaymentStatus": "Completed",
                        "CreatedBy": "SampleGen"
                    })
                
                current_month = next_month
    else:
        # Original random generation logic for non-growth mode
        for idx, customer in customers_with_kitchen.iterrows():
            if idx > 0 and idx % 50 == 0:
                print(f"   Processed {idx}/{len(customers_with_kitchen)} customers...")
            
            customer_id = customer['CustomerID']
            customer_segment = customer.get('CustomerRelationshipTypeID', 'Standard')
            customer_type = get_customer_type_from_relationship(customer_segment)
            
            # Get customer's Kitchen account
            kitchen_account = df_kitchen_accounts[df_kitchen_accounts['CustomerID'] == customer_id].iloc[0]
            account_id = kitchen_account['CustomerAccountID']
            
            # Determine number of orders for this customer
            freq_range = SEGMENT_ORDER_FREQ.get(customer_segment, (1, 3))
            num_orders = random.randint(freq_range[0], freq_range[1])
            
            for _ in range(num_orders):
                # Generate unique order ID
                order_id = str(uuid.uuid4())
                while order_id in order_id_set:
                    order_id = str(uuid.uuid4())
                order_id_set.add(order_id)
                
                # Order details
                order_number = f"D{order_number_counter}"
                order_number_counter += 1
                order_date = random_date(start_date, end_date)
                order_status = pick_order_status()
                payment_method = pick_payment_method()
                
                # Generate order lines (2-4 products per order for kitchen items - boosted for revenue)
                num_lines = random.randint(2, 4)  # Increased from 1-2 to 2-4
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
                    quantity = random.randint(2, 4)  # Kitchen items boosted to 2-4 items
                    
                    # Apply 2x revenue multiplier for kitchen domain visibility
                    revenue_multiplier = 2.0
                    boosted_unit_price = unit_price * revenue_multiplier
                    
                    discount = calculate_discount(boosted_unit_price, customer_segment, quantity)
                    line_total = round((boosted_unit_price * quantity) - discount, 2)
                    tax = round(line_total * 0.06, 2)  # 6% sales tax rate (reduced for kitchen items)
                    
                    subtotal += line_total
                    total_tax += tax
                    
                    orderlines.append({
                        "OrderID": order_id,
                        "OrderLineNumber": line_num,
                        "ProductID": product_id,
                        "ProductName": product_name,
                        "Quantity": quantity,
                        "UnitPrice": boosted_unit_price,  # Use boosted price
                        "LineTotal": line_total,
                        "DiscountAmount": discount,
                        "TaxAmount": tax
                    })
                
                order_total = round(subtotal + total_tax, 2)
                
                # Create order record
                orders.append({
                    "OrderID": order_id,
                    "SalesChannelID": kitchen_account['CustomerAccountName'],
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
                    "InvoiceStatus": "Issued",
                    "CreatedBy": "SampleGen"
                })
                
                # Create payment record (immediate payment - eCommerce model)
                payment_id = str(uuid.uuid4())
                payments.append({
                    "PaymentID": payment_id,
                    "InvoiceID": invoice_id,
                    "CustomerID": customer_id,
                    "PaymentDate": order_date.date(),
                    "PaymentAmount": order_total,
                    "PaymentMethod": payment_method,
                    "PaymentStatus": "Completed",
                    "CreatedBy": "SampleGen"
                })

    # Generate customer accounts for finance
    print("\\n🏦 Generating customer accounts for finance...")
    kitchen_customers = df_kitchen_accounts['CustomerID'].unique()
    for customer_id in kitchen_customers:
        account_id = f"ACCT-Kitchen-{customer_id}"
        accounts.append({
            "AccountID": account_id,
            "AccountNumber": f"ACC-{customer_id}-Kitchen",
            "CustomerID": customer_id,
            "AccountType": "Receivable",
            "AccountStatus": "Active",
            "CreatedDate": start_date.date(),
            "ClosedDate": "",  # Empty string for active accounts
            "Balance": 0.0,  # Zero balance since payments are immediate
            "Currency": "USD",
            "Description": f"Accounts Receivable for Customer {customer_id} - Kitchen Channel",
            "CreatedBy": "SampleGen"
        })

    print(f"\\n📊 Generation Summary:")
    print(f"   Orders: {len(orders):,}")
    print(f"   Order Lines: {len(orderlines):,}")
    print(f"   Sales Payments: {len(orderpayments):,}")
    print(f"   Invoices: {len(invoices):,}")
    print(f"   Finance Payments: {len(payments):,}")
    print(f"   Customer Accounts: {len(accounts):,}")
    
    # Show business growth analytics if enabled
    if enable_growth:
        print(f"\\n📈 Business Growth Analytics:")
        total_orders = len(orders)
        phase1_pct = (growth_stats['phase1_orders'] / total_orders * 100) if total_orders > 0 else 0
        phase2_pct = (growth_stats['phase2_orders'] / total_orders * 100) if total_orders > 0 else 0
        phase3_pct = (growth_stats['phase3_orders'] / total_orders * 100) if total_orders > 0 else 0
        
        print(f"   Phase 1 (Growth): {growth_stats['phase1_orders']:,} orders ({phase1_pct:.1f}%)")
        print(f"   Phase 2 (Decline): {growth_stats['phase2_orders']:,} orders ({phase2_pct:.1f}%)")
        print(f"   Phase 3 (Recovery): {growth_stats['phase3_orders']:,} orders ({phase3_pct:.1f}%)")
        
        if growth_stats['market_events']:
            print(f"   Market Events:")
            for event, count in growth_stats['market_events'].items():
                print(f"     {event}: {count:,} orders")
    
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
    
    print(f"\\n🎉 Kitchen product sales & finance data generation complete!")
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
    generate_kitchen_orders(start_date, end_date, args.order_start, args.enable_growth)

if __name__ == "__main__":
    # Set random seed for reproducible results
    random.seed(42)
    np.random.seed(42)
    
    main()