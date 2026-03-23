



# Key Concepts 

## Measures

Measures are **reusable calculations** written in DAX that compute values *at query time*.
 Examples:

Total Sales

Year-over-Year Growth

Average Daily Active Users

## Calculation Groups



Calculation groups let you apply **reusable calculation patterns** (time intelligence, currency conversion, variations, etc.) **without writing dozens of separate measures**.

Each “calculation item” is like a *rule* that modifies existing measures.

Example calculation items:

- YTD
- QoQ Change
- Trailing 12 Months
- % Change vs Last Year

## Expressions

In the semantic modeling world, "expressions" often refer broadly to **DAX expressions** used in:

- Measures
- Calculated columns
- Calculation groups
- Row-level security (RLS)



## Perspectives

Perspectives are **custom views** of the model that expose only a subset of tables, columns, or measures.

They do *not* change data — only what is visible.



- Self-service analytics (keep it simple)
- Department-specific models (Finance vs Marketing)
- Hiding complexity from casual users

## Relationships

The connections between tables — usually defined by keys (e.g., CustomerID, DateKey).

Types:

- One-to-many (most common)
- Many-to-many
- One-to-one
- Inactive relationships (can be activated with DAX using `USERELATIONSHIP`)





# What You Should Do Next (The Practical Workflow)

Now that your lakehouse tables are imported:

### **1. Clean your model structure**

- Rename tables & fields (user-friendly names)
- Hide keys and technical columns (surrogate keys, audit fields)
- Mark date table(s)
- Create dimension & fact table folders if needed

### **2. Establish and validate relationships**

- Ensure your star schema is correct
- Avoid unnecessary many-to-many relationships
- Define inactive relationships for alternative contexts (e.g., order date vs ship date)

### **3. Create core business measures**

Start simple:

- Total Sales
- Total Quantity
- Distinct Customers

Then layer in:

- Ratios
- KPIs
- Time intelligence

### **4. Add calculation groups**

Recommended starter groups:

- Time Intelligence (YTD, MTD, LY, YOY)
- Variance (Absolute, Percentage)
- Currency conversion (if needed)

### **5. Build perspectives to simplify user experience**

Examples:

- Executive View
- Finance View
- Supply Chain View

### **6. Add security (optional but recommended)**

- Row-level security roles
- Object-level security (hide whole tables)