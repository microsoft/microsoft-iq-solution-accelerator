#!/usr/bin/env python3
"""
Camping Product Data Generator - Microsoft camping Channel
=========================================================

Generates realistic sales & finance data for camping products:
🏕️  Seasonal product preferences (tents in spring, winter gear in fall/winter)
👥 Customer segmentation (Standard, Premium, VIP, Partner, Government)  
💰 Simplified pricing (no discounts)
📈 Business growth patterns enabled (3-phase growth simulation)

Usage:
  python generate_camping_orders.py -s 2025-01-01 -e 2025-12-31
  python generate_camping_orders.py --enable-growth  # Enable growth patterns

Outputs 6 CSV files:
Sales: Order, OrderLine, OrderPayment → sales/camping/
Finance: Invoice, Payment, Account → finance/camping/

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

# Import business growth logic
from business_growth_logic import calculate_order_adjustments

# Configuration
BASE_DIR = Path(__file__).parent.absolute()
INPUT_DIR = BASE_DIR / "input"
SALES_OUTPUT_DIR = BASE_DIR / "output" / "sales" / "camping"
FINANCE_OUTPUT_DIR = BASE_DIR / "output" / "finance" / "camping"

# Input file paths
CUSTOMER_FILE = INPUT_DIR / "Customer_Samples.csv"
ACCOUNT_FILE = INPUT_DIR / "CustomerAccount_Samples.csv"
PRODUCT_FILE = INPUT_DIR / "Product_Samples_Camping.csv"
LOCATION_FILE = INPUT_DIR / "Location_Samples.csv"

# Sales output file paths
ORDER_FILE = SALES_OUTPUT_DIR / "Order_Samples_Camping.csv"
ORDERLINE_FILE = SALES_OUTPUT_DIR / "OrderLine_Samples_Camping.csv"
ORDERPAYMENT_FILE = SALES_OUTPUT_DIR / "OrderPayment_Camping.csv"

# Finance output file paths
INVOICE_FILE = FINANCE_OUTPUT_DIR / "Invoice_Samples_Camping.csv"
PAYMENT_FILE = FINANCE_OUTPUT_DIR / "Payment_Samples_Camping.csv"
ACCOUNT_FIN_FILE = FINANCE_OUTPUT_DIR / "Account_Samples_Camping.csv"

# Data generation parameters
# Remove default dates - require user to specify
# DEFAULT_START_DATE = datetime(2020, 1, 1)
# DEFAULT_END_DATE = datetime(2026, 1, 12)  # Default end date
ORDER_NUMBER_START = 100000

# Customer hierarchy structure matching schema
CUSTOMER_HIERARCHY = {
    'Individual': {
        'Standard': (1, 2),   # 1-2 orders
        'Premium': (2, 4),    # 2-4 orders
        'VIP': (3, 8)         # 3-8 orders
    },
    'Business': {
        'SMB': (2, 5),        # Small/Medium Business: 2-5 orders
        'Premier': (4, 10),   # Premier Business: 4-10 orders
        'Partner': (5, 12)    # Partner Business: 5-12 orders (highest)
    },
    'Government': {
        'Federal': (1, 3),    # Federal Government: 1-3 orders
        'State': (1, 2),      # State Government: 1-2 orders
        'Local': (1, 2)       # Local Government: 1-2 orders
    }
}

# Flatten hierarchy for backwards compatibility and easier selection
SEGMENT_ORDER_FREQ = {}
for customer_type, relationships in CUSTOMER_HIERARCHY.items():
    for relationship_type, freq_range in relationships.items():
        SEGMENT_ORDER_FREQ[relationship_type] = freq_range

# Camping product preferences by season (ProductCategoryID weightings)
SEASONAL_PREFERENCES = {
    "spring": {151: 0.3, 152: 0.2, 153: 0.15, 154: 0.15, 155: 0.1, 156: 0.05, 157: 0.03, 158: 0.02},  # Tents higher
    "summer": {151: 0.25, 152: 0.25, 153: 0.1, 154: 0.1, 155: 0.15, 156: 0.1, 157: 0.03, 158: 0.02}, # Backpacks, tables higher
    "fall": {151: 0.2, 152: 0.2, 153: 0.2, 154: 0.15, 155: 0.05, 156: 0.05, 157: 0.1, 158: 0.05},   # Clothing higher
    "winter": {151: 0.15, 152: 0.15, 153: 0.25, 154: 0.15, 155: 0.05, 156: 0.05, 157: 0.15, 158: 0.05} # Clothing, sleeping bags
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
        description='Generate Camping Product Orders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Examples:
  python generate_camping_orders.py                    # Full date range
  python generate_camping_orders.py -s 2025-01-01     # From 2025
  python generate_camping_orders.py -s 2024-06-01 -e 2024-12-31
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
    """Determine season from date for seasonal product preferences"""
    month = date.month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"

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
    """Select products based on seasonal camping preferences"""
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

def generate_camping_orders(start_date, end_date, order_start_number, enable_growth=False):
    """Generate camping product orders"""
    
    print("🏕️ Generating Camping Product Orders")
    print("=" * 64)
    print(f"📅 Date Range: {start_date.date()} to {end_date.date()}")
    print(f"📊 Order Number Start: F{order_start_number}")
    
    # Create output directories
    SALES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FINANCE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load input data
    print("\n📂 Loading input data...")
    df_customer = pd.read_csv(CUSTOMER_FILE)
    df_account = pd.read_csv(ACCOUNT_FILE)
    df_product = pd.read_csv(PRODUCT_FILE)
    
    # Filter accounts to Camping channel only
    df_camping_accounts = df_account[df_account['CustomerAccountName'] == 'Camping'].copy()
    
    print(f"   Customers: {len(df_customer):,}")
    print(f"   Camping Accounts: {len(df_camping_accounts):,}")
    print(f"   Camping Products: {len(df_product):,}")
    
    # Initialize data containers
    orders = []
    orderlines = []
    orderpayments = []
    
    # Finance data containers
    invoices = []
    payments = []
    accounts = []
    
    order_id_set = set()
    order_number_counter = order_start_number
    
    print("\n🎯 Generating orders with business growth patterns...")
    
    # Track business growth metrics for summary
    phase_orders = {1: 0, 2: 0, 3: 0}
    event_orders = {}
    
    # Generate orders for each customer with Camping account
    customers_with_camping = df_customer[
        df_customer['CustomerID'].isin(df_camping_accounts['CustomerID'])
    ]
    
    for idx, customer in customers_with_camping.iterrows():
        if idx > 0 and idx % 50 == 0:
            print(f"   Processed {idx}/{len(customers_with_camping)} customers...")
        
        customer_id = customer['CustomerID']
        customer_segment = customer.get('CustomerRelationshipTypeID', 'Standard')
        customer_type = get_customer_type_from_relationship(customer_segment)
        
        # Get customer's Camping account
        camping_account = df_camping_accounts[df_camping_accounts['CustomerID'] == customer_id].iloc[0]
        account_id = camping_account['CustomerAccountID']
        
        # Determine number of orders for this customer with business growth patterns
        freq_range = SEGMENT_ORDER_FREQ.get(customer_segment, (1, 2))
        base_num_orders = random.randint(freq_range[0], freq_range[1])
        
        # Generate orders with dates spread across the period
        order_dates = []
        
        if enable_growth:
            # Business growth logic enabled - Generate orders month by month for proper growth scaling
            # This ensures each month gets the correct number of orders based on its growth multiplier
            from business_growth_logic import calculate_business_phase, get_market_event_multiplier
            
            # Calculate months in the period
            current_month = start_date.replace(day=1)
            end_month = end_date.replace(day=1)
            
            while current_month <= end_month:
                # Calculate next month boundary
                if current_month.month == 12:
                    next_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    next_month = current_month.replace(month=current_month.month + 1)
                
                # Month boundaries for this iteration
                month_start = max(current_month, start_date)
                month_end = min(next_month - timedelta(days=1), end_date)
                
                # Get multiplier for middle of month to represent the month's growth level
                month_mid = month_start + (month_end - month_start) / 2
                freq_multiplier, size_multiplier, debug_info = calculate_order_adjustments(
                    month_mid, start_date, end_date, customer_segment
                )
                
                # Calculate orders for this month based on growth multiplier
                # Base orders per month (spread across year)
                base_monthly = base_num_orders / 12.0  
                # Apply frequency multiplier to get actual orders for this month
                monthly_orders = max(1, int(base_monthly * freq_multiplier))
                
                # Generate the orders for this month
                for i in range(monthly_orders):
                    # Random date within the month
                    days_in_month = (month_end - month_start).days + 1
                    day_offset = random.randint(0, days_in_month - 1)
                    order_date = month_start + timedelta(days=day_offset)
                    
                    # Get exact multipliers for this specific date
                    freq_mult_exact, size_mult_exact, debug_exact = calculate_order_adjustments(
                        order_date, start_date, end_date, customer_segment
                    )
                    
                    order_dates.append((order_date, size_mult_exact, debug_exact))
                    
                    # Track phase for analytics
                    phase, _ = calculate_business_phase(order_date, start_date, end_date)
                    phase_orders[phase] = phase_orders.get(phase, 0) + 1
                    
                    # Track events
                    event_name, _, _ = get_market_event_multiplier(order_date)
                    if event_name != "Normal":
                        event_orders[event_name] = event_orders.get(event_name, 0) + 1
                
                # Move to next month
                current_month = next_month
        else:
            # Original logic - simple random order generation
            for _ in range(base_num_orders):
                order_date = random_date(start_date, end_date)
                order_dates.append((order_date, 1.0, "Original Logic"))  # Default size multiplier
        
        # Sort orders by date
        order_dates.sort(key=lambda x: x[0])
        
        for order_date, size_multiplier, debug_info in order_dates:
            # Generate unique order ID
            order_id = str(uuid.uuid4())
            while order_id in order_id_set:
                order_id = str(uuid.uuid4())
            order_id_set.add(order_id)
            
            # Order details
            order_number = f"F{order_number_counter}"
            order_number_counter += 1
            order_status = pick_order_status()
            payment_method = pick_payment_method()
            
            # Generate order lines with business growth affecting order size
            base_num_lines = random.randint(1, 4)  # Base camping gear order size
            # Apply size multiplier from business growth
            adjusted_num_lines = max(1, int(base_num_lines * size_multiplier))
            selected_products = select_products_by_season(df_product, order_date, adjusted_num_lines)
            
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
                base_unit_price = float(prod_data['ListPrice'])
                
                # Apply business growth to quantities (more aggressive scaling)
                base_quantity = random.randint(1, 3)  # Camping gear typically 1-3 items
                adjusted_quantity = max(1, int(base_quantity * size_multiplier))
                
                # Apply business growth to unit prices during high-growth phases
                # High-growth phases can support premium pricing
                unit_price = base_unit_price
                if size_multiplier > 1.2:  # Growth phase premium pricing
                    price_premium = min(1.3, 1.0 + (size_multiplier - 1.0) * 0.5)
                    unit_price = round(base_unit_price * price_premium, 2)
                elif size_multiplier < 0.9:  # Decline phase discounting
                    price_discount = max(0.8, size_multiplier)
                    unit_price = round(base_unit_price * price_discount, 2)
                
                quantity = adjusted_quantity
                
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
                "SalesChannelID": camping_account['CustomerAccountName'],
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
            
            # Generate Finance Data (Invoice + Payment)
            # eCommerce logic: Order -> Invoice (next day) -> Payment (immediate)
            invoice_id = str(uuid.uuid4())
            invoice_number = f"IN-{order_number}"
            invoice_date = order_date.date() + timedelta(days=1)  # Invoice day after order
            
            # Create invoice record
            invoices.append({
                "InvoiceID": invoice_id,
                "InvoiceNumber": invoice_number,
                "CustomerID": customer_id,
                "OrderID": order_id,
                "InvoiceDate": invoice_date,
                "DueDate": invoice_date,  # eCommerce: immediate payment
                "SubTotal": round(subtotal, 2),
                "TaxAmount": round(total_tax, 2),
                "TotalAmount": order_total,
                "InvoiceStatus": "Issued",
                "CreatedBy": "SampleGen"
            })
            
            # Create finance payment record (follows CSV structure, not schema)
            payments.append({
                "PaymentID": str(uuid.uuid4()),
                "InvoiceID": invoice_id,
                "CustomerID": customer_id,
                "PaymentDate": invoice_date,  # eCommerce: immediate payment
                "PaymentAmount": order_total,
                "PaymentMethod": payment_method,
                "PaymentStatus": "Completed",
                "CreatedBy": "SampleGen"
            })
    
    # Generate Customer Accounts for Finance
    print(f"\\n🏦 Generating customer accounts for finance...")
    account_counter = 1000  # Start numbering from 1000
    
    for customer in customers_with_camping.itertuples():
        customer_id = customer.CustomerID
        
        accounts.append({
            "AccountID": str(uuid.uuid4()),
            "AccountNumber": f"ACC-Camping-{account_counter}",
            "CustomerID": customer_id,
            "AccountType": "Receivable",
            "AccountStatus": "Active",
            "CreatedDate": start_date.date(),
            "ClosedDate": "",  # Empty for active accounts
            "Balance": 0.0,  # eCommerce: immediate payment, no balance
            "Currency": "USD",
            "Description": f"Customer receivable account (Camping)",
            "CreatedBy": "SampleGen"
        })
        account_counter += 1
    
    print(f"\n📊 Generation Summary:")
    print(f"   Orders: {len(orders):,}")
    print(f"   Order Lines: {len(orderlines):,}")
    print(f"   Sales Payments: {len(orderpayments):,}")
    print(f"   Invoices: {len(invoices):,}")
    print(f"   Finance Payments: {len(payments):,}")
    print(f"   Customer Accounts: {len(accounts):,}")
    
    # Business Growth Analytics (only show if enabled)
    if enable_growth:
        print(f"\n📈 Business Growth Analytics:")
        total_phase_orders = sum(phase_orders.values())
        if total_phase_orders > 0:
            print(f"   Phase 1 (Growth): {phase_orders.get(1, 0):,} orders ({phase_orders.get(1, 0)/total_phase_orders*100:.1f}%)")
            print(f"   Phase 2 (Decline): {phase_orders.get(2, 0):,} orders ({phase_orders.get(2, 0)/total_phase_orders*100:.1f}%)")
            print(f"   Phase 3 (Recovery): {phase_orders.get(3, 0):,} orders ({phase_orders.get(3, 0)/total_phase_orders*100:.1f}%)")
        
        if event_orders:
            print(f"   Market Events:")
            for event, count in event_orders.items():
                print(f"     {event}: {count:,} orders")
        else:
            print(f"   Market Events: None detected in this period")
    
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
    
    print(f"\\n🎉 Camping product sales & finance data generation complete!")
    print(f"   Sales output: {SALES_OUTPUT_DIR}")
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
    generate_camping_orders(start_date, end_date, args.order_start)

if __name__ == "__main__":
    # Set random seed for reproducible results
    random.seed(42)
    np.random.seed(42)
    
    main()