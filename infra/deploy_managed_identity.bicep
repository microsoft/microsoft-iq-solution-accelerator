// ========== Managed Identity ========== //
targetScope = 'resourceGroup'

@minLength(1)
@maxLength(20)
@description('Solution Name')
param solutionName string

@description('Solution Location')
param solutionLocation string

@description('Managed Identity Name')
param miName string

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: miName
  location: solutionLocation
  tags: {
    app: solutionName
    location: solutionLocation
  }
}

@description('The managed identity details including id, objectId, clientId, and name.')
output managedIdentityOutput object = {
  id: managedIdentity.id
  objectId: managedIdentity.properties.principalId
  clientId: managedIdentity.properties.clientId
  name: miName
}
