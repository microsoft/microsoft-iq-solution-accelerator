# Microsoft Fabric Ontology Learning

## Key Concepts
- **Ontology**: Semantic layer that defines business concepts, relationships, and rules
- **Business Objects**: Customer, Product, Order, Supplier, Warehouse
- **Relationships**: Customer→Order, Product→Category, Supplier→Product  
- **Measures**: Revenue, Growth Rate, Lead Time, Inventory Turnover

## Current Data Assets
- **Sales Schema**: Orders, customers, products across camping/kitchen/ski
- **Finance Schema**: Invoices, payments, accounts
- **Supply Chain Schema**: Suppliers, inventory, warehouses, purchase orders

## Ontology Goals
1. **Unified Business View**: Single source of truth across sales, finance, supply chain
2. **Self-Service Analytics**: Business users can explore without SQL knowledge
3. **Consistent Metrics**: Standardized KPIs across all dashboards
4. **Semantic Relationships**: Intelligent data discovery and recommendations

## Next Steps
1. **Define Business Objects**: Map lakehouse tables to business concepts
2. **Model Relationships**: Define how entities connect (1:many, many:many)
3. **Create Measures**: Calculate KPIs (revenue growth, supplier performance)  
4. **Test & Validate**: Ensure ontology serves both Power BI dashboards

## Documentation Resources

### Microsoft Fabric IQ Documentation
- [Fabric IQ documentation - Microsoft Fabric | Microsoft Learn](https://learn.microsoft.com/en-us/fabric/iq/) main page for all useful documentations. 

### GitHub Repo Example
- [Microsoft Fabric Samples Repository](https://github.com/microsoft/fabric-samples) - Comprehensive collection of practical implementations
  - Semantic link tutorials and notebooks
  - Data agent implementation examples
  - Business object modeling patterns
  - FabricDataFrame usage examples
  - AI and machine learning integration samples
  - End-to-end data science workflows
