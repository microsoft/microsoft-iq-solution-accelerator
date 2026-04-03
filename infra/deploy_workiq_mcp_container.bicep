// deploy_workiq_mcp_container.bicep - WorkIQ MCP Server Container Deployment

param location string = resourceGroup().location
param environmentName string = 'workiq-mcp-env'
param containerAppName string = 'workiq-mcp-server'
param containerImage string = 'gpickettacr.azurecr.io/workiq-mcp:v4'
param workiqUser string
param managedIdentityName string = '${containerAppName}-identity'
param acrName string = 'gpickettacr'

// Get existing ACR
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = {
  name: acrName
}

// Container Apps Environment
resource environment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  properties: {
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

// Managed Identity for WorkIQ authentication
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
}

// Role assignment to allow pulling from ACR
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, managedIdentity.id, '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull role
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Container App for WorkIQ MCP Server
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  dependsOn: [
    acrPullRoleAssignment
  ]
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    environmentId: environment.id
    configuration: {
      registries: [
        {
          server: acr.properties.loginServer 
          identity: managedIdentity.id
        }
      ]
      ingress: {
        external: true
        targetPort: 3000
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      secrets: [
        {
          name: 'workiq-user'
          value: workiqUser
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'workiq-mcp'
          image: containerImage
          env: [
            {
              name: 'PORT'
              value: '3000'
            }
            {
              name: 'WORKIQ_USER'
              secretRef: 'workiq-user'
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: managedIdentity.properties.clientId
            }
          ]
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output containerAppName string = containerApp.name
output managedIdentityClientId string = managedIdentity.properties.clientId