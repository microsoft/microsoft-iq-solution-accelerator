# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "environment": {
# META       "environmentId": "dbdd05da-38b9-ba76-46a5-48b7eb002739",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Configure Fabric Data Agent
# 
# This notebook configures the Microsoft Fabric Data Agent using the `fabric-data-agent-sdk` library (in preview).
# 
# The notebook performs the following tasks:
# 1. **Install and Import Required Libraries** - Set up the necessary SDK and dependencies
# 2. **Variable Initialization and AI Instructions** - Configure data agent settings and define comprehensive AI instructions for manufacturing analytics
# 3. **Initialize Data Agent Client** - Create a connection to the Data Agent service
# 4. **Connect to Existing Data Agent** - Establish connection to a pre-existing data agent instance
# 5. **Configure KQL Database as Data Source** - Add the KQL database and select specific tables (assets, events, locations, products, sites) for AI access
# 6. **Configure Data Agent with AI Instructions and Few-shot Examples** - Apply AI instructions, remove existing few-shot examples, and add new query examples to improve the agent's performance
# 7. **Publish Data Agent Configuration** - Publish all configuration changes to make the data agent available for use

# MARKDOWN ********************

# ## Step 1: Install and Import Required Libraries

# CELL ********************

# Install the fabric data agent SDK for programmatic management
# NOTE: THIS WILL BE CONFIGURED VIA ENVIRONMENT AS SCHEDULED JOBS DO NOT ALLOW pip install COMMANDS
# %pip install fabric-data-agent-sdk==0.1.16a0
# %pip show fabric-data-agent-sdk

# Import required libraries
from uuid import UUID
from fabric.dataagent.client import FabricDataAgentManagement

print("✅ Installation and import complete")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Step 2: Variable Initialization and AI Instructions
# 
# Configure the variables needed for the data agent setup and define AI instructions:

# CELL ********************

# Configuration variables
data_agent_id = "f373b898-e1f3-4a01-9519-4b7de4fd112d"
kql_database_id = "db86e8ca-cf19-41e7-812b-03652b724f0b"
kql_database_workspace_id = "70ca3b6c-a202-456c-ad4d-4355f7bfa375"

print(f"📋 Configuration:")
print(f"   Data Agent ID: {data_agent_id}")
print(f"   KQL Database ID: {kql_database_id}")

# AI instructions
agent_instructions = """
# Manufacturing Analytics Data Agent - Master Prompt

## Objective

You are a specialized manufacturing analytics data agent designed to help business users analyze camping equipment production data and real-time manufacturing events. Your primary goal is to translate natural business questions into efficient KQL queries that provide actionable insights for operational excellence, quality control, predictive maintenance, and financial optimization.

Your goal is to empower business users with data-driven insights that improve manufacturing operations, product quality, and financial performance while maintaining the highest standards of data accuracy and query performance.

## Background and Special Guide

The data is synthetically generated. It is part of a solution accelerator as a public GitHub Repository. The purpose is to let users clone and deploy to jumpstart their real-time intelligence projects. The data is far from being comprehensive like those collected from a real-world manufacturing facility. There are limitations on what you can get out of the small sample datasets. Please follow below guidelines when interacting with users: 

- Do not offer root cause analysis or other complex statistical analysis.  
- Do not offer charts or visual reports. If users ask for them, explain that you cannot produce them at present. 
- When users ask about data in particular tables, exclude fields that are GUIDs when you display the fields of a table. 
- When users ask general questions such as "How tall is the Empire State Building?" or "What is the population of USA?", please refrain from answering them and decline politely as you are not a general chatbot. 

## Starter Prompts 

For starter prompts, you can suggest below questions for user to ask:

- Can you show me the baseline statistics and performance ranges for each asset?
- What are the detailed defect statistics and quality issue rates by asset?
- Can you give me a high-level overview of our manufacturing data and operations?
- What's our total production volume over the last 3 months?
- What's the total revenue generated from our manufacturing operations?

## Data Architecture & Sources

**Primary Data Source:** `events` table (fact table with 259K+ manufacturing events)

- **Assets:** A_1000, A_1001 (camping equipment production assets)
- **Time Range:** 3-month period (Aug-Oct 2025 currently, but this can change based on user's deployment and data set)
- **Key Metrics:** Speed (RPM), Temperature (°C), Vibration, DefectProbability

**Dimensional Tables:** 

- `assets` - Asset master data and specifications
- `sites` - Manufacturing site and plant information  
- `locations` - Facility and geographic data
- `products` - Product catalog and specifications

**Data Priority Order:**

1. Use `events` table for all transactional analysis
2. Join with `assets` for asset-specific insights
3. Use other dimension tables only when specifically needed for context

## Key Business Terminology

**Manufacturing KPIs:**

- **OEE (Overall Equipment Effectiveness):** Asset utilization and efficiency measure
- **Defect Rate:** Percentage of products with quality issues (target: <2% for Six Sigma)
- **Quality Score:** Inverted defect rate ((1 - DefectProbability) * 100)
- **Production Efficiency:** Combination of speed, quality, and throughput
- **Asset Health Score:** Composite metric for predictive maintenance

**Operational Terms:**

- **Shift Patterns:** Day (6-14h), Evening (14-22h), Night (22-6h)
- **Critical Defect Events:** DefectProbability > 0.10 (10%)
- **High Defect Events:** DefectProbability > 0.05 (5%)
- **Quality Grades:** A+ (≤2%), A (≤3.5%), B (≤5%), C (≤7.5%), D (>7.5%)

**Financial Metrics:**

- **Quality Premium:** Revenue multiplier based on quality performance
- **Production Cost:** Base cost + operational factors (speed, temperature)
- **Profit Margin:** (Revenue - Costs) / Revenue * 100

## Critical KQL Generation Guidelines

### ✅ **ALWAYS DO:**

1. **Use Simple Queries:** Start with basic `summarize` operations, avoid complex nesting
2. **Single-Level Operations:** Use one `extend` operation per step, never reference variables within the same extend
3. **Direct Aggregations:** Use direct `summarize` functions instead of `let` statements
4. **Performance-First:** Optimize for Fabric EventHouse compatibility
5. **Statistical Approach:** For large datasets, start with row counts and data ranges

### ❌ **NEVER DO:**

1. **Complex Let Statements:** Avoid `let variableName = (complex query)`
2. **Union Operations:** Don't use `union` for report formatting - use simple queries
3. **Circular References:** Never reference a calculated column in the same `extend` operation
4. **Nested Subqueries:** Avoid complex nested operations that cause semantic errors
5. **Print + Union Patterns:** Don't use `print` with `union` for formatting

### 🎯 **Proven KQL Patterns:**

**Basic Asset Analysis:**

```kql
events
| summarize 
    TotalEvents = count(),
    AvgSpeed = round(avg(Speed), 1),
    AvgDefectRate = round(avg(DefectProbability) * 100, 2)
by AssetId
| extend QualityScore = round((1 - AvgDefectRate/100) * 100, 1)
| order by QualityScore desc
```

**Time-Based Analysis:**

```kql
events
| extend Shift = case(
    hourofday(Timestamp) >= 6 and hourofday(Timestamp) < 14, "Day_Shift",
    hourofday(Timestamp) >= 14 and hourofday(Timestamp) < 22, "Evening_Shift", 
    "Night_Shift"
)
| summarize Production = count(), AvgSpeed = avg(Speed) by AssetId, Shift
```

**Multi-Step Calculations:**

```kql
events
| summarize AvgDefectRate = avg(DefectProbability) by AssetId
| extend QualityScore = round((1 - AvgDefectRate) * 100, 1)
| extend QualityGrade = case(
    QualityScore >= 98, "A_Excellent",
    QualityScore >= 95, "B_Good",
    "C_Fair"
)
```


## Response Guidelines

### Data Integrity & Accuracy

- **Always use actual data** - Never fabricate or assume values
- **Acknowledge limitations** - If data doesn't support the question, explain what's missing
- **Validate before querying** - For large datasets, start with record counts and date ranges
- **Performance consciousness** - Optimize queries for Fabric EventHouse real-time requirements

### Query Development Process

1. **Understand the business question** - Clarify intent before writing KQL
2. **Start simple** - Begin with basic aggregations, add complexity incrementally  
3. **Test logic** - Ensure calculations make business sense
4. **Optimize performance** - Use appropriate time filters and groupings
5. **Provide context** - Explain results in business terms

### Communication Style

- **Business-friendly language** - Translate technical results into actionable insights
- **Structured responses** - Use clear headings and bullet points
- **Visual indicators** - Use emojis and formatting for key insights
- **Actionable recommendations** - When possible, suggest next steps or improvements

### Error Handling

- **Clarify ambiguous requests** - Ask specific questions to understand intent
- **Identify potential typos** - Suggest corrections for unclear asset names or metrics
- **Explain limitations** - When requests exceed available data or capabilities
- **Provide alternatives** - Suggest related analysis when exact request isn't feasible

## Manufacturing-Specific Topic Handling

### Asset Performance Questions

**Common Patterns:** "How is Asset [X] performing?" "Compare A_1000 vs A_1001"
**Response Framework:**

1. Production volume and efficiency metrics
2. Quality performance and defect rates  
3. Operating condition ranges (speed, temperature)
4. Performance trends and recommendations

### Quality & Defect Analysis

**Common Patterns:** "What's our quality?" "Why are defects increasing?" 
**Response Framework:**

1. Current defect rates vs targets (Six Sigma = <2%)
2. Quality distribution and statistical analysis
3. Root cause correlation (speed, temperature, shift)
4. Improvement opportunities and benchmarks

### Production Efficiency & Optimization  

**Common Patterns:** "Which shift performs better?" "How can we improve efficiency?"
**Response Framework:**

1. Shift and time-based performance analysis
2. Efficiency scoring and grading
3. Optimal operating condition identification
4. Bottleneck and improvement opportunities

### Predictive Maintenance & Asset Health

**Common Patterns:** "When should we maintain [asset]?" "Asset health status?"
**Response Framework:**

1. Asset health scoring based on operational metrics
2. Maintenance priority classification
3. Performance degradation trends
4. Recommended maintenance schedules

### Financial & Business Impact

**Common Patterns:** "What's our ROI?" "How does quality affect revenue?"
**Response Framework:**

1. Revenue calculations with quality premiums
2. Cost analysis including operational factors
3. Profit margins and financial KPIs
4. Investment and optimization recommendations

## Data Quality & Validation Rules

### Before Every Query

1. **Check data freshness:** Verify recent data availability
2. **Validate time ranges:** Ensure requested periods have data
3. **Confirm asset coverage:** Check which assets have data in the timeframe
4. **Assess data completeness:** Identify any gaps or anomalies

### Performance Optimization

- **Use time filters:** Always include relevant time constraints
- **Limit result sets:** Use `take` or `top` for large datasets when appropriate
- **Efficient grouping:** Group by the most selective dimensions first
- **Avoid cartesian joins:** Be careful with multi-table queries

### Business Logic Validation

- **Realistic ranges:** Speed (0-150 RPM), Temperature (15-50°C), DefectProbability (0-1)
- **Logical relationships:** Higher speed may correlate with higher defects
- **Seasonal patterns:** Consider time-based trends and cycles
- **Asset-specific behavior:** A_1000 and A_1001 may have different characteristics

## Sample Query Starters by Business Scenario

### Executive Dashboard

```kql
// Production overview for leadership reporting
events | summarize TotalProduction = count(), AvgQuality = round((1-avg(DefectProbability))*100,1) by AssetId
```

### Operational Monitoring  

```kql
// Real-time asset performance monitoring
events | where Timestamp >= ago(24h) | summarize Events = count(), AvgSpeed = avg(Speed) by AssetId, bin(Timestamp, 1h)
```

### Quality Analysis

```kql
// Quality control and process improvement
events | summarize DefectRate = round(avg(DefectProbability)*100,2), QualityEvents = countif(DefectProbability <= 0.02) by AssetId
```

### Maintenance Planning

```kql
// Predictive maintenance insights  
events | summarize AvgSpeed = avg(Speed), AvgTemp = avg(Temperature), AvgVibration = avg(Vibration) by AssetId
```

## Ethical Guidelines & Safety

- **Data Accuracy:** Only rely on the data provided from the data sources and never make up any new data.
- **Manufacturing safety:** Never provide recommendations that could compromise worker safety
- **Data privacy:** Respect any confidentiality requirements for production data
- **Accurate reporting:** Ensure quality and safety metrics are precisely calculated
- **Responsible insights:** Consider business impact of recommendations and analysis
"""

data_source_instructions="""
# Data Source Instructions

## Overview

This Fabric Data Agent has access to manufacturing operations data in an EventHouse database.

## Business Context

**Note:** Replace this content with your organization's actual business performance measurements. 

This sample dataset represents common manufacturing scenarios:

- Equipment monitoring and maintenance
- Product quality control
- Operational efficiency analysis
- Real-time alerting and diagnostics

### Database Tables and Relationships 

**Note:** Replace this content with your organization's actual data and update table schemas accordingly.

#### Core Tables

- **`events`** - Manufacturing telemetry and sensor data (real-time + historical)
- **`assets`** - Equipment and machinery information  
- **`products`** - Product catalog and specifications
- **`sites`** - Manufacturing facility locations
- **`locations`** - Geographic information

#### Data Relationships

```
events → assets → sites → locations
events → products
```

#### Real-Time Data

- **`events` table** receives continuous real-time data via EventStream
- Contains sensor readings: temperature, vibration, humidity, speed
- Includes quality metrics: defect probability
- Links to specific assets and products

#### Reference Data  

- **Static tables** (assets, products, sites, locations) contain stable reference information
- Used for context and enrichment of event data
- Updated infrequently

### Query Patterns

When analyzing manufacturing data, typically join events with reference tables:

```kql
// Asset performance analysis
events
| join assets on $left.AssetId == $right.Id
| summarize avg(Temperature), avg(Speed) by AssetId, assets.Name

// Product quality tracking  
events
| join products on $left.ProductId == $right.Id
| summarize avg(DefectProbability) by ProductId, products.Name
```
```
"""

data_source_description="""
# Data Source Descriptions for Fabric Data Agent 

## Overview
The KQL database contains manufacturing operations data from Contoso Outdoors' Ho Chi Minh facility, which produces outdoor camping equipment. The data includes real-time telemetry, asset information, and product details.

## Data Tables

### Table `events`
Large telemetry dataset with 259,000+ sensor readings from manufacturing equipment. Contains timestamps, asset IDs, product IDs, sensor measurements (vibration, temperature, humidity, speed), and defect probability calculations.

### Table `assets`  
Equipment information for 2 manufacturing assets:
- A_1000: Robotic Arm 1 (Assembly line)
- A_1001: Packaging Line 1 (Packaging operations)

Includes asset names, types, serial numbers, and maintenance status.

### Table `products`
Product catalog with 21 outdoor camping products including camping stoves and tables. Contains product details, pricing (list price and unit cost), categories, colors, and brand information (Contoso Outdoors).

### Table `locations`
Geographic data showing the facility location in Ho Chi Minh City, Vietnam.
"""

# Initialize few-shot examples for KQL queries based on manufacturing operations
fewshots_examples = {'Can you show me the baseline statistics and performance ranges for each asset?': 'events\r\n| summarize \r\n    EventCount = count(),\r\n    SpeedMean = round(avg(Speed), 2),\r\n    SpeedStdev = round(stdev(Speed), 2),\r\n    SpeedMin = round(min(Speed), 1),\r\n    SpeedMax = round(max(Speed), 1),\r\n    TempMean = round(avg(Temperature), 2),\r\n    TempStdev = round(stdev(Temperature), 2),\r\n    TempMin = round(min(Temperature), 1),\r\n    TempMax = round(max(Temperature), 1),\r\n    DefectMean = round(avg(DefectProbability), 4),\r\n    DefectStdev = round(stdev(DefectProbability), 4),\r\n    DefectMin = round(min(DefectProbability), 4),\r\n    DefectMax = round(max(DefectProbability), 4)\r\nby AssetId\r\n| order by AssetId', 'What are the detailed defect statistics and quality issue rates by asset?': 'events\r\n| summarize \r\n    Events = count(),\r\n    MinDefect = round(min(DefectProbability), 4),\r\n    MaxDefect = round(max(DefectProbability), 4),\r\n    MeanDefect = round(avg(DefectProbability), 4),\r\n    MedianDefect = round(percentile(DefectProbability, 50), 4),\r\n    StdDevDefect = round(stdev(DefectProbability), 4),\r\n    P95Defect = round(percentile(DefectProbability, 95), 4),\r\n    Above5Percent = countif(DefectProbability > 0.05),\r\n    Above10Percent = countif(DefectProbability > 0.10),\r\n    Above15Percent = countif(DefectProbability > 0.15)\r\nby AssetId\r\n| extend \r\n    MeanPercent = round(MeanDefect * 100, 2),\r\n    MedianPercent = round(MedianDefect * 100, 2),\r\n    P95Percent = round(P95Defect * 100, 2)\r\n| extend\r\n    QualityIssueRate = round(Above5Percent * 100.0 / Events, 1),\r\n    HighDefectRate = round(Above10Percent * 100.0 / Events, 1),\r\n    CriticalDefectRate = round(Above15Percent * 100.0 / Events, 1)\r\n| order by MeanPercent asc', 'Can you give me a high-level overview of our manufacturing data and operations?': 'events \r\n| summarize \r\n    EventCount = count(),\r\n    DateFrom = min(Timestamp),\r\n    DateTo = max(Timestamp),\r\n    UniqueAssets = dcount(AssetId),\r\n    AvgSpeed = round(avg(Speed), 1),\r\n    AvgTemp = round(avg(Temperature), 1),\r\n    AvgDefectRate = round(avg(DefectProbability) * 100, 2)\r\n\r\n'}

print(f"📋 AI Instructions and Configuration Defined:")
print(f"   Agent Instructions: {len(agent_instructions)} characters")
print(f"   Data Source Description: {len(data_source_description)} characters")
print(f"   Data Source Instructions: {len(data_source_instructions)} characters")
print(f"   Fewshots Examples: {len(fewshots_examples)} examples prepared")
print(f"   ✅ Configuration ready")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Step 3: Initialize Data Agent Client
# 
# Create a connection to the Data Agent service:

# CELL ********************

# Initialize the Data Agent management client for existing data agent
mgmt_client = FabricDataAgentManagement(UUID(data_agent_id))
print(f"✅ Successfully initialized Data Agent management client for: {data_agent_id}")
print(f"✅ Client ready for data agent operations")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Step 4: Connect to Existing Data Agent
# 
# Connect to an existing data agent using the configured ID:

# CELL ********************

# Connect to existing data agent and verify configuration
print(f"🤖 Connecting to existing data agent: {data_agent_id}")

config = mgmt_client.get_configuration()
print(f"✅ Successfully connected to data agent")

print(f"\n📊 Data Agent Details:")
print(f"   Name: RTI Operations Agent")
print(f"   ID: {data_agent_id}")
print(f"   Status: Ready for configuration")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Step 5: Configure KQL Database as Data Source
# 
# Add the KQL database as a data source and select specific tables (assets, events, locations, products, sites) for the data agent:

# CELL ********************

# Add KQL database as data source to the data agent
print(f"🔗 Adding KQL database as data source...")
print(f"   Data Agent ID: {data_agent_id}")
print(f"   KQL Database ID: {kql_database_id}")

# Add the KQL database as a data source
datasource = mgmt_client.add_datasource(
    workspace_id_or_name=UUID(kql_database_workspace_id),
    artifact_name_or_id=UUID(kql_database_id),
    type="kqldatabase"
)

print(f"✅ Successfully added KQL database data source")
print(f"   Datasource ID: {datasource._id}")

# Configure specific tables to be available to the AI
selected_tables = ["assets", "events", "locations", "products", "sites"]
print(f"\n📋 Configuring table selection...")
print(f"   Selected tables: {', '.join(selected_tables)}")

# Enable the specified tables for the data agent
for table_name in selected_tables:
    datasource.select(table_name)
    print(f"   ✓ Enabled table: {table_name}")

print(f"✅ Table configuration completed")
print(f"   Tables available to AI: {', '.join(selected_tables)}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Step 6: Configure Data Agent with AI Instructions and Few-shot Examples
# 
# Apply the AI instructions and add few-shot examples to configure the data agent's behavior:

# CELL ********************

# Update data agent with general AI instructions
print(f"🤖 Updating data agent with AI instructions...")
print(f"   Instructions length: {len(agent_instructions)} characters")

mgmt_client.update_configuration(instructions=agent_instructions)
print(f"✅ Successfully updated data agent configuration")

# Configure data source with specific instructions and description
print(f"\n🔗 Configuring data source instructions...")
print(f"   Instructions length: {len(data_source_instructions)} characters")

datasource.update_configuration(
    instructions=data_source_instructions,
    user_description=data_source_description
)
print(f"✅ Successfully updated data source configuration")

# Get existing few-shot examples and remove them
print(f"\n🔍 Checking for existing few-shot examples...")
existing_fewshots = datasource.get_fewshots()
print(f"   Found {len(existing_fewshots)} existing examples")

if len(existing_fewshots) > 0:
    print(f"🗑️ Removing existing few-shot examples...")
    for i, row in existing_fewshots.iterrows():
        fewshot_id = row['Id']
        question = row['Question'][:50] + ('...' if len(row['Question']) > 50 else '')
        print(f"   Removing: {question}")
        datasource.remove_fewshot(fewshot_id)
    print(f"✅ Successfully removed all {len(existing_fewshots)} existing examples")
else:
    print(f"   No existing examples to remove")

# Add few-shot examples to improve query generation
print(f"\n📚 Adding few-shot examples...")
print(f"   Adding {len(fewshots_examples)} example question-query pairs")

for i, (question, query) in enumerate(fewshots_examples.items(), 1):
    print(f"   {i}. Adding: {question[:60]}{'...' if len(question) > 60 else ''}")
    single_example = {question: query}
    datasource.add_fewshots(single_example)

print(f"✅ Successfully added all {len(fewshots_examples)} few-shot examples")

# Verify final configuration
fewshots_df = datasource.get_fewshots()
config = mgmt_client.get_configuration()
ds_config = datasource.get_configuration()

print(f"\n📊 Final Configuration Summary:")
print(f"   Agent instructions: {'✓' if config.instructions else '✗'}")
print(f"   Data source instructions: {'✓' if ds_config.get('additional_instructions') else '✗'}")
print(f"   Data source description: {'✓' if ds_config.get('user_description') else '✗'}")
print(f"   Few-shot examples: {len(fewshots_df)}")
print(f"   Datasource ID: {datasource._id}")

print(f"\n✅ Data agent configuration completed successfully!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Step 7: Publish Data Agent Configuration
# 
# Publish the data agent configuration to make it available for use:

# CELL ********************

# Publish the data agent configuration
print(f"📤 Publishing data agent configuration...")
print(f"   Making data agent available for use...")

mgmt_client.publish()
print(f"✅ Successfully published data agent configuration")
print(f"   Data agent is now ready to answer questions!")
print(f"   You can now interact with the agent in Fabric using natural language queries")

print(f"\n🎉 Data Agent Configuration Complete!")
print(f"   Agent ID: {data_agent_id}")
print(f"   Status: Published and Ready")
print(f"   Available Tables: {', '.join(selected_tables)}")
print(f"   Few-shot Examples: {len(fewshots_examples)}")
print(f"   Next: Test the agent with manufacturing analytics queries!")
