// ========== main.bicep ========== //
targetScope = 'resourceGroup'
var abbrs = loadJsonContent('./abbreviations.json')
@minLength(3)
@maxLength(20)
@description('A unique prefix for all resources in this deployment. This should be 3-20 characters long:')
param environmentName string

@description('Optional: Existing Log Analytics Workspace Resource ID')
param existingLogAnalyticsWorkspaceId string = ''

@description('Use this parameter to use an existing AI project resource ID')
param azureExistingAIProjectResourceId string = ''

@description('Optional. created by user name')
param createdBy string = contains(deployer(), 'userPrincipalName')? split(deployer().userPrincipalName, '@')[0]: deployer().objectId

// Backend runtime stack parameter removed - not needed for Copilot Studio

@minLength(1)
@description('Industry use case for deployment:')
@allowed([
  'Retail-sales-analysis'
  'Insurance-improve-customer-meetings'
])
param usecase string = 'Retail-sales-analysis'

// Secondary location parameter removed - not needed for Copilot Studio deployment

@description('Location for AI services deployment. This is the location where the Search service resource will be deployed.')
param searchServiceLocation string = resourceGroup().location

@minLength(1)
@description('GPT model deployment type:')
@allowed([
  'Standard'
  'GlobalStandard'
])
param deploymentType string = 'GlobalStandard'

@description('Name of the GPT model to deploy:')
param gptModelName string = 'gpt-4.1-mini'

@description('Version of the GPT model to deploy:')
param gptModelVersion string = '2025-04-14'

param azureOpenAIApiVersion string = '2025-01-01-preview'

param azureAiAgentApiVersion string = '2025-05-01'

@minValue(10)
@description('Capacity of the GPT deployment:')
// You can increase this, but capacity is limited per model/region, so you will get errors if you go over
// https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits
param gptDeploymentCapacity int = 150

// @description('Optional. The tags to apply to all deployed Azure resources.')
// param tags resourceInput<'Microsoft.Resources/resourceGroups@2025-04-01'>.tags = {}

@minLength(1)
@description('Name of the Text Embedding model to deploy:')
@allowed([
  'text-embedding-3-small'
])
param embeddingModel string = 'text-embedding-3-small'

@minValue(10)
@description('Capacity of the Embedding Model deployment')
param embeddingDeploymentCapacity int = 80

// Image tag parameter removed - not needed for Copilot Studio



param AZURE_LOCATION string=''
var solutionLocation = empty(AZURE_LOCATION) ? resourceGroup().location : AZURE_LOCATION

var uniqueId = toLower(uniqueString(subscription().id, environmentName, solutionLocation))

@allowed([
  'australiaeast'
  'eastus'
  'eastus2'
  'francecentral'
  'japaneast'
  'swedencentral'
  'uksouth'
  'westus'
  'westus3'
])
@metadata({
  azd:{
    type: 'location'
    usageName: [
      'OpenAI.GlobalStandard.gpt4.1-mini,100'
      'OpenAI.GlobalStandard.text-embedding-3-small,80'
    ]
  }
})
@description('Location for AI Foundry deployment. This is the location where the AI Foundry resources will be deployed.')
param aiDeploymentsLocation string

var solutionPrefix = 'da${padLeft(take(uniqueId, 12), 12, '0')}'

// ACR name parameter removed - not needed for Copilot Studio

// WorkIQ parameters removed - localhost MCP doesn't work in cloud deployments

//Get the current deployer's information
var deployerInfo = deployer()
var deployingUserPrincipalId = deployerInfo.objectId

@description('The principal type of the deploying user. Use ServicePrincipal for CI/CD pipelines with OIDC.')
@allowed(['User', 'ServicePrincipal'])
param deployingUserPrincipalType string = 'User'

// ========== Resource Group Tag ========== //
resource resourceGroupTags 'Microsoft.Resources/tags@2021-04-01' = {
  name: 'default'
  properties: {
    tags: {
      ...resourceGroup().tags
      TemplateName: 'Unified Data Analysis Agents'
      CreatedBy: createdBy
      DeploymentName: deployment().name
    }
  }
}

// ========== Managed Identity ========== //
module managedIdentityModule 'deploy_managed_identity.bicep' = {
  name: 'deploy_managed_identity'
  params: {
    miName:'${abbrs.security.managedIdentity}${solutionPrefix}'
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
  }
  scope: resourceGroup(resourceGroup().name)
}

// ==========AI Foundry and related resources ========== //
module aifoundry 'deploy_ai_foundry.bicep' = {
  name: 'deploy_ai_foundry'
  params: {
    solutionName: solutionPrefix
    solutionLocation: aiDeploymentsLocation
    deploymentType: deploymentType
    gptModelName: gptModelName
    gptModelVersion: gptModelVersion
    gptDeploymentCapacity: gptDeploymentCapacity
    embeddingModel: embeddingModel
    embeddingDeploymentCapacity: embeddingDeploymentCapacity
    managedIdentityObjectId: managedIdentityModule.outputs.managedIdentityOutput.objectId
    existingLogAnalyticsWorkspaceId: existingLogAnalyticsWorkspaceId
    azureExistingAIProjectResourceId: azureExistingAIProjectResourceId
    deployingUserPrincipalId: deployingUserPrincipalId
    deployingUserPrincipalType: deployingUserPrincipalType
    searchServiceLocation: searchServiceLocation
  }
  scope: resourceGroup(resourceGroup().name)
}

// Cosmos DB and SQL DB modules removed - not needed for Copilot Studio

// App Service components removed - not needed for Copilot Studio

// ============================================================================
// Outputs
// ============================================================================

@description('Solution prefix used for naming resources')
output SOLUTION_NAME string = solutionPrefix

@description('Name of the deployed resource group')
output RESOURCE_GROUP_NAME string = resourceGroup().name

// Cosmos DB outputs removed - not deployed for Copilot Studio
// @description('Cosmos DB account name for conversation history storage')
// output AZURE_COSMOSDB_ACCOUNT string = ''

// @description('Cosmos DB container name for storing conversations')
// output AZURE_COSMOSDB_CONVERSATIONS_CONTAINER string = ''

// @description('Cosmos DB database name for conversation history')
// output AZURE_COSMOSDB_DATABASE string = ''

@description('GPT model deployment name (e.g., gpt-4o-mini)')
output AZURE_OPENAI_DEPLOYMENT_MODEL string = gptModelName

@description('Azure OpenAI service endpoint URL')
output AZURE_OPENAI_ENDPOINT string = aifoundry.outputs.aiServicesTarget

@description('Embedding model deployment name for vector search')
output AZURE_OPENAI_EMBEDDING_MODEL string = embeddingModel

// SQL Database outputs removed - not deployed for Copilot Studio
// @description('Azure SQL database name (Azure-only mode)')
// output SQLDB_DATABASE string = ''

// @description('Azure SQL server fully qualified domain name (Azure-only mode)')
// output SQLDB_SERVER string = ''

// @description('Managed identity client ID for SQL authentication (Azure-only mode)')
// output SQLDB_USER_MID string = ''

// Backend API outputs removed - not deployed for Copilot Studio
// @description('Backend API managed identity client ID') 
// output API_UID string = managedIdentityModule.outputs.managedIdentityBackendAppOutput.clientId

@description('Azure AI Agent service endpoint URL')
output AZURE_AI_AGENT_ENDPOINT string = aifoundry.outputs.projectEndpoint

@description('Model deployment name used by Azure AI Agent')
output AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME string = gptModelName

// @description('Backend API App Service name')
// output API_APP_NAME string = ''

// @description('Backend API managed identity object/principal ID')
// output API_PID string = managedIdentityModule.outputs.managedIdentityBackendAppOutput.objectId

// @description('Backend API managed identity display name')
// output MID_DISPLAY_NAME string = managedIdentityModule.outputs.managedIdentityBackendAppOutput.name

// @description('Frontend web application URL')
// output WEB_APP_URL string = ''

@description('Deployed use case identifier (e.g., Retail-sales-analysis)')
output USE_CASE string = usecase

@description('Azure AI Search service endpoint URL')
output AZURE_AI_SEARCH_ENDPOINT string = aifoundry.outputs.aiSearchTarget

@description('Azure AI Search index name for document search')
output AZURE_AI_SEARCH_INDEX string = '${solutionPrefix}-documents'

@description('Azure AI Search service resource name')
output AZURE_AI_SEARCH_NAME string = aifoundry.outputs.aiSearchName

@description('Local path to documents folder for search indexing')
output SEARCH_DATA_FOLDER string = 'data/documents'

@description('AI Foundry connection name for Azure AI Search')
output AZURE_AI_SEARCH_CONNECTION_NAME string = aifoundry.outputs.aiSearchConnectionName

@description('Azure Storage blob service endpoint URL')
output AZURE_STORAGE_BLOB_ENDPOINT string = aifoundry.outputs.storageBlobEndpoint

@description('Azure Storage account name')
output AZURE_STORAGE_ACCOUNT_NAME string = aifoundry.outputs.storageAccountName

@description('AI Foundry connection ID for Azure AI Search')
output AZURE_AI_SEARCH_CONNECTION_ID string = aifoundry.outputs.aiSearchConnectionId

@description('Azure AI Foundry project endpoint URL')
output AZURE_AI_PROJECT_ENDPOINT string = aifoundry.outputs.projectEndpoint

@description('Azure AI Foundry resource ID for role assignments')
output AI_FOUNDRY_RESOURCE_ID string = aifoundry.outputs.aiFoundryResourceId

@description('Azure AI Foundry project name')
output AZURE_AI_PROJECT_NAME string = aifoundry.outputs.aiProjectName

@description('Azure AI Services resource name')
output AI_SERVICE_NAME string = aifoundry.outputs.aiServicesName

// @description('AI Foundry resource ID for role assignments')
// output AI_FOUNDRY_RESOURCE_ID string = aifoundry.outputs.aiFoundryResourceId
