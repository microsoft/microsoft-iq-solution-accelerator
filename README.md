# Microsoft IQ Solution Accelerator

The Microsoft IQ Solution Accelerator is an AI-powered enterprise intelligence solution accelerator that enables faster, more informed decisions by unifying enterprise data, business knowledge, and execution workflows into a shared context. This accelerator connects unified data, semantic models and ontologies in Fabric IQ, enterprise knowledge and retrieval in Foundry IQ, and work context in Work IQ to identify signals, produce impact analysis, recommend disruption mitigation to support human decision making in evaluating business decisions and coordinating responses.

**Key use cases:**

- **Supply Chain**: During supplier disruptions, organizations use unified intelligence to assess risk and inventory levels, evaluate sourcing options across the enterprise, and coordinate actions across teams to protect product availability and ensure continuity of supply.
- **TBD** — (Note: Will delete if no additional use case to be supported.)

<br/>

<div align="center">
[**SOLUTION OVERVIEW**](#solution-overview) \| [**QUICK DEPLOY**](#quick-deploy) \| [**BUSINESS SCENARIO**](#business-use-case) \| [**SUPPORTING DOCUMENTATION**](#supporting-documentation)

</div>
<br/>


<h2 id="solution-overview"><img src="./docs/images/readme/solution-overview.png" width="48" />
Solution overview
</h2>
This solution accelerator offers a 


### Solution architecture

The architecture below illustrates the solution architecture. For detailed architecture description, please refer 

[Architecture Description Page](./docs/TechnicalArchitecture.md).

| ![image](./docs/images/readme/solution-architecture.png) |
| -------------------------------------------------------- |

### How to customize

If you'd like to customize the solution accelerator, here are some common areas to start:

You can modify the data models and notebooks in different folders under the `src` folder. Please note that if any part is modified, you will need to modify the associated parts accordingly, as the data model (schemas and tables), notebooks, Power BI semantic models, Power BI dashboards, and sample data are a cohesive set of resources working together as designed.

| Customization Area | Description |
|---|---|
| [Customize Fabric Data Agent](./docs/fabric/fabric_data_agent/README.md) | Customize Data Agent |
| TBD | Text Here|

## Resources

| Resource | Description |
|---|---|
| [What's New in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/whats-new) | Latest features and updates |
| [Microsoft Fabric Blog](https://blog.fabric.microsoft.com/en-us/blog) | News, tips, and best practices |
|  |  |
|  |  |

<br/>

## Features
<details>
  <summary>Click to learn more about the key features this solution enables</summary>

  - **Supply Chain Disruption Management Work Flow** <br/>Work IQ intelligent workflow trigged by supply chain disruption events. The workflow enables supply chain management team to leverage 
  - **TBD** <br/>TBD

</details>

<br /><br />

<h2 id="quick-deploy"><img src="./docs/images/readme/quick-deploy.png" width="48" />
Quick deploy
</h2>
TBD

### Prerequisites and costs

To deploy this solution accelerator, ensure you have access to an [Azure subscription](https://azure.microsoft.com/free/) with the following permissions:

- **Contributor** role at the subscription level
- **Role Based Access Control (RBAC)** permissions to assign roles at the subscription and/or resource group level
- Ability to create resource groups, resources, and app registrations

For detailed setup instructions, see [Azure Account Set Up](./docs/AzureAccountSetUp.md).

**Additional setup for extended architectures:**

| Architecture Option | Additional Setup Required |
|---|---|
| TBD |  |
| TBD | [](./docs/SetupPurview.md) |

Licenses for Microsoft Fabric, TBD ADD MORE

 Below is a high-level overview of the cost considerations for each architecture option:

- **Microsoft Fabric:** Licensing and cost information can be found at [Microsoft Fabric concepts and licenses](https://learn.microsoft.com/en-us/fabric/enterprise/licenses) and [Microsoft Fabric Pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/).

- TBD

  

> **Note:** This pricing overview is not comprehensive—actual costs will vary based on your selected SKUs, usage scale, customizations, and tenant integrations. Use these estimates as a starting point and adjust for your specific requirements.

<br/>

| Product | Description | Cost |
|---|---|---|
| [Microsoft Fabric](https://learn.microsoft.com/en-us/fabric) | Core Medallion Architecture in Microsoft Fabric, and Unified Data Platform for integration with other platforms such as Azure Databricks and Snowflake. | [Pricing](https://learn.microsoft.com/en-us/fabric/enterprise/buy-subscription#prerequisites) |
| TBD                                                          |                                                              |                                                              |
| TBD                                                          |                                                              |                                                              |

<br/>

>⚠️ **Important:** To avoid unnecessary costs, remember to take down your app if it's no longer in use,
either by deleting the resource group in the Portal or running `azd down`.

<br /><br />

<h2 id="business-use-case"><img src="./docs/images/readme/business-scenario.png" width="48" />
Business use case
</h2>
TBD

**Key use cases by role:**

| Role | Capabilities |
|---|---|
| **Data Engineer** |  |
| **Sales Analyst** |  |
| **Business User** |  |

> ⚠️ **Note:** The sample data in this repository is synthetic, generated using Python programs, and intended for demonstration purposes only.

### Business value
<details>
  <summary>Click to learn more about what value this solution provides</summary>

  - **TBD** <br/> TEXT 
  - **TBD** <br/> Text

</details>

<br /><br />

<h2 id="supporting-documentation"><img src="./docs/images/readme/supporting-documentation.png" width="48" />
Supporting documentation
</h2>

## Guidance

### Security guidelines

This template uses Azure Key Vault to store all connections to communicate between resources.

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
Check out similar solution accelerators

| Solution Accelerator | Description |
|---|---|
|                      |             |
|                      |             |

<br/>   

💡 Want to get familiar with Microsoft's AI and Data Engineering best practices? Check out our playbooks to learn more

| Playbook | Description |
|:---|:---|
| [AI&nbsp;playbook](https://learn.microsoft.com/en-us/ai/playbook/) | The Artificial Intelligence (AI) Playbook provides enterprise software engineers with solutions, capabilities, and code developed to solve real-world AI problems. |
| [Data&nbsp;playbook](https://learn.microsoft.com/en-us/data-engineering/playbook/understanding-data-playbook) | The data playbook provides enterprise software engineers with solutions which contain code developed to solve real-world problems. Everything in the playbook is developed with, and validated by, some of Microsoft's largest and most influential customers and partners. |

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
