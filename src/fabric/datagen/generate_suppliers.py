"""
Supply Chain Data Generator - Suppliers Module

This module generates sample data for supplier-related tables:
- Suppliers: Master supplier data with backup relationships  
- ProductSuppliers: Product-supplier mappings with pricing and terms

Uses configuration from suppliers.json and existing product catalog.
Calculates realistic wholesale costs based on retail pricing patterns.
"""

import pandas as pd
import json
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import os


class SupplierDataGenerator:
    
    def __init__(self, base_path=None):
        """Initialize the supplier data generator.
        
        Args:
            base_path (str): Base path to the data_generator directory
        """
        if base_path is None:
            self.base_path = Path(__file__).parent
        else:
            self.base_path = Path(base_path)
            
        self.input_path = self.base_path / "input"
        self.output_path = self.base_path / "output"
        
        # Create output directories
        self.suppliers_output = self.output_path / "supplychain"
        self.suppliers_output.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.suppliers_config = self._load_suppliers_config()
        self.products_data = self._load_products_data()
        
        print(f"✅ Supplier generator initialized")
        print(f"📁 Input: {self.input_path}")
        print(f"📁 Output: {self.suppliers_output}")
        
    def _load_suppliers_config(self):
        """Load supplier configuration from JSON file."""
        config_file = self.input_path / "suppliers.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Suppliers config file not found: {config_file}")
            
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        print(f"📋 Loaded {len(config['suppliers'])} suppliers from config")
        return config
        
    def _load_products_data(self):
        """Load product data for supplier mappings."""
        products = {}
        
        # Load combined products if available, otherwise individual category files
        combined_file = self.input_path / "Product_Samples_Combined.csv"
        if combined_file.exists():
            df = pd.read_csv(combined_file)
            products['all'] = df
            print(f"📦 Loaded {len(df)} products from combined file")
        else:
            # Load individual category files
            for category in ['Camping', 'Kitchen', 'Ski']:
                file_path = self.input_path / f"Product_Samples_{category}.csv"
                if file_path.exists():
                    df = pd.read_csv(file_path)
                    products[category.lower()] = df
                    print(f"📦 Loaded {len(df)} {category} products")
                    
        if not products:
            raise FileNotFoundError("No product data files found in input directory")
            
        return products
        
    def generate_suppliers_table(self, start_date, end_date):
        """Generate the Suppliers table data."""
        
        suppliers_data = []
        
        for supplier in self.suppliers_config['suppliers']:
            # Add timestamp - use random date within generation period
            days_in_range = (end_date - start_date).days
            random_days = random.randint(0, max(0, days_in_range - 30))  # Keep some margin from end
            created_date = start_date + timedelta(days=random_days)
            
            supplier_record = {
                'SupplierID': supplier['SupplierID'],
                'SupplierName': supplier['SupplierName'],
                'SupplierType': supplier['SupplierType'],
                'Status': supplier['Status'],
                'ProductCategory': supplier['ProductCategory'], 
                'PrimarySupplierID': supplier['PrimarySupplierID'],
                'LeadTimeDays': supplier['LeadTimeDays'],
                'ReliabilityScore': supplier['ReliabilityScore'],
                'Location': supplier['Location'],
                'ContactEmail': supplier['ContactEmail'],
                'CreatedBy': supplier['CreatedBy'],
                'CreatedDate': created_date.strftime('%Y-%m-%d')
            }
            
            suppliers_data.append(supplier_record)
            
        df_suppliers = pd.DataFrame(suppliers_data)
        
        # Save to CSV
        output_file = self.suppliers_output / "Suppliers.csv"
        df_suppliers.to_csv(output_file, index=False)
        
        print(f"✅ Generated {len(df_suppliers)} supplier records")
        print(f"💾 Saved to: {output_file}")
        
        return df_suppliers
        
    def generate_product_suppliers_table(self, start_date, end_date):
        """Generate the ProductSuppliers mapping table."""
        
        product_supplier_data = []
        product_supplier_id = 1
        
        # Get all products from loaded data
        all_products = []
        for category, df in self.products_data.items():
            if category != 'all':  # Skip if we have combined data
                for _, product in df.iterrows():
                    all_products.append({
                        'ProductID': product.get('ProductID', product_supplier_id * 100),
                        'ProductName': product.get('ProductName', product.get('Name', f'Product {product_supplier_id}')),
                        'ProductCategory': category.title(),
                        'RetailPrice': product.get('ListPrice', product.get('Price', random.uniform(25, 500)))
                    })
            else:  # Using combined data
                for _, product in df.iterrows():
                    # Determine category from BrandName in combined file
                    brand_name = product.get('BrandName', '')
                    if 'Camping' in brand_name:
                        category = 'Camping'
                    elif 'Kitchen' in brand_name:
                        category = 'Kitchen'
                    elif 'Ski' in brand_name:
                        category = 'Ski'
                    else:
                        category = 'General'
                    
                    all_products.append({
                        'ProductID': product.get('ProductID', product_supplier_id * 100),
                        'ProductName': product.get('ProductName', product.get('Name', f'Product {product_supplier_id}')),
                        'ProductCategory': category,
                        'RetailPrice': product.get('ListPrice', product.get('Price', random.uniform(25, 500)))
                    })
                break  # Only process combined data once
                
        print(f"📦 Processing {len(all_products)} products for supplier mapping")
        
        # Create mappings for each product
        for product in all_products:
            category = product['ProductCategory'].lower()
            
            # Find suppliers for this product category
            category_suppliers = []
            for supplier in self.suppliers_config['suppliers']:
                supplier_category = supplier['ProductCategory'].lower()
                if supplier_category == 'multi' or supplier_category == category:
                    category_suppliers.append(supplier)
                    
            # Create primary supplier mapping
            primary_suppliers = [s for s in category_suppliers if s['SupplierType'] == 'Primary']
            if primary_suppliers:
                primary_supplier = primary_suppliers[0]  # Take first primary for category
                
                # Calculate wholesale cost (60-80% of retail)
                retail_price = float(product['RetailPrice'])
                wholesale_cost = retail_price * random.uniform(0.60, 0.80)
                
                # Generate supplier product code
                supplier_code = f"{primary_supplier['SupplierName'][:3].upper()}-{product['ProductID']}"
                
                record = {
                    'ProductSupplierID': product_supplier_id,
                    'ProductID': product['ProductID'],
                    'ProductName': product['ProductName'],
                    'ProductCategory': product['ProductCategory'],
                    'SupplierID': primary_supplier['SupplierID'],
                    'SupplierName': primary_supplier['SupplierName'],
                    'SupplierProductCode': supplier_code,
                    'WholesaleCost': round(wholesale_cost, 2),
                    'MinOrderQuantity': random.choice([1, 5, 10, 25, 50]),
                    'MaxOrderQuantity': random.choice([None, 1000, 5000, 10000]),
                    'LeadTimeDays': primary_supplier['LeadTimeDays'] + random.randint(-3, 3),
                    'Status': 'Active',
                    'CreatedBy': 'system',
                    'CreatedDate': (end_date - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d')
                }
                
                product_supplier_data.append(record)
                product_supplier_id += 1
                
            # Also create secondary supplier mappings (15% chance per secondary supplier)
            backup_suppliers = [s for s in category_suppliers if s['SupplierType'] == 'Secondary']
            for backup_supplier in backup_suppliers:
                if random.random() < 0.15:  # 15% chance
                    
                    # Secondary suppliers typically cost more
                    retail_price = float(product['RetailPrice'])
                    wholesale_cost = retail_price * random.uniform(0.65, 0.85)
                    
                    supplier_code = f"{backup_supplier['SupplierName'][:3].upper()}-{product['ProductID']}"
                    
                    record = {
                        'ProductSupplierID': product_supplier_id,
                        'ProductID': product['ProductID'],
                        'ProductName': product['ProductName'],
                        'ProductCategory': product['ProductCategory'],
                        'SupplierID': backup_supplier['SupplierID'],
                        'SupplierName': backup_supplier['SupplierName'],
                        'SupplierProductCode': supplier_code,
                        'WholesaleCost': round(wholesale_cost, 2),
                        'MinOrderQuantity': random.choice([1, 10, 25, 50]),
                        'MaxOrderQuantity': random.choice([None, 500, 2000, 5000]),
                        'LeadTimeDays': backup_supplier['LeadTimeDays'] + random.randint(-5, 5),
                        'Status': 'Active',
                        'CreatedBy': 'system',
                        'CreatedDate': (end_date - timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d')
                    }
                    
                    product_supplier_data.append(record)
                    product_supplier_id += 1
                    
        df_product_suppliers = pd.DataFrame(product_supplier_data)
        
        # Save to CSV
        output_file = self.suppliers_output / "ProductSuppliers.csv"
        df_product_suppliers.to_csv(output_file, index=False)
        
        print(f"✅ Generated {len(df_product_suppliers)} product-supplier mappings")
        print(f"💾 Saved to: {output_file}")
        
        return df_product_suppliers
        
    def generate_supply_chain_events_sample(self, start_date, end_date, num_events=10):
        """Generate sample supply chain events for testing."""
        
        events_data = []
        
        # Sample disruption scenarios
        event_templates = [
            {
                'DisruptionType': 'Weather',
                'EventName': 'Winter Storm Alpha',
                'Description': 'Major winter storm affecting transportation networks',
                'Severity': 'High',
                'GeographicArea': 'Northwestern USA',
                'IndustryImpact': 'Logistics'
            },
            {
                'DisruptionType': 'Supplier',
                'EventName': 'Factory Maintenance', 
                'Description': 'Scheduled maintenance at key supplier facility',
                'Severity': 'Medium',
                'GeographicArea': 'Regional',
                'IndustryImpact': 'Manufacturing'
            },
            {
                'DisruptionType': 'Economic',
                'EventName': 'Raw Material Shortage',
                'Description': 'Global shortage of key manufacturing materials',
                'Severity': 'Critical', 
                'GeographicArea': 'Global',
                'IndustryImpact': 'Manufacturing'
            }
        ]
        
        for i in range(num_events):
            template = random.choice(event_templates)
            # Generate start dates within the generation period
            days_in_range = (end_date - start_date).days
            event_start = start_date + timedelta(days=random.randint(0, max(0, days_in_range - 30)))
            
            # Some events are resolved, some ongoing
            if random.random() < 0.7:  # 70% resolved
                event_end = event_start + timedelta(days=random.randint(1, 30))
                status = 'Resolved'
                actual_duration = (event_end - event_start).days
            else:
                event_end = None
                status = random.choice(['Active', 'Monitoring'])
                actual_duration = None
                
            event = {
                'EventID': i + 1,
                'DisruptionType': template['DisruptionType'],
                'EventName': f"{template['EventName']} - {i+1}",
                'Description': template['Description'],
                'Severity': template['Severity'],
                'Status': status,
                'StartDate': event_start.strftime('%Y-%m-%d'),
                'EndDate': event_end.strftime('%Y-%m-%d') if event_end else None,
                'GeographicArea': template['GeographicArea'],
                'IndustryImpact': template['IndustryImpact'],
                'PredictedDuration': random.randint(3, 21),
                'ActualDuration': actual_duration,
                'AlertLevel': random.choice(['Yellow', 'Orange', 'Red']),
                'ReportedBy': 'Supply Chain Monitor',
                'CreatedBy': 'system',
                'CreatedDate': event_start.strftime('%Y-%m-%d'),
                'SupplierID': None,
                'ProductCategory': template.get('ProductCategory', None),
                'ImpactLevel': random.choice(['Low', 'Medium', 'High']),
                'DeliveryDelay': random.randint(1, 14),
                'CostIncrease': round(random.uniform(0, 25), 2),
                'AlternativeAction': random.choice(['Switch supplier', 'Increase safety stock', 'Expedite shipping', 'Negotiate terms', None]),
                'EstimatedRevenueImpact': round(random.uniform(1000, 500000), 2)
            }
            
            events_data.append(event)
            
        df_events = pd.DataFrame(events_data)
        
        # Save to CSV
        output_file = self.suppliers_output / "SupplyChainEvents.csv"
        df_events.to_csv(output_file, index=False)
        
        print(f"✅ Generated {len(df_events)} sample supply chain events")
        print(f"💾 Saved to: {output_file}")
        
        return df_events
        
    def generate_all_supplier_data(self, start_date, end_date, num_events=10):
        """Generate all supplier-related data tables."""
        
        print("\n🏭 Starting Supplier Data Generation...")
        print("=" * 50)
        
        # Generate each table
        df_suppliers = self.generate_suppliers_table(start_date, end_date)
        df_product_suppliers = self.generate_product_suppliers_table(start_date, end_date)
        df_events = self.generate_supply_chain_events_sample(start_date, end_date, num_events)
        
        print("\n📊 Generation Summary:")
        print(f"   Suppliers: {len(df_suppliers)} records")
        print(f"   ProductSuppliers: {len(df_product_suppliers)} records")
        print(f"   SupplyChainEvents: {len(df_events)} records")
        
        print(f"\n💾 All files saved to: {self.suppliers_output}")
        
        return {
            'suppliers': df_suppliers,
            'product_suppliers': df_product_suppliers, 
            'supply_chain_events': df_events
        }


def main():
    """Main function to run supplier data generation."""
    
    parser = argparse.ArgumentParser(description='Generate supplier data for specified date range')
    parser.add_argument('-s', '--start', type=str, required=True,
                      help='Start date in YYYY-MM-DD format (e.g., 2026-01-01)')
    parser.add_argument('-e', '--end', type=str, required=True, 
                      help='End date in YYYY-MM-DD format (e.g., 2026-03-31)')
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = datetime.strptime(args.start, '%Y-%m-%d') 
    end_date = datetime.strptime(args.end, '%Y-%m-%d')
    
    try:
        # Initialize generator
        generator = SupplierDataGenerator()
        
        # Generate all data with date range
        results = generator.generate_all_supplier_data(
            start_date=start_date, 
            end_date=end_date, 
            num_events=15
        )
        
        print(f"\n🎉 Supplier data generation completed successfully!")
        print(f"📅 Date range: {args.start} to {args.end}")
        
    except Exception as e:
        print(f"\n❌ Error during generation: {str(e)}")
        raise


if __name__ == "__main__":
    main()