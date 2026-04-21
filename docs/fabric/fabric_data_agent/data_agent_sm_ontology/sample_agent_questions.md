# Sample Agent Test Questions

Test questions to validate the Semantic Model → Ontology data agent. Organized by difficulty — start from the top and work down.

---

## How to Use

1. Open your data agent in the Fabric workspace.
2. Ask each question in the chat interface.
3. Verify the response matches the expected behavior in the **Validates** column.

> **Tip:** Ask *"List all products"* or *"Show all suppliers"* first to discover available entity values.

---

## Test Questions

| # | Level | Domain | Question | Validates |
|---|---|---|---|---|
| 1 | Beginner | Product | How many products do we have? | Single-entity count |
| 2 | Beginner | Product | List all product categories. | Entity listing + display names |
| 3 | Beginner | Inventory | List all warehouses. | Entity listing |
| 4 | Beginner | Supply Chain | List all suppliers. | Entity listing |
| 5 | Intermediate | Inventory | Which products are below their reorder point? | Filter + comparison logic |
| 6 | Intermediate | Inventory | What is the current stock of Alpine Explorer Tent? | Product → Inventory join |
| 7 | Intermediate | Inventory | Show all purchase orders with status Pending. | Status filter |
| 8 | Intermediate | Supply Chain | Which products are supplied by Contoso Ltd? | Bridge entity traversal |
| 9 | Intermediate | Inventory | Which warehouse has the most available stock? | Aggregation + sorting |
| 10 | Intermediate | Inventory | How much of Coffee Mug is reserved in stock? | Specific product lookup |
| 11 | Advanced | Inventory | What is the demand forecast for Tents for May 2026? | Category → Product → Forecast path |
| 12 | Advanced | Inventory | List top 5 products by current stock in Main Distribution Center. | Multi-hop join + sort + limit |
| 13 | Advanced | Supply Chain | Which suppliers were affected by weather disruptions? | Event impact traversal |
| 14 | Advanced | Supply Chain | What is the total PO value by supplier? | Aggregation across PO items + supplier |
| 15 | Advanced | Cross-domain | Show products with low stock that have active supply chain disruptions. | Multi-domain correlation |

---

## Expected Behavior

✅ **Good responses** include:
- Human-readable names (not raw IDs)
- Correct aggregation with grouping columns
- Explicit sorting when asked for "top" or "bottom"
- Clarification when a term is ambiguous

❌ **Red flags:**
- Agent returns only IDs without names
- Agent invents data not in the ontology
- Multi-hop questions return empty when data exists
- Agent cannot find a product by partial name
