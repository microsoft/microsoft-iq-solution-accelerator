# 📅 Sample Data Refresh Notebooks

Two simplified, self-contained Fabric notebooks for managing sample data dates in `miqsadata` Lakehouse.

## 📦 What's Included

| Notebook | Purpose | When to Run |
|----------|---------|------------|
| **01_sample_data_initial_refresh.ipynb** | One-time setup that shifts all business dates forward by the calculated delta | **Once** after loading sample data into Lakehouse |
| **02_sample_data_daily_refresh.ipynb** | Daily incremental refresh (shift by 1 day each run) for automated scheduling | **Daily** as a Fabric pipeline job |

---

## 🎯 Quick Start

### Step 1: Run Notebook 01 (Initial Setup)

1. Open **`01_sample_data_initial_refresh.ipynb`** in Fabric Notebooks
2. Review the **PARAMETERS** section (cell 2):
   - `BASE_DATE` — Fixed anchor date (default: `2026-04-30`). **Do NOT change after initial run.**
   - `DRY_RUN` — Set to `True` to preview changes without writing
   - Other settings typically don't need changes
3. Click **Run all cells**
4. Wait for completion — you'll see a summary with results

**Expected output:**
```
📊 EXECUTION SUMMARY — Notebook 01 Initial Refresh
================================
✅ Successful  : 22
❌ Failed      : 0
⏭️  Skipped     : 0
📦 Total Rows  : 450,000+
================================
```

### Step 2: Schedule Notebook 02 (Daily Refresh)

1. Open **`02_sample_data_daily_refresh.ipynb`**
2. Verify `BASE_DATE` matches what you used in Notebook 01 (should be identical)
3. In Fabric, create a **Pipeline Job** to run this notebook daily:
   - Recommended time: **2:00 AM UTC** (adjust to your timezone)
   - Trigger: **Daily**

**The notebook will:**
- ✅ Check if it already ran today — if yes, exit cleanly (no duplicate shifts)
- ✅ Calculate incremental shift (always 1 day)
- ✅ Apply the shift to all eligible columns
- ✅ Log the execution

---

## ⚙️ Configuration

### What Gets Updated?

**22 columns across 5 schemas:**

| Schema | Tables | Example Columns |
|--------|--------|-----------------|
| `sales` | Order | OrderDate |
| `finance` | invoice, payment | InvoiceDate, DueDate, PaymentDate |
| `inventory` | InventoryTransactions, Inventory, PurchaseOrders, PurchaseOrderItems, DemandForecast | TransactionDate, OrderDate, ForecastDate |
| `supplychain` | SupplyChainEvents, SupplyChainEventImpacts | StartDate, EndDate |
| `product` | Product | SellStartDate, SellEndDate |

### What Gets Excluded?

**Sensitive columns are NEVER touched:**
- `DateOfBirth`, `DOB` (customer data)
- `CreatedDate`, `UpdatedDate` from protected tables
- `DimDate` calendar table
- Any column you add to `EXCLUDE_CONFIG`

To customize, edit **EXCLUDE_CONFIG** (cell 4 in each notebook).

---

## 🔒 Safety Features

✅ **NULL Preservation** — NULL dates are never shifted  
✅ **Pre/Post Validation** — Every column is validated before and after update  
✅ **Idempotent** — Notebook 02 is safe to re-run (checks if it already ran today)  
✅ **Dry-Run Mode** — Set `DRY_RUN = True` to preview changes  
✅ **Execution Logging** — All runs logged to `default.date_refresh_execution_log`  
✅ **Guard Clauses** — Skips missing tables/columns gracefully  

---

## 📊 Monitoring & Auditing

### Check Execution History

Query the execution log to see all runs:

```sql
SELECT * FROM default.date_refresh_execution_log
ORDER BY run_date DESC;
```

### Check Latest Run for Notebook 02

```sql
SELECT 
    run_id, 
    run_date, 
    COUNT(*) as columns_updated, 
    SUM(rows_affected) as total_rows_updated
FROM default.date_refresh_execution_log
WHERE notebook = 'notebook_02_daily'
GROUP BY run_id, run_date
ORDER BY run_date DESC
LIMIT 10;
```

### View Success/Failure Stats

```sql
SELECT 
    DATE(run_date) as run_date,
    notebook,
    status,
    COUNT(*) as count
FROM default.date_refresh_execution_log
GROUP BY DATE(run_date), notebook, status
ORDER BY run_date DESC;
```

---

## 🚨 Troubleshooting

### Issue: `Delta is non-positive`

**Cause:** Today's date is not after `BASE_DATE`

**Fix:** Check that `BASE_DATE` is set correctly (should be before today)

```python
BASE_DATE = "2026-04-30"  # Example — adjust to your needs
```

### Issue: `Table not found` messages

**Cause:** One or more tables in `INCLUDE_CONFIG` don't exist in your Lakehouse

**Fix:** Either:
1. Create the missing table, OR
2. Remove it from `INCLUDE_CONFIG` (cell 4)

### Issue: `Column not found` messages

**Cause:** One or more columns listed in `INCLUDE_CONFIG` don't exist

**Fix:** Verify column names (case-sensitive) and remove non-existent columns from the config

### Issue: Notebook 02 exits immediately with "Already refreshed today"

**This is expected behavior.** The notebook uses idempotency checks to prevent duplicate shifts on the same day.

To force a re-run (use with care):
```python
FORCE_RUN = True  # Only if you need to re-run on the same day
```

---

## 📋 Configuration Reference

### Cell 2 — Parameters

```python
BASE_DATE = "2026-04-30"   # Fixed anchor — never change after initial setup
DRY_RUN   = False          # True = preview only, no writes
FORCE_RUN = False          # True = bypass idempotency check (Notebook 02 only)
```

### Cell 4 — INCLUDE_CONFIG

Define which (schema, table, column) tuples to update:

```python
INCLUDE_CONFIG = {
    "sales": {
        "Order": ["OrderDate"],
    },
    "finance": {
        "invoice": ["InvoiceDate", "DueDate"],
        # Add more tables and columns as needed
    },
    # ... more schemas
}
```

### Cell 4 — EXCLUDE_CONFIG

Define columns that must NEVER be touched (safety override):

```python
EXCLUDE_CONFIG = {
    "customer": {
        "Customer": ["DateOfBirth", "CustomerEstablishedDate"],
    },
    # ... more schemas and columns
}
```

---

## 🔄 How It Works

### Notebook 01: One-Time Initial Refresh

```
1. Calculate delta = today - BASE_DATE
2. Validate delta > 0
3. Capture pre-update stats (min/max/null for each column)
4. For each eligible column:
   - UPDATE table SET column = DATE_ADD(column, delta) WHERE column IS NOT NULL
5. Validate post-update stats
6. Log all operations to default.date_refresh_execution_log
7. Display summary report
```

### Notebook 02: Daily Incremental Refresh

```
1. Calculate today_delta = today - BASE_DATE
2. Calculate yesterday_delta = yesterday - BASE_DATE
3. incremental_shift = today_delta - yesterday_delta (always 1)
4. Check if already ran today → if yes, exit cleanly
5. Validate delta > 0
6. Capture pre-update stats
7. For each eligible column:
   - UPDATE table SET column = DATE_ADD(column, incremental_shift) WHERE column IS NOT NULL
8. Validate post-update stats
9. Log all operations
10. Display summary report
```

**Key insight:** Because the incremental shift is always (today_delta - yesterday_delta), running the notebook multiple times on the same day has no effect — dates advance by exactly 1 day per calendar day.

---

## 📌 Best Practices

✅ **Do:**
- Run Notebook 01 exactly once after initial data load
- Schedule Notebook 02 as a daily pipeline job at a consistent time
- Review execution logs weekly to monitor health
- Test with `DRY_RUN = True` before scheduling
- Keep `BASE_DATE` constant forever

❌ **Don't:**
- Run Notebook 01 more than once (dates will double-shift)
- Change `BASE_DATE` after initial setup
- Manually edit dates in included tables while notebooks are running
- Disable safety checks/exclusion rules
- Schedule Notebook 01 repeatedly

---

## 🔧 Advanced Customization

### Add a New Table

To add a new table to refresh:

1. Open the notebook
2. Go to cell 4 (INCLUDE_CONFIG)
3. Add the schema, table, and columns:

```python
"myschema": {
    "MyTable": ["DateColumn1", "DateColumn2"],
}
```

4. Save and run

### Exclude a Column Temporarily

Add to `EXCLUDE_CONFIG`:

```python
EXCLUDE_CONFIG = {
    # ... existing entries
    "myschema": {
        "MyTable": ["ColumnToSkip"],
    }
}
```

The exclusion takes precedence over inclusion.

### View Detailed Logs for a Specific Run

```python
run_id = "RUN_20260501_120000_a1b2c3d4"  # Replace with actual run_id
spark.sql(f"SELECT * FROM default.date_refresh_execution_log WHERE run_id = '{run_id}'").display()
```

---

## 📞 Support

- **Log Table:** `default.date_refresh_execution_log` — check this for all execution details
- **Test Mode:** Use `DRY_RUN = True` to see what would happen without changes
- **Idempotent:** Notebook 02 is safe to re-run multiple times (checks prevent duplicates)

---

## 🎓 Example: Typical Deployment

```
Monday:
  → Run Notebook 01 (initial setup)
  → Delta = 150 days (from 2026-04-30 to 2026-09-27)
  → All 22 columns shifted forward 150 days

Tuesday-Daily:
  → Notebook 02 scheduled at 2 AM UTC
  → incremental_shift = 1 day
  → All 22 columns shifted forward 1 more day
  → Dates always stay synchronized with "today"

Example: OrderDate
  Original in CSV:  2024-01-15
  After Notebook 01: 2026-06-13 (2024-01-15 + 150 days)
  After 1 day:       2026-06-14 (2026-06-13 + 1 day)
  After 2 days:      2026-06-15 (2026-06-14 + 1 day)
  etc.
```

---

**Version:** 1.0  
**Last Updated:** 2026-07-23  
**Status:** Production Ready ✅