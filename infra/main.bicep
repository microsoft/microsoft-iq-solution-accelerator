metadata name = 'Unified data foundation with Fabric solution accelerator'
metadata description = '''CSA CTO Gold Standard Solution Accelerator for Unified Data Foundation with Fabric.
'''
@minLength(1)
@maxLength(20)
@description('Optional. A friendly string representing the application/solution name to give to all resource names in this deployment. This should be 3-16 characters long.')
param solutionName string = 'udfwfsa'

@maxLength(5)
@description('Optional. A unique text value for the solution. This is used to ensure resource names are unique for global resources. Defaults to a 5-character substring of the unique string generated from the subscription ID, resource group name, and solution name.')
param solutionUniqueText string = substring(uniqueString(subscription().id, resourceGroup().name, solutionName), 0, 5)

@minLength(3)
@metadata({ azd: { type: 'location' } })
@description('Optional. Azure region for all services. Defaults to the tenant\' location to avoid usage of Microsoft Fabric multi-geo capabilities.')
param location string = resourceGroup().location

@description('Optional. Enable/Disable usage telemetry for module.')
param enableTelemetry bool = true

@description('Optional. An array of user object IDs or service principal object IDs that will be assigned the Fabric Capacity Admin role. This can be used to add additional admins beyond the default admin which is the user assigned managed identity created as part of this deployment.')
param fabricAdminMembers array = []

@allowed([
  'F2'
  'F4'
  'F8'
  'F16'
  'F32'
  'F64'
  'F128'
  'F256'
  'F512'
  'F1024'
  'F2048'
])
@description('Optional. SKU tier of the Fabric resource.')
param skuName string = 'F2'

@description('Optional. Name of an existing Fabric capacity to use. If empty, a new capacity will be created.')
param existingFabricCapacityName string = ''

@description('Optional. Created by user name.')
param createdBy string = contains(deployer(), 'userPrincipalName') ? split(deployer().userPrincipalName, '@')[0] : deployer().objectId

var useExistingFabricCapacity = !empty(existingFabricCapacityName)

var solutionSuffix = toLower(trim(replace(
  replace(
    replace(replace(replace(replace('${solutionName}${solutionUniqueText}', '-', ''), '_', ''), '.', ''), '/', ''),
    ' ',
    ''
  ),
  '*',
  ''
)))

// ========== Resource Group Tag ========== //
resource resourceGroupTags 'Microsoft.Resources/tags@2021-04-01' = {
  name: 'default'
  properties: {
    tags: union(
      resourceGroup().tags,
      {
        TemplateName: 'Unified Data Foundation with Fabric'
        CreatedBy: createdBy
        Type: 'Non-WAF'
      }
    )
  }
}

// var userAssignedIdentityResourceName = 'id-${solutionSuffix}'
// module userAssignedIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.1' = {
//   name: take('avm.res.managed-identity.user-assigned-identity.${userAssignedIdentityResourceName}', 64)
//   params: {
//     name: userAssignedIdentityResourceName
//     location: location
//     enableTelemetry: enableTelemetry
//   }
// }

var fabricCapacityResourceName = useExistingFabricCapacity ? existingFabricCapacityName : 'fc${solutionSuffix}'
var fabricCapacityDefaultAdmins = deployer().?userPrincipalName == null
  ? [deployer().objectId]
  : [deployer().userPrincipalName]
var fabricTotalAdminMembers = union(fabricCapacityDefaultAdmins, fabricAdminMembers)
module newFabricCapacity 'br/public:avm/res/fabric/capacity:0.1.1' = if (!useExistingFabricCapacity) {
  name: take('avm.res.fabric.capacity.${fabricCapacityResourceName}', 64)
  params: {
    name: fabricCapacityResourceName
    location: location
    enableTelemetry: enableTelemetry
    skuName: skuName
    adminMembers: fabricTotalAdminMembers
  }
}

// Outputs for AZD
@description('The location the resources were deployed to')
output AZURE_LOCATION string = location

@description('The name of the resource group')
output AZURE_RESOURCE_GROUP string = resourceGroup().name

@description('The name of the Fabric capacity resource')
output AZURE_FABRIC_CAPACITY_NAME string = fabricCapacityResourceName

@description('The identities assigned as Fabric Capacity Admin members when a new capacity is created. When an existing capacity is used, this value is not applied and is provided for informational purposes only.')
output AZURE_FABRIC_CAPACITY_ADMINISTRATORS array = fabricTotalAdminMembers

@description('The unique solution suffix of the deployed resources')
output SOLUTION_SUFFIX string = solutionSuffix
