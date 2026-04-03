import os
import json
import random
from datetime import datetime, timedelta
import pandas as pd
from fpdf import FPDF

# Constants for rows
NUM_CUSTOMERS = 200
NUM_PRODUCTS = 50
NUM_STORES = 20
NUM_SALES = 1000
NUM_EMPLOYEES = 100
NUM_ORDERS = 200
NUM_RETURNS = 150

# Base output directory and subfolders
base_dir = r"C:/Users/gpickett/OneDrive - Microsoft/Documents/GitHub/microsoft-iq-solution-accelerator/data/20260325_163843_telecommunications"
config_dir = os.path.join(base_dir, "config")
tables_dir = os.path.join(base_dir, "tables")
documents_dir = os.path.join(base_dir, "documents")

os.makedirs(config_dir, exist_ok=True)
os.makedirs(tables_dir, exist_ok=True)
os.makedirs(documents_dir, exist_ok=True)

today = datetime.now()

# Helper functions for date generation
def recent_date(num_rows):
    dates = []
    for i in range(num_rows):
        r = random.random()
        if r < 0.3:
            days_ago = random.randint(0, 30)
        elif r < 0.6:
            days_ago = random.randint(31, 90)
        else:
            days_ago = random.randint(91, 180)
        dates.append((today - timedelta(days=days_ago)).strftime('%Y-%m-%d'))
    return dates

def recent_datetime(num_rows):
    datetimes = []
    for i in range(num_rows):
        r = random.random()
        if r < 0.3:
            days_ago = random.randint(0, 30)
        elif r < 0.6:
            days_ago = random.randint(31, 90)
        else:
            days_ago = random.randint(91, 180)
        hours_ago = random.randint(0,23)
        minutes_ago = random.randint(0,59)
        dt = today - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        datetimes.append(dt.strftime('%Y-%m-%dT%H:%M:%S'))
    return datetimes

# Generate Customers table
first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 
               'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Moore']

customer_ids = [f"CUST{str(i).zfill(4)}" for i in range(1, NUM_CUSTOMERS + 1)]
customer_names = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(NUM_CUSTOMERS)]
customer_cities = random.choices(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia'], k=NUM_CUSTOMERS)
customer_segments = random.choices(['Consumer', 'Business', 'Premium'], weights=[60,30,10], k=NUM_CUSTOMERS)
customer_signups = recent_date(NUM_CUSTOMERS)

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "name": customer_names,
    "city": customer_cities,
    "segment": customer_segments,
    "signup_date": customer_signups
})
customers.to_csv(os.path.join(tables_dir, "customers.csv"), index=False)

# Generate Products table
product_ids = [f"PROD{str(i).zfill(4)}" for i in range(1, NUM_PRODUCTS + 1)]
product_names = [f"Mobile Plan {i}" for i in range(1, NUM_PRODUCTS + 1)]
product_types = random.choices(['Prepaid', 'Postpaid', 'Data-only', 'Family Plan'], k=NUM_PRODUCTS)
monthly_fee = [round(random.uniform(20.0, 150.0),2) for _ in range(NUM_PRODUCTS)]
contract_lengths = random.choices([12,24,0], weights=[60,30,10], k=NUM_PRODUCTS)  # 0 means no contract

products = pd.DataFrame({
    "product_id": product_ids,
    "product_name": product_names,
    "type": product_types,
    "monthly_fee": monthly_fee,
    "contract_length_months": contract_lengths
})
products.to_csv(os.path.join(tables_dir, "products.csv"), index=False)

# Generate Stores table
store_ids = [f"STORE{str(i).zfill(3)}" for i in range(1, NUM_STORES + 1)]
store_cities = random.choices(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia'], k=NUM_STORES)
store_types = random.choices(['Retail', 'Outlet', 'Franchise'], weights=[70,20,10], k=NUM_STORES)
store_sizes = random.choices(['Small', 'Medium', 'Large'], weights=[30,50,20], k=NUM_STORES)

stores = pd.DataFrame({
    "store_id": store_ids,
    "city": store_cities,
    "store_type": store_types,
    "store_size": store_sizes
})
stores.to_csv(os.path.join(tables_dir, "stores.csv"), index=False)

# Generate Employees table
employee_ids = [f"EMP{str(i).zfill(4)}" for i in range(1, NUM_EMPLOYEES + 1)]
employee_names = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(NUM_EMPLOYEES)]
departments = random.choices(['Sales', 'Customer Service', 'Technical Support', 'Management'], weights=[40,30,20,10], k=NUM_EMPLOYEES)
hire_dates = recent_date(NUM_EMPLOYEES)

employees = pd.DataFrame({
    "employee_id": employee_ids,
    "name": employee_names,
    "department": departments,
    "hire_date": hire_dates
})
employees.to_csv(os.path.join(tables_dir, "employees.csv"), index=False)

# Generate Orders table
order_ids = [f"ORD{str(i).zfill(5)}" for i in range(1, NUM_ORDERS + 1)]
order_customer_ids = [random.choice(customer_ids) for _ in range(NUM_ORDERS)]
order_store_ids = [random.choice(store_ids) for _ in range(NUM_ORDERS)]
order_employee_ids = [random.choice(employee_ids) for _ in range(NUM_ORDERS)]
order_dates = recent_date(NUM_ORDERS)
order_statuses = random.choices(['Completed', 'Pending', 'Cancelled'], weights=[80,15,5], k=NUM_ORDERS)
order_total_amounts = [round(random.uniform(30.0, 400.0), 2) for _ in range(NUM_ORDERS)]

orders = pd.DataFrame({
    "order_id": order_ids,
    "customer_id": order_customer_ids,
    "store_id": order_store_ids,
    "employee_id": order_employee_ids,
    "order_date": order_dates,
    "status": order_statuses,
    "total_amount": order_total_amounts
})
orders.to_csv(os.path.join(tables_dir, "orders.csv"), index=False)

# Generate Sales Details table (line items of orders, 1000 rows)
sale_ids = [f"SALE{str(i).zfill(5)}" for i in range(1, NUM_SALES + 1)]
sale_order_ids = [random.choice(order_ids) for _ in range(NUM_SALES)]
sale_product_ids = [random.choice(product_ids) for _ in range(NUM_SALES)]
sale_quantity = [random.randint(1, 5) for _ in range(NUM_SALES)]
# Generate unit prices aligned with product monthly_fee with some random variance +/-10%
prod_fee_dict = dict(zip(products.product_id, products.monthly_fee))
sale_unit_price = [round(prod_fee_dict[sale_product_ids[i]] * random.uniform(0.9, 1.1), 2) for i in range(NUM_SALES)]

sales = pd.DataFrame({
    "sale_id": sale_ids,
    "order_id": sale_order_ids,
    "product_id": sale_product_ids,
    "quantity": sale_quantity,
    "unit_price": sale_unit_price
})
sales.to_csv(os.path.join(tables_dir, "sales.csv"), index=False)

# Generate Returns table (secondary, 150 rows, fraction of orders returned)
return_ids = [f"RET{str(i).zfill(5)}" for i in range(1, NUM_RETURNS + 1)]
return_sale_ids = random.choices(sale_ids, k=NUM_RETURNS)
return_dates = recent_date(NUM_RETURNS)
return_reasons = random.choices(['Defective', 'Customer Dissatisfaction', 'Billing Issue', 'Wrong Product'], k=NUM_RETURNS)
return_statuses = random.choices(['Processed', 'Pending', 'Rejected'], weights=[70,20,10], k=NUM_RETURNS)
# Return quantities between 1 and corresponding sale quantity (we must get sale quantity per return_sale_ids)
sale_quant_dict = dict(zip(sales.sale_id, sales.quantity))
return_quantities = []
for rid in return_sale_ids:
    max_qty = sale_quant_dict.get(rid,1)
    return_quantities.append(random.randint(1, max_qty if max_qty > 0 else 1))

returns = pd.DataFrame({
    "return_id": return_ids,
    "sale_id": return_sale_ids,
    "return_date": return_dates,
    "reason": return_reasons,
    "status": return_statuses,
    "quantity": return_quantities
})
returns.to_csv(os.path.join(tables_dir, "returns.csv"), index=False)

# Relationships
# relationships to define (5 to 7):
# orders.customer_id -> customers.customer_id
# orders.store_id -> stores.store_id
# orders.employee_id -> employees.employee_id
# sales.order_id -> orders.order_id
# sales.product_id -> products.product_id
# returns.sale_id -> sales.sale_id

config = {
    "scenario": "telecommunications",
    "name": "Retail Sales Analysis",
    "description": "Data for analyzing retail sales and operations in a telecommunications company",
    "tables": {
        "customers": {
            "columns": ["customer_id", "name", "city", "segment", "signup_date"],
            "types": {"customer_id":"String", "name":"String", "city":"String", "segment":"String", "signup_date":"Date"},
            "key": "customer_id",
            "source_table": "customers"
        },
        "products": {
            "columns": ["product_id", "product_name", "type", "monthly_fee", "contract_length_months"],
            "types": {"product_id":"String", "product_name":"String", "type":"String", "monthly_fee":"Double", "contract_length_months":"BigInt"},
            "key": "product_id",
            "source_table": "products"
        },
        "stores": {
            "columns": ["store_id", "city", "store_type", "store_size"],
            "types": {"store_id":"String", "city":"String", "store_type":"String", "store_size":"String"},
            "key": "store_id",
            "source_table": "stores"
        },
        "employees": {
            "columns": ["employee_id", "name", "department", "hire_date"],
            "types": {"employee_id":"String", "name":"String", "department":"String", "hire_date":"Date"},
            "key": "employee_id",
            "source_table": "employees"
        },
        "orders": {
            "columns": ["order_id", "customer_id", "store_id", "employee_id", "order_date", "status", "total_amount"],
            "types": {"order_id":"String", "customer_id":"String", "store_id":"String", "employee_id":"String", "order_date":"Date", "status":"String", "total_amount":"Double"},
            "key": "order_id",
            "source_table": "orders"
        },
        "sales": {
            "columns": ["sale_id", "order_id", "product_id", "quantity", "unit_price"],
            "types": {"sale_id":"String", "order_id":"String", "product_id":"String", "quantity":"BigInt", "unit_price":"Double"},
            "key": "sale_id",
            "source_table": "sales"
        },
        "returns": {
            "columns": ["return_id", "sale_id", "return_date", "reason", "status", "quantity"],
            "types": {"return_id":"String", "sale_id":"String", "return_date":"Date", "reason":"String", "status":"String", "quantity":"BigInt"},
            "key": "return_id",
            "source_table": "returns"
        }
    },
    "relationships": [
        {"name": "order_customer", "from": "orders", "to": "customers", "fromKey": "customer_id", "toKey": "customer_id"},
        {"name": "order_store", "from": "orders", "to": "stores", "fromKey": "store_id", "toKey": "store_id"},
        {"name": "order_employee", "from": "orders", "to": "employees", "fromKey": "employee_id", "toKey": "employee_id"},
        {"name": "sale_order", "from": "sales", "to": "orders", "fromKey": "order_id", "toKey": "order_id"},
        {"name": "sale_product", "from": "sales", "to": "products", "fromKey": "product_id", "toKey": "product_id"},
        {"name": "return_sale", "from": "returns", "to": "sales", "fromKey": "sale_id", "toKey": "sale_id"}
    ]
}

with open(os.path.join(config_dir, "ontology_config.json"), "w") as f:
    json.dump(config, f, indent=4)

# PDF Generation helper
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

# Policy documents with thresholds and detailed text (8 documents, 6-8 sections each, 50+ words per section)

# 1. Customer Service Policy
create_pdf("Customer Service Policy", [
    ("1. Response Time Standards",
     "All customer inquiries and complaints must be responded to within 24 hours during business "
     "days. Delays longer than this require escalation to a supervisor. Customers are prioritized "
     "based on their segment, with Premium customers receiving a faster response. Tracking and "
     "logging of response times is mandatory for quality assurance."),
    ("2. Complaint Resolution",
     "Complaints should be resolved within 5 business days whenever possible. If resolution will "
     "take longer, customers must be updated about the delay and expected resolution date. "
     "All resolutions must be documented with detailed notes, including customer feedback."),
    ("3. Escalation Procedures",
     "If an issue cannot be resolved within 72 hours, it must be escalated to the department "
     "manager. Managers are responsible for providing updates every 48 hours until resolution. "
     "Escalation levels are tracked in the support system to ensure compliance."),
    ("4. Customer Satisfaction Measurement",
     "Surveys are sent after each interaction to assess customer satisfaction. A minimum "
     "satisfaction score of 80% is expected. Scores below this trigger reviews and corrective "
     "actions. Quarterly reports are generated to monitor trends and training needs."),
    ("5. Training Requirements",
     "All customer service employees must complete mandatory training quarterly. Training includes "
     "communication skills, product knowledge, and complaint handling. Records of completed training "
     "are maintained centrally."),
    ("6. Call Quality Monitoring",
     "Random quality checks are conducted monthly. At least 85% of assessed calls must meet quality "
     "standards. Issues identified are addressed with additional coaching and re-evaluation.")
], "customer_service_policy.pdf")

# 2. Sales Operations Manual
create_pdf("Sales Operations Manual", [
    ("1. Sales Targets",
     "Each sales employee is assigned monthly sales targets based on region, product mix, and "
     "historical performance. Targets include total revenue, units sold, and new customer acquisitions. "
     "Progress is tracked weekly and reviewed in team meetings."),
    ("2. Discount Policies",
     "Discounts must not exceed 15% per customer unless approved by management. Unauthorized discounts "
     "are subject to review and possible disciplinary action. All discounts are logged in the sales system."),
    ("3. Order Processing",
     "Orders are processed within 48 hours of receipt. Delays must be reported to customers proactively. "
     "Order status updates are sent via email and SMS. Accuracy of order details is critical to avoid returns."),
    ("4. Customer Credit Checks",
     "Prior to approving postpaid plans, customer credit is evaluated. Customers with credit scores below 600 "
     "require manager approval. High risk customers may be required to pay deposits."),
    ("5. Reporting and Analysis",
     "Sales data is compiled daily to provide insights on performance trends, product popularity, and regional "
     "growth. Weekly dashboards are reviewed by management."),
    ("6. Product Promotion Guidelines",
     "Promotions are coordinated centrally and run for defined periods. All promotional offers must comply "
     "with company guidelines and legal requirements. Marketing materials require prior approval.")
], "sales_operations_manual.pdf")

# 3. Return and Refund Policy
create_pdf("Return and Refund Policy", [
    ("1. Return Eligibility",
     "Products may be returned within 30 days of purchase if unused and in original packaging. Returns "
     "must be accompanied by proof of purchase. Defective items may be returned beyond 30 days subject "
     "to inspection."),
    ("2. Refund Processing Time",
     "Approved refunds are processed within 7 business days. Customers are notified when the refund is "
     "issued. Refunds are made to the original payment method."),
    ("3. Return Reason Documentation",
     "All returns require a reason to be recorded in the system. Common reasons include defects, customer "
     "dissatisfaction, incorrect product, or billing issues. This data is analyzed monthly for quality improvements."),
    ("4. Restocking Fees",
     "Certain returns may incur a restocking fee of up to 10% if the product is damaged or not in resalable "
     "condition. Customers are informed of any fees prior to return approval."),
    ("5. Return Authorization",
     "Returns must be authorized prior to shipment. Unauthorized returns will be rejected. Authorization "
     "requests are processed within 2 business days."),
    ("6. Policy Exceptions",
     "Special exception requests are reviewed case-by-case by the returns department. Exceptions include "
     "customer service gestures or warranty claims.")
], "return_refund_policy.pdf")

# 4. Data Privacy and Security Policy
create_pdf("Data Privacy and Security Policy", [
    ("1. Customer Data Protection",
     "All customer information is stored in encrypted databases with restricted access. Access is granted "
     "only to authorized employees who have signed confidentiality agreements."),
    ("2. Data Retention",
     "Customer data is retained for a minimum of 5 years following last account activity unless otherwise required "
     "by law. Data older than this is securely deleted."),
    ("3. Access Monitoring",
     "All access to sensitive data is logged and reviewed monthly. Unauthorized access attempts trigger alerts "
     "and investigations."),
    ("4. Employee Training",
     "Employees receive annual training on data privacy laws and company policies. Compliance certifications are "
     "tracked."),
    ("5. Incident Response",
     "In case of a data breach, the incident response team must respond within 24 hours. Notification to affected "
     "customers and regulators is mandatory within 72 hours."),
    ("6. Device Security",
     "Company devices must have full disk encryption and updated antivirus software. Remote wipe capabilities are "
     "enabled for mobile devices."),
    ("7. Third-party Access",
     "Third-party service providers with data access are required to sign data processing agreements and "
     "undergo security audits.")
], "data_privacy_security_policy.pdf")

# 5. Network Maintenance Guidelines
create_pdf("Network Maintenance Guidelines", [
    ("1. Scheduled Maintenance",
     "Network maintenance windows are scheduled weekly from 1:00 AM to 4:00 AM on Sundays. Notifications are sent "
     "to affected customers 48 hours in advance."),
    ("2. Maintenance Frequency",
     "Critical network components must be serviced at least every 90 days. Logs of maintenance actions are recorded."),
    ("3. Emergency Procedures",
     "Emergency maintenance can be performed outside scheduled windows in case of outages or security threats. "
     "These require approval by the network operations manager."),
    ("4. Maintenance Documentation",
     "All maintenance activities must be documented including date, personnel, actions taken, and issues found."),
    ("5. Equipment Replacement",
     "Equipment nearing end-of-life must be replaced proactively. Replacement criteria include age above 5 years or "
     "failure rates exceeding 2% per month."),
    ("6. Quality Assurance Checks",
     "Post-maintenance testing includes uptime verification, performance benchmarking, and security scans."),
    ("7. Maintenance Team Training",
     "Network technicians must complete quarterly training on new technologies, safety standards, and troubleshooting.")
], "network_maintenance_guidelines.pdf")

# 6. Quality Control Manual
create_pdf("Quality Control Manual", [
    ("1. Inspection Standards",
     "All products undergo inspection prior to shipment. Inspectors check for defects, packaging integrity, and "
     "correct labeling. A minimum pass rate of 80% is expected."),
    ("2. Defect Reporting",
     "Defects found during inspections must be logged with severity and description. High severity defects require "
     "immediate action."),
    ("3. Continuous Improvement",
     "Quality control teams review defect data monthly to identify trends and implement corrective actions."),
    ("4. Training and Certification",
     "Inspectors complete annual certification and quarterly refresher courses. Training records are maintained."),
    ("5. Sampling Procedures",
     "Random sampling is employed with at least 10% of all shipments inspected. Sampling rates increase with quality "
     "issues."),
    ("6. Equipment Calibration",
     "All inspection equipment is calibrated biannually to ensure accuracy. Calibration logs are maintained."),
    ("7. Supplier Quality",
     "Incoming materials from suppliers are evaluated quarterly. Supplier scorecards influence ordering decisions.")
], "quality_control_manual.pdf")

# 7. Pricing and Billing Policy
create_pdf("Pricing and Billing Policy", [
    ("1. Pricing Transparency",
     "All prices listed to customers must include applicable taxes and fees unless otherwise specified. Discounts "
     "are clearly itemized."),
    ("2. Billing Cycle",
     "Customers are billed monthly with invoices generated within 5 days of the billing period end. Late payments "
     "incur a 5% surcharge."),
    ("3. Payment Methods",
     "Accepted payment methods include credit card, bank transfer, and direct debit. Payment details are secured."),
    ("4. Invoice Disputes",
     "Disputes must be raised within 30 days of invoice receipt. Disputed amounts are investigated and resolved "
     "within 15 days."),
    ("5. Price Changes",
     "Price changes require 30 days' notice to customers. Notices are sent via email and posted on the website."),
    ("6. Discounts and Promotions",
     "Promotions are controlled centrally. Unauthorized discounts are prohibited and subject to internal review."),
    ("7. Refund Processing",
     "Refunds related to billing errors are processed within 7 business days after approval.")
], "pricing_billing_policy.pdf")

# 8. Employee Conduct and Safety Manual
create_pdf("Employee Conduct and Safety Manual", [
    ("1. Workplace Conduct",
     "Employees must adhere to professional conduct standards including respect, integrity, and confidentiality. "
     "Violations may result in disciplinary action."),
    ("2. Safety Training",
     "All employees complete annual safety training covering workplace hazards, emergency procedures, and equipment use."),
    ("3. Incident Reporting",
     "Workplace incidents and near-misses must be reported within 24 hours to supervisors. Reports are logged and reviewed."),
    ("4. Personal Protective Equipment",
     "Use of PPE is mandatory in designated areas including warehouses and technical installations. PPE availability is ensured."),
    ("5. Attendance and Punctuality",
     "Employees are expected to maintain regular attendance and be punctual for shifts. Absences must be notified in advance."),
    ("6. Use of Company Property",
     "Company equipment and resources must be used responsibly and only for business purposes. Unauthorized use is prohibited."),
    ("7. Harassment Policy",
     "Harassment of any form is not tolerated. Complaints are investigated confidentially with protections against retaliation.")
], "employee_conduct_safety_manual.pdf")

# Create sample_questions.txt with 3 sections: SQL, Document, Combined Insight
questions_path = os.path.join(config_dir, "sample_questions.txt")

with open(questions_path, "w") as f:
    # SQL Questions
    f.write("=== SQL QUESTIONS (Fabric Data) ===\n")
    f.write("1. How many orders were completed in the last month across all retail stores?\n")
    f.write("2. What is the average monthly_fee for prepaid products compared to postpaid products?\n")
    f.write("3. Show total sales quantity grouped by product type for the last quarter.\n")
    f.write("4. Which customer segment had the highest total_order amount in the past six months?\n")
    f.write("5. How many returns have been processed due to defective reasons in the last 90 days?\n")
    f.write("\n")

    # Document Questions
    f.write("=== DOCUMENT QUESTIONS (AI Search) ===\n")
    f.write("1. According to the Customer Service Policy, what is the maximum allowed response time for customer inquiries?\n")
    f.write("2. What percentage discount is authorized without managerial approval in the Sales Operations Manual?\n")
    f.write("3. How long does the Return and Refund Policy allow for customers to return products?\n")
    f.write("4. What is the minimum pass rate for product inspections stated in the Quality Control Manual?\n")
    f.write("5. What is the required frequency for scheduled network maintenance according to the Network Maintenance Guidelines?\n")
    f.write("\n")

    # Combined Insight Questions
    f.write("=== COMBINED INSIGHT QUESTIONS ===\n")
    f.write("1. Are there any sales employees whose monthly revenue targets are not being met as per the Sales Operations Manual?\n")
    f.write("2. Do any customer service requests exceed the response time limits defined in the Customer Service Policy?\n")
    f.write("3. Are any product returns due to defects exceeding the acceptable threshold outlined in the Return and Refund Policy?\n")
    f.write("4. Which product types have inspection failure rates above the maximum allowed in the Quality Control Manual?\n")
    f.write("5. Are there any network maintenance events not performed within the required 90-day period based on the Network Maintenance Guidelines?\n")

print("Telecommunications retail sales data generation completed successfully.")