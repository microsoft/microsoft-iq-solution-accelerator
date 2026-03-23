Based on general knowledge, you can build a semantic model from your Lakehouse in a few ways—here are the two most common, step-by-step.

**Option A — Build directly in Fabric (fastest to keep everything in the service)**

- In your Fabric workspace, create a new semantic model and choose Lakehouse as the source.
- Select your Lakehouse, then pick the schema/tables you want.
- Confirm relationships (star schema if possible), set column data types and formatting, and add basic measures.
- Save the semantic model to your workspace.

**Option B — Build in Power BI Desktop using Direct Lake**

- In Power BI Desktop, Get Data → OneLake data hub (or Lakehouse).
- Select your Lakehouse and choose the tables. If eligible, this uses Direct Lake (near real-time, no refresh required).
- Model your relationships, create measures, organize fields.
- Publish to your Fabric workspace; this creates the semantic model there.

Alternative — Use the SQL analytics endpoint (DirectQuery/Import)

- Connect from Power BI Desktop using the SQL analytics endpoint for your Lakehouse.
- Choose DirectQuery (live) or Import (cached) based on performance/latency needs.
- Model, then publish.

Quick modeling checklist

- Create a proper Date table and mark it as Date; turn off Auto Date/Time.
- Use measures for business logic; avoid calculated columns unless necessary.
- Hide keys/technical columns; organize fields into display folders.
- Validate relationships (one-to-many, single direction) and cardinality.
- Set data categories (e.g., geographic, URLs) and format strings.

Would you prefer to build this in Fabric web or in Power BI Desktop? If you tell me which Lakehouse you’re targeting and your preferred mode (Direct Lake, DirectQuery, or Import), I can tailor the exact steps.