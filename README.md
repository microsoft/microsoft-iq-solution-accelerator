# Microsoft IQ Solution Accelerator

The Microsoft IQ Solution Accelerator is an AI-powered enterprise intelligence accelerator that enables faster, more informed decisions by unifying enterprise data, business knowledge, and execution workflows into a shared context. It connects unified data, semantic models and ontologies in Fabric IQ, enterprise knowledge and retrieval in Foundry IQ, and work context in Work IQ to identify signals, assess impact, and recommend disruption mitigation, supporting human decision-making and coordinated responses.

**Key Use Cases and Customization:**

- **Supply Chain Use Case**: During supplier disruptions, teams assess risk and inventory, evaluate sourcing options, and coordinate actions to protect product availability and continuity of supply.
- **Reusability and Customization**: The architecture can be adapted for other business scenarios. Please refer to [How to customize](#how-to-customize).

<br/>

<div align="center">


[**SOLUTION OVERVIEW**](#solution-overview) \| [**QUICK DEPLOY**](#quick-deploy) \| [**BUSINESS SCENARIO**](#business-use-case) \| [**SUPPORTING DOCUMENTATION**](#supporting-documentation)

</div>
<br/>


<h2 id="solution-overview"><img src="./docs/images/readme/solution-overview.png" width="48" />
Solution overview
</h2>
This is a ready-to-deploy solution accelerator built on Microsoft 365 Copilot, Microsoft Foundry, and Microsoft Fabric. It combines Work IQ, Foundry IQ, and Fabric IQ to support end-to-end disruption detection, analysis, and response.


### Solution architecture

The diagram below illustrates the solution architecture. For a detailed architecture description, see the [architecture description](./docs/TechnicalArchitecture.md).

| ![image](./docs/images/readme/solution-architecture.png) |
| -------------------------------------------------------- |

### How to customize

If you'd like to customize the solution accelerator, here are some common areas to start with steps to take:  

1.  Review the documentation in the [docs](./docs) folder and subfolders, including [architecture description](./docs/TechnicalArchitecture.md).
2.  Review the schema and data loaded for Fabric Lakehouse to understand the differences between the sample data structure and your business data. Refer to [Fabric Component Overview](./docs/fabric/README.md) for more details. 
3.  Review the documents stored in Foundry. Refer to [Foundry Component Overview](./docs/foundry/README.md) for more details. 
4.  Review the Copilot Studio Agent and workflow, and compare it with your business process. Refer to [Copilot Component Overview](./docs/copilot/README.md) for more details. 
5.  Then develop a customization plan. 

## Features
<details>
  <summary>Click to learn more about the key features this solution enables</summary>

  - **Copilot Studio Agent and Supply Chain Management Workflow** <br/>Powered by AI, Copilot Studio Agent orchestrates the response workflow when disruption signals appear, helping teams triage issues and act quickly.

  - **Foundry Chat Agent** <br/>

    Used within the Copilot workflow, the Foundry Chat Agent answers questions about supplier contracts, terms, and policies.

  - **Fabric Ontology Data Agent** <br/>

    Used within the Copilot workflow, the Fabric Ontology Data Agent answers questions about enterprise data, including customers, products, inventory, suppliers, and demand forecasts.

</details>

<br /><br />

<h2 id="quick-deploy"><img src="./docs/images/readme/quick-deploy.png" width="48" />
Quick deploy
</h2>
<br />

To deploy the solution in your environment, follow the [deployment guide](./docs/DeploymentGuide.md).

### Prerequisites and costs

To deploy this solution accelerator, ensure you have access to an [Azure subscription](https://azure.microsoft.com/free/) with the following permissions:

- **Contributor** role at the subscription level
- **Role Based Access Control (RBAC)** permissions to assign roles at the subscription and/or resource group level
- Ability to create resource groups, resources, and app registrations

For detailed setup instructions, see [Azure Account Set Up](./docs/AzureAccountSetUp.md).

The table below lists the major Microsoft products utilized, with product, description, and cost reference. 

> **Note:** This pricing overview is not comprehensive—actual costs will vary based on your selected SKUs, usage scale, customizations, and tenant integrations. Use these estimates as a starting point and adjust for your specific requirements.

<br/>

| Product | Description | Cost |
|---|---|---|
| [Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-365/copilot/) | Microsoft 365 Copilot is an AI-powered tool that helps with your work tasks. Users enter a prompt, and Copilot responds with AI-generated information using both web and organizational data that the user has permission to access | [Pricing](https://www.microsoft.com/en-us/microsoft-365-copilot/pricing) |
| [Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/) | Microsoft Foundry is a unified Azure platform-as-a-service offering for enterprise AI operations, model builders, and application development. This foundation combines production-grade infrastructure with friendly interfaces, enabling developers to focus on building applications rather than managing infrastructure. | [Pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-foundry/) |
| [Microsoft Fabric](https://learn.microsoft.com/en-us/fabric) | Microsoft Fabric is an analytics platform that supports end‑to‑end data workflows, including data ingestion, transformation, real‑time stream processing, analytics, and reporting. It provides integrated experiences such as Data Engineering, Data Factory, Data Science, Real‑Time Intelligence, Data Warehouse, and Databases, which operate over a shared compute and storage model. | [Pricing](https://learn.microsoft.com/en-us/fabric/enterprise/buy-subscription#prerequisites) |

<br/>

>⚠️ **Important:** To avoid unnecessary costs, remember to take down your app if it's no longer in use,
either by deleting the resource group in the Portal or running `azd down`.

<br /><br />

<h2 id="business-use-case"><img src="./docs/images/readme/business-scenario.png" width="48" />
Business use case
</h2>
The Microsoft IQ Solution Accelerator leverages a shared intelligence layer that connects enterprise data, knowledge, and workflows to enable faster, more informed operational decisions. The accelerator integrates signals across customer, product, sales, inventory, and supply chain to detect risks early, assess business impact, and align cross-functional response efforts.

**Key use cases by role:**

| Role | Capabilities |
|---|---|
| **Supply Chain Manager** | The supply chain manager quickly assesses supply chain disruption impact, updates sourcing and planning actions that protect availability and meet demand. |
| **Support Staff** | Support staff can assist the supply chain manager in validating information and resolving problems. |

> ⚠️ **Note:** The sample data in this repository is synthetic, generated using Python programs, and intended for demonstration purposes only.

### Business value
<details>
  <summary>Click to learn more about what value this solution provides</summary>

  - **Role-aware signal detection and decisions in workflow** <br/>Copilot Studio Agent coordinates sub‑agents, people, and workflows to validate disruptions, align stakeholders, and act. Data-driven decisions are supported by Foundry Chat Agent and Fabric Ontology Data Agent. 

  - **Assess impact in a timely manner**

    Fabric Ontology Data Agent enables consistent impact assessment across suppliers, products, and distribution centers, so teams can understand what’s at risk before decisions are made.

  - **Reason through feasible options**

    Foundry Chat Agent retrieves and reasons over supplier contracts, SLAs, lead times, policies, and historical performance to evaluate feasible sourcing and replanning paths.

</details>

<br /><br />

<h2 id="supporting-documentation"><img src="./docs/images/readme/supporting-documentation.png" width="48" />
Supporting documentation
</h2>

## Guidance

### Security guidelines

This template uses Azure Key Vault to store all connections used to communicate between resources.

This template also uses [Managed Identity](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview) for local development and deployment.

To ensure continued best practices in your own repository, we recommend that anyone creating solutions based on our templates ensure that the [GitHub secret scanning](https://docs.github.com/code-security/secret-scanning/about-secret-scanning) setting is enabled.

You may want to consider additional security measures, such as:

* Enabling Microsoft Defender for Cloud to [secure your Azure resources](https://learn.microsoft.com/en-us/azure/defender-for-cloud/).
* Protecting the Azure Container Apps instance with a [firewall](https://learn.microsoft.com/azure/container-apps/waf-app-gateway) and/or [Virtual Network](https://learn.microsoft.com/azure/container-apps/networking?tabs=workload-profiles-env%2Cazure-cli).

<br/>

### Frequently asked questions

[Click here](./docs/FAQs.md) to learn more about common questions about this solution.

<br/>

### Cross references

Check out similar solution accelerators.

| Solution Accelerator                                         | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Agentic applications for unified data foundation](https://github.com/microsoft/agentic-applications-for-unified-data-foundation-solution-accelerator) | Agentic AI application that provides natural language query of the data using unified data foundation, extending the Fabric Data Agent capabilities included in this solution. |
| [Real-Time Intelligence for Operations Solution Accelerator](https://github.com/microsoft/real-time-intelligence-operations-solution-accelerator) | This solution accelerator provides a complete real-time intelligence platform for manufacturing operations. It analyzes live and historical telemetry data through interactive dashboards, automatically detects anomalies with email alerts, and includes an AI-powered data agent for conversational insights. |
| [Unified Data Foundation with Microsoft Fabric](https://github.com/microsoft/unified-data-foundation-with-fabric-solution-accelerator) | Unified Data Foundation with Microsoft Fabric with Options to Integrate with Azure Databricks and Microsoft Purview. |

<br/>

## Provide feedback

Have questions, find a bug, or want to request a feature? [Submit a new issue](https://github.com/microsoft/microsoft-iq-solution-accelerator/issues) on this repo and we'll connect.

<br/>

## Responsible AI Transparency FAQ 
Please refer to [Transparency FAQ](./TRANSPARENCY_FAQ.md) for responsible AI transparency details of this solution accelerator.

<br/>

## Disclaimers

To the extent that the Software includes components or code used in or derived from Microsoft products or services, including without limitation Microsoft Azure Services (collectively, “Microsoft Products and Services”), you must also comply with the Product Terms applicable to such Microsoft Products and Services. You acknowledge and agree that the license governing the Software does not grant you a license or other right to use Microsoft Products and Services. Nothing in the license or this ReadMe file will serve to supersede, amend, terminate or modify any terms in the Product Terms for any Microsoft Products and Services. 

You must also comply with all domestic and international export laws and regulations that apply to the Software, which include restrictions on destinations, end users, and end use. For further information on export restrictions, visit https://aka.ms/exporting. 

You acknowledge that the Software and Microsoft Products and Services (1) are not designed, intended or made available as a medical device(s), and (2) are not designed or intended to be a substitute for professional medical advice, diagnosis, treatment, or judgment and should not be used to replace or as a substitute for professional medical advice, diagnosis, treatment, or judgment. Customer is solely responsible for displaying and/or obtaining appropriate consents, warnings, disclaimers, and acknowledgements to end users of Customer’s implementation of the Online Services. 

You acknowledge the Software is not subject to SOC 1 and SOC 2 compliance audits. No Microsoft technology, nor any of its component technologies, including the Software, is intended or made available as a substitute for the professional advice, opinion, or judgement of a certified financial services professional. Do not use the Software to replace, substitute, or provide professional financial advice or judgment.  

BY ACCESSING OR USING THE SOFTWARE, YOU ACKNOWLEDGE THAT THE SOFTWARE IS NOT DESIGNED OR INTENDED TO SUPPORT ANY USE IN WHICH A SERVICE INTERRUPTION, DEFECT, ERROR, OR OTHER FAILURE OF THE SOFTWARE COULD RESULT IN THE DEATH OR SERIOUS BODILY INJURY OF ANY PERSON OR IN PHYSICAL OR ENVIRONMENTAL DAMAGE (COLLECTIVELY, “HIGH-RISK USE”), AND THAT YOU WILL ENSURE THAT, IN THE EVENT OF ANY INTERRUPTION, DEFECT, ERROR, OR OTHER FAILURE OF THE SOFTWARE, THE SAFETY OF PEOPLE, PROPERTY, AND THE ENVIRONMENT ARE NOT REDUCED BELOW A LEVEL THAT IS REASONABLY, APPROPRIATE, AND LEGAL, WHETHER IN GENERAL OR IN A SPECIFIC INDUSTRY. BY ACCESSING THE SOFTWARE, YOU FURTHER ACKNOWLEDGE THAT YOUR HIGH-RISK USE OF THE SOFTWARE IS AT YOUR OWN RISK.  
