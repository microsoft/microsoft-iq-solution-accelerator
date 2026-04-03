import os
import random
import json
from datetime import datetime, timedelta
import pandas as pd
from fpdf import FPDF

# ===== Constants and Output Paths =====
OUTPUT_DIR = "C:/Users/gpickett/OneDrive - Microsoft/Documents/GitHub/microsoft-iq-solution-accelerator/data/20260325_162634_telecommunications"
config_dir = os.path.join(OUTPUT_DIR, "config")
tables_dir = os.path.join(OUTPUT_DIR, "tables")
documents_dir = os.path.join(OUTPUT_DIR, "documents")

os.makedirs(config_dir, exist_ok=True)
os.makedirs(tables_dir, exist_ok=True)
os.makedirs(documents_dir, exist_ok=True)

# ===== Row Counts =====
NUM_CUSTOMERS = 200
NUM_PRODUCTS = 50
NUM_STORES = 20
NUM_SALES = 1000
NUM_EMPLOYEES = 200
NUM_SHIPMENTS = 400
NUM_SERVICES = 50

# ===== Current Date Anchor =====
today = datetime.now()

# ===== Helper Functions =====
def random_dates(num, start_days, end_days):
    dates = []
    for _ in range(num):
        days_ago = random.randint(start_days, end_days)
        dt = today - timedelta(days=days_ago)
        dates.append(dt.strftime('%Y-%m-%d'))
    return dates

def weighted_choice(choices, weights, k):
    return random.choices(choices, weights=weights, k=k)

def create_pdf(title, sections, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    for heading, content in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, heading, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        content_ascii = content.encode('ascii', 'replace').decode('ascii')
        pdf.multi_cell(0, 6, content_ascii)
        pdf.ln(5)
    pdf.output(os.path.join(documents_dir, filename))

# ===== Generate Products Table =====
product_ids = [f'PROD{str(i).zfill(4)}' for i in range(1, NUM_PRODUCTS + 1)]
product_categories = ['Smartphones', 'Internet Plans', 'Accessories', 'TV Packages', 'VoIP Services']
products = pd.DataFrame({
    'product_id': product_ids,
    'product_name': [f'{random.choice(["Ultra", "Super", "Max", "Pro", "Basic"])} {random.choice(["Phone", "Plan", "Box", "Cord", "Service"])} {i}' for i in range(1, NUM_PRODUCTS +1)],
    'category': [product_categories[i % len(product_categories)] for i in range(NUM_PRODUCTS)],
    'price': [round(random.uniform(10.0, 1200.0), 2) for _ in range(NUM_PRODUCTS)]
})
products.to_csv(os.path.join(tables_dir, 'products.csv'), index=False)

# ===== Generate Customers Table =====
first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
               'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']

customer_ids = [f'CUST{str(i).zfill(4)}' for i in range(1, NUM_CUSTOMERS + 1)]
customers = pd.DataFrame({
    'customer_id': customer_ids,
    'name': [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(NUM_CUSTOMERS)],
    'signup_date': random_dates(NUM_CUSTOMERS, 10, 180),
    'region': random.choices(['North', 'South', 'East', 'West', 'Central'], weights=[20, 20, 20, 20, 20], k=NUM_CUSTOMERS)
})
customers.to_csv(os.path.join(tables_dir, 'customers.csv'), index=False)

# ===== Generate Stores Table =====
store_ids = [f'STORE{str(i).zfill(3)}' for i in range(1, NUM_STORES + 1)]
cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']
store_statuses = ['Open', 'Closed', 'Under Renovation']
stores = pd.DataFrame({
    'store_id': store_ids,
    'store_name': [f'{city} Store {i}' for i, city in enumerate(random.choices(cities, k=NUM_STORES), 1)],
    'city': [random.choice(cities) for _ in range(NUM_STORES)],
    'status': [store_statuses[i % 3] for i in range(NUM_STORES)],
    'open_date': random_dates(NUM_STORES, 180, 365),
})
stores.to_csv(os.path.join(tables_dir, 'stores.csv'), index=False)

# ===== Generate Employees Table =====
employee_ids = [f'EMP{str(i).zfill(4)}' for i in range(1, NUM_EMPLOYEES + 1)]
departments = ['Sales', 'Technical Support', 'Marketing', 'Operations', 'Billing']
employees = pd.DataFrame({
    'employee_id': employee_ids,
    'name': [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(NUM_EMPLOYEES)],
    'department': [departments[i % len(departments)] for i in range(NUM_EMPLOYEES)],
    'hire_date': random_dates(NUM_EMPLOYEES, 10, 180),
    'store_id': [random.choice(store_ids) for _ in range(NUM_EMPLOYEES)]
})
employees.to_csv(os.path.join(tables_dir, 'employees.csv'), index=False)

# ===== Generate Sales Table =====
sale_ids = [f'SALE{str(i).zfill(5)}' for i in range(1, NUM_SALES + 1)]

# Create order_date with distribution: 30% in last 30 days, 30% in 31-90 days ago, 40% in 91-180 days ago
order_dates = []
for _ in range(NUM_SALES):
    r = random.random()
    if r < 0.30:
        days_ago = random.randint(0, 30)
    elif r < 0.60:
        days_ago = random.randint(31, 90)
    else:
        days_ago = random.randint(91, 180)
    order_dates.append((today - timedelta(days=days_ago)).strftime('%Y-%m-%d'))

# Status with realistic distribution
sale_statuses = weighted_choice(['Completed', 'Pending', 'Cancelled'], [75, 15, 10], NUM_SALES)

products_for_sales = [random.choice(product_ids) for _ in range(NUM_SALES)]
customers_for_sales = [random.choice(customer_ids) for _ in range(NUM_SALES)]
stores_for_sales = [random.choice(store_ids) for _ in range(NUM_SALES)]
employees_for_sales = [random.choice(employee_ids) for _ in range(NUM_SALES)]

quantities = [random.randint(1, 5) for _ in range(NUM_SALES)]
# Amount calculated from product price * quantity with small random discount or markup (+/- 10%)
price_map = dict(zip(products['product_id'], products['price']))

amounts = []
for pid, qty in zip(products_for_sales, quantities):
    base = price_map[pid] * qty
    adj = base * (1 + random.uniform(-0.1, 0.1))
    amounts.append(round(adj, 2))

sales = pd.DataFrame({
    'sale_id': sale_ids,
    'order_date': order_dates,
    'status': sale_statuses,
    'product_id': products_for_sales,
    'customer_id': customers_for_sales,
    'store_id': stores_for_sales,
    'employee_id': employees_for_sales,
    'quantity': quantities,
    'amount': amounts
})
sales.to_csv(os.path.join(tables_dir, 'sales.csv'), index=False)

# ===== Generate Shipments Table =====
shipment_ids = [f'SHIP{str(i).zfill(5)}' for i in range(1, NUM_SHIPMENTS + 1)]

shipment_order_ids = random.choices(sale_ids, k=NUM_SHIPMENTS)
# Ship date always after order_date (1-14 days after)
order_date_map = dict(zip(sales['sale_id'], sales['order_date']))

ship_dates = []
for oid in shipment_order_ids:
    base_date = datetime.strptime(order_date_map[oid], '%Y-%m-%d')
    days_after = random.randint(1, 14)
    ship_dt = base_date + timedelta(days=days_after)
    # Ensure ship date not future beyond today
    if ship_dt > today:
        ship_dt = today - timedelta(days=random.randint(0,3))
    ship_dates.append(ship_dt.strftime('%Y-%m-%d'))

carriers = ['FedEx', 'UPS', 'USPS', 'DHL', 'LocalCourier']
tracking_prefixes = ['FDX', 'UPS', 'USPS', 'DHL', 'LC']

shipments = pd.DataFrame({
    'shipment_id': shipment_ids,
    'sale_id': shipment_order_ids,
    'ship_date': ship_dates,
    'carrier': [random.choice(carriers) for _ in range(NUM_SHIPMENTS)],
    'tracking_number': [f"{random.choice(tracking_prefixes)}{random.randint(10000000,99999999)}" for _ in range(NUM_SHIPMENTS)]
})
shipments.to_csv(os.path.join(tables_dir, 'shipments.csv'), index=False)

# ===== Generate Service Requests Table =====
service_ids = [f'SERVICE{str(i).zfill(4)}' for i in range(1, NUM_SERVICES + 1)]

service_types = ['Installation', 'Repair', 'Upgrade', 'Consultation']
service_statuses = ['Open', 'In Progress', 'Closed', 'Cancelled']

# Create request_date with distribution similar to sales
request_dates = []
for _ in range(NUM_SERVICES):
    r = random.random()
    if r < 0.30:
        days_ago = random.randint(0, 30)
    elif r < 0.60:
        days_ago = random.randint(31, 90)
    else:
        days_ago = random.randint(91, 180)
    request_dates.append((today - timedelta(days=days_ago)).strftime('%Y-%m-%d'))

service_product_ids = random.choices(product_ids, k=NUM_SERVICES)
service_customer_ids = random.choices(customer_ids, k=NUM_SERVICES)
service_employee_ids = random.choices(employee_ids, k=NUM_SERVICES)

# Response time in hours - 75% within 48h, 25% exceed 48h (violation)
response_times = []
for i in range(NUM_SERVICES):
    if i < int(NUM_SERVICES * 0.75):
        response_times.append(random.randint(1, 48))
    else:
        response_times.append(random.randint(49, 120))

service_requests = pd.DataFrame({
    'service_id': service_ids,
    'request_date': request_dates,
    'product_id': service_product_ids,
    'customer_id': service_customer_ids,
    'employee_id': service_employee_ids,
    'service_type': [random.choice(service_types) for _ in range(NUM_SERVICES)],
    'status': [random.choice(service_statuses) for _ in range(NUM_SERVICES)],
    'response_time_hours': response_times
})
service_requests.to_csv(os.path.join(tables_dir, 'service_requests.csv'), index=False)

# ===== Ontology Config JSON =====
config = {
    "scenario": "telecommunications",
    "name": "Telecommunications Retail Sales Analysis",
    "description": "Analyzing retail sales, service requests, shipments, employees and stores for telecom industry",
    "tables": {
        "products": {
            "columns": ["product_id", "product_name", "category", "price"],
            "types": {"product_id": "String", "product_name": "String", "category": "String", "price": "Double"},
            "key": "product_id",
            "source_table": "products"
        },
        "customers": {
            "columns": ["customer_id", "name", "signup_date", "region"],
            "types": {"customer_id": "String", "name": "String", "signup_date": "Date", "region": "String"},
            "key": "customer_id",
            "source_table": "customers"
        },
        "stores": {
            "columns": ["store_id", "store_name", "city", "status", "open_date"],
            "types": {"store_id": "String", "store_name": "String", "city": "String", "status": "String", "open_date": "Date"},
            "key": "store_id",
            "source_table": "stores"
        },
        "employees": {
            "columns": ["employee_id", "name", "department", "hire_date", "store_id"],
            "types": {"employee_id": "String", "name": "String", "department": "String", "hire_date": "Date", "store_id": "String"},
            "key": "employee_id",
            "source_table": "employees"
        },
        "sales": {
            "columns": ["sale_id", "order_date", "status", "product_id", "customer_id", "store_id", "employee_id", "quantity", "amount"],
            "types": {"sale_id": "String", "order_date": "Date", "status": "String", "product_id": "String", "customer_id": "String", "store_id": "String", "employee_id": "String", "quantity": "BigInt", "amount": "Double"},
            "key": "sale_id",
            "source_table": "sales"
        },
        "shipments": {
            "columns": ["shipment_id", "sale_id", "ship_date", "carrier", "tracking_number"],
            "types": {"shipment_id": "String", "sale_id": "String", "ship_date": "Date", "carrier": "String", "tracking_number": "String"},
            "key": "shipment_id",
            "source_table": "shipments"
        },
        "service_requests": {
            "columns": ["service_id", "request_date", "product_id", "customer_id", "employee_id", "service_type", "status", "response_time_hours"],
            "types": {"service_id": "String", "request_date": "Date", "product_id": "String", "customer_id": "String", "employee_id": "String", "service_type": "String", "status": "String", "response_time_hours": "BigInt"},
            "key": "service_id",
            "source_table": "service_requests"
        }
    },
    "relationships": [
        {"name": "sales_product", "from": "sales", "to": "products", "fromKey": "product_id", "toKey": "product_id"},
        {"name": "sales_customer", "from": "sales", "to": "customers", "fromKey": "customer_id", "toKey": "customer_id"},
        {"name": "sales_store", "from": "sales", "to": "stores", "fromKey": "store_id", "toKey": "store_id"},
        {"name": "sales_employee", "from": "sales", "to": "employees", "fromKey": "employee_id", "toKey": "employee_id"},
        {"name": "shipments_sale", "from": "shipments", "to": "sales", "fromKey": "sale_id", "toKey": "sale_id"},
        {"name": "employees_store", "from": "employees", "to": "stores", "fromKey": "store_id", "toKey": "store_id"},
        {"name": "service_requests_customer", "from": "service_requests", "to": "customers", "fromKey": "customer_id", "toKey": "customer_id"}
    ]
}

with open(os.path.join(config_dir, "ontology_config.json"), "w") as f:
    json.dump(config, f, indent=4)

# ===== Create Policy Documents (8 PDFs) =====

# 1. Retail Sales Policy
sections1 = [
    ("1. Sales Recording Accuracy",
     "All retail sales must be recorded in the system immediately upon transaction completion. Delays in recording sales beyond 24 hours are not permitted. It is critical to maintain 100 percent accuracy in sales data for inventory and revenue tracking. Any discrepancies found during audits require reporting within 48 hours and corrective actions within 7 days."),
    ("2. Pricing and Discounts",
     "Product pricing must adhere strictly to the approved price list. Discounts exceeding 15 percent require manager approval. Unauthorized discounting is subject to disciplinary action. Effective promotion dates must be accurately reflected in the system to prevent pricing conflicts."),
    ("3. Sales Return Procedures",
     "Returns must be processed within 14 days of sale date, with valid proof of purchase. Returned products must be inspected for condition and restocked if acceptable. Refunds should be authorized within 3 business days. Return rates exceeding 5 percent of total sales trigger additional review."),
    ("4. Employee Sales Performance",
     "Employees are evaluated monthly based on sales volume, customer feedback, and compliance with sales protocols. A minimum sales achievement of 80 percent of personal targets is required to maintain good standing. Failure to meet targets for three consecutive months results in performance review."),
    ("5. Customer Data Protection",
     "All customer data collected during sales must be handled confidentially. Access to customer information is restricted to authorized personnel only. Breaches of data privacy will result in immediate investigation and potential legal consequences.")
]

create_pdf("Retail Sales Policy", sections1, "retail_sales_policy.pdf")

# 2. Shipping and Delivery Guidelines
sections2 = [
    ("1. Shipment Scheduling",
     "Shipments must be scheduled within 24 hours after order confirmation. Weekend and holiday shipments require prior approvals and may incur additional fees. Delays in shipment scheduling must be reported within 12 hours."),
    ("2. Carrier Selection Criteria",
     "Preferred carriers include FedEx, UPS, USPS, DHL, and LocalCourier based on region and service type. Performance is reviewed quarterly. Carrier failure rate must not exceed 3 percent. Alternate carriers may be approved for special circumstances."),
    ("3. Tracking and Notifications",
     "All shipments must include valid tracking numbers accessible to customers. Notification emails regarding shipment status must be sent within 2 hours of shipment dispatch."),
    ("4. Delivery Time Standards",
     "Standard delivery timeframes are within 5 business days for domestic shipments. Expedited options are available for additional cost. Delivery delays beyond 7 business days require automatic escalation and customer notification."),
    ("5. Damaged or Lost Shipments",
     "Any damaged or lost shipments must be reported within 24 hours of discovery. Investigation must be completed within 10 business days. Compensation policies apply according to shipment insurance coverage.")
]

create_pdf("Shipping and Delivery Guidelines", sections2, "shipping_delivery_guidelines.pdf")

# 3. Employee Conduct and Performance Standards
sections3 = [
    ("1. Code of Conduct",
     "All employees are expected to maintain professionalism, integrity, and respect in the workplace. Violations including harassment, discrimination or misconduct will be subject to disciplinary actions up to termination."),
    ("2. Sales Target Requirements",
     "Employees must meet monthly sales targets based on assigned store locations and roles. Minimum target achievement is set at 80 percent. Continued underperformance triggers coaching and potential reassignment."),
    ("3. Training and Certification",
     "Completion of product and customer service training is mandatory within the first 30 days of employment. Certification renewal is required annually. Failure to complete training may affect employment status."),
    ("4. Attendance and Punctuality",
     "Regular attendance and punctuality are mandatory. Absences must be reported in advance where possible. Excessive tardiness or unexcused absences affect performance evaluations."),
    ("5. Data Security Compliance",
     "Employees must comply with all data security policies. Unauthorized access or sharing of sensitive information is prohibited and may result in legal consequences.")
]

create_pdf("Employee Conduct and Performance Standards", sections3, "employee_conduct_performance.pdf")

# 4. Customer Service and Support Procedures
sections4 = [
    ("1. Service Request Handling",
     "All service requests must be acknowledged within 4 hours. Resolution targets vary by request type. Repair requests should be resolved within 72 hours. Open requests exceeding 7 days require escalation."),
    ("2. Response Time Expectations",
     "The maximum allowable response time for customer inquiries is 48 hours. Delays must be communicated proactively. Exceeding response standards will be tracked and reviewed monthly."),
    ("3. Customer Feedback Management",
     "Feedback must be logged and reviewed weekly. Negative feedback triggers a follow-up within 24 hours. Trends in complaints require monthly reporting and corrective action."),
    ("4. Service Quality Standards",
     "Service delivery must meet defined quality metrics including accuracy, professionalism, and timeliness. Minimum customer satisfaction rating target is 85 percent."),
    ("5. Escalation Pathways",
     "Escalation procedures must be followed for unresolved issues after 48 hours. Contact hierarchy includes frontline support, supervisors, and managers. Documentation of escalations is mandatory.")
]

create_pdf("Customer Service and Support Procedures", sections4, "customer_service_support.pdf")

# 5. Product Quality and Maintenance Guidelines
sections5 = [
    ("1. Product Quality Assurance",
     "Products must comply with industry standards and internal quality benchmarks prior to release. Quality audits are conducted monthly. Defect rates must remain below 2 percent."),
    ("2. Maintenance Scheduling",
     "Equipment maintenance must occur every 90 days. Maintenance logs must be updated immediately after service. Overdue maintenance triggers alerts and review."),
    ("3. Fault Reporting Procedures",
     "All faults must be reported within 24 hours of detection. Faults affecting service delivery require immediate escalation."),
    ("4. Replacement and Repair Policies",
     "Defective products are eligible for repair or replacement within warranty periods. Claims must be processed within 7 days."),
    ("5. Documentation and Traceability",
     "Maintenance and quality check records must be stored with clear traceability. Records are subject to periodic audits.")
]

create_pdf("Product Quality and Maintenance Guidelines", sections5, "product_quality_maintenance.pdf")

# 6. Data Privacy and Security Policy
sections6 = [
    ("1. Customer Data Handling",
     "Customer data is confidential and access is strictly limited to authorized personnel only. Data must be encrypted at rest and in transit."),
    ("2. Access Controls",
     "Role-based access control policies enforce permissions. Unauthorized access attempts are logged and investigated."),
    ("3. Incident Reporting",
     "Security incidents must be reported within 2 hours to the security team. Response plans are activated immediately."),
    ("4. Employee Responsibilities",
     "All employees must complete annual data privacy training. Non-compliance results in disciplinary action."),
    ("5. Data Retention and Disposal",
     "Customer data retention follows legal and regulatory requirements. Secure data disposal methods must be used for obsolete data.")
]

create_pdf("Data Privacy and Security Policy", sections6, "data_privacy_security.pdf")

# 7. Sales and Service Compliance Manual
sections7 = [
    ("1. Regulatory Compliance",
     "All sales and service activities must comply with telecommunications regulations. Non-compliance may result in penalties or license suspension."),
    ("2. Documentation Requirements",
     "Proper documentation for all transactions is mandatory for auditability. Missing documentation triggers review and corrective action."),
    ("3. Compliance Training",
     "Employees must complete compliance training annually. Training covers data handling, fair sales practices, and customer rights."),
    ("4. Monitoring and Auditing",
     "Regular audits assess compliance adherence. Audit results are reviewed quarterly with management."),
    ("5. Non-Compliance Consequences",
     "Violations of compliance requirements lead to disciplinary actions including retraining, suspension, or termination.")
]

create_pdf("Sales and Service Compliance Manual", sections7, "sales_service_compliance.pdf")

# 8. Equipment and Network Maintenance Procedures
sections8 = [
    ("1. Network Equipment Checks",
     "Network equipment must be inspected every 90 days with thorough checks on performance and security. Logs must be updated with all findings."),
    ("2. Scheduled Downtime Notifications",
     "Scheduled maintenance and downtime must be communicated to affected customers at least 48 hours in advance."),
    ("3. Incident Response Times",
     "Network incidents require initial response within 2 hours and resolution within 24 hours where possible."),
    ("4. Maintenance Personnel Responsibilities",
     "Technicians are responsible for following checklists and documenting all maintenance tasks accurately."),
    ("5. Equipment Replacement Criteria",
     "Equipment reaching end-of-life or with repeated failures must be replaced promptly according to inventory protocols.")
]

create_pdf("Equipment and Network Maintenance Procedures", sections8, "equipment_network_maintenance.pdf")

# ===== Sample Questions =====
with open(os.path.join(config_dir, "sample_questions.txt"), "w") as f:
    f.write("=== SQL QUESTIONS (Fabric Data) ===\n")
    f.write("1. How many sales were recorded as 'Completed' in the last month?\n")
    f.write("2. What is the average response time in hours for service requests currently 'Open' or 'In Progress'?\n")
    f.write("3. Show total sales amount grouped by product category over the past 6 months.\n")
    f.write("4. Which store has generated the highest total sales revenue in the last quarter?\n")
    f.write("5. How many shipments were delayed beyond 7 days from the order date?\n")
    f.write("\n")
    f.write("=== DOCUMENT QUESTIONS (AI Search) ===\n")
    f.write("1. According to the Retail Sales Policy, what is the maximum allowed discount without manager approval?\n")
    f.write("2. What are the standard delivery time expectations detailed in the Shipping and Delivery Guidelines?\n")
    f.write("3. What is the required response time for customer service requests per the Customer Service and Support Procedures?\n")
    f.write("4. What minimum sales target achievement is expected from employees in the Employee Conduct and Performance Standards?\n")
    f.write("5. What is the maintenance interval for network equipment described in the Equipment and Network Maintenance Procedures?\n")
    f.write("\n")
    f.write("=== COMBINED INSIGHT QUESTIONS ===\n")
    f.write("1. Are there service requests with response times exceeding the limits defined in the Customer Service and Support Procedures?\n")
    f.write("2. Do any stores have sales revenue below the minimum sales targets set in the Employee Conduct and Performance Standards?\n")
    f.write("3. Are there shipments that violated the delivery time standards outlined in the Shipping and Delivery Guidelines?\n")
    f.write("4. What percentage of product returns exceed the acceptable defect rates mentioned in the Product Quality and Maintenance Guidelines?\n")
    f.write("5. How does the average sales discount applied compare with the authorized discount limits defined in the Retail Sales Policy?\n")

print("Telecommunications retail-sales-analysis data generation complete.")