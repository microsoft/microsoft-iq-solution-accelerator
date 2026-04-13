# Inventory Data Generation Summary

**Date Range**: 2025-07-01 to 2026-04-30  
**Duration**: 303 days  
**Integration**: Connected to 53,219 sales line items

## 🏭 Generation Overview

### **Total Summary**
- **Total Records Generated**: 5,402
- **Suppliers**: 5 suppliers loaded from CSV files
- **Product-Supplier Mappings**: 75 relationships
- **Inventory Records**: 81 stock locations
- **Purchase Orders**: 118 procurement orders  
- **PO Line Items**: 238 order details
- **Inventory Transactions**: 4545 movement records
- **Demand Forecasts**: 420 predictive analytics records

### **Supplier Network**

| Supplier | Type | Category | Lead Time |
|----------|------|----------|-----------|
| Contoso Ltd | Primary | Camping | 10 days |  
| Proseware Inc | Primary | Kitchen | 10 days |
| Alpine Ski House | Primary | Ski | 12 days |
| Worldwide Importers | Secondary | Multi-category | 21 days |

### **Domain Coverage**

| Product Category | Primary Supplier | Secondary Coverage | Status |
|------------------|------------------|--------------------|--------|
| 🏕️ Camping | Contoso Ltd | Worldwide Importers | ✅ Active |
| 🍳 Kitchen | Proseware Inc | Worldwide Importers | ✅ Active |  
| ⛷️ Ski | Alpine Ski House | Worldwide Importers | ✅ Active |

## 📋 Generated Files

### **Inventory Data** (`output/inventory/`)  
- `Inventory.csv` - 81 stock levels across warehouses
- `InventoryTransactions.csv` - 4545 movement audit trail
- `PurchaseOrders.csv` - 118 procurement orders  
- `PurchaseOrderItems.csv` - 238 line items with details
- `DemandForecast.csv` - 420 predictive analytics records
- `Warehouses.csv` - 3 distribution center configurations
