# About `definitions` folder

This directory contains Microsoft Fabric item definitions downloaded from the Fabric workspace 'Microsoft IQ - dev'. Definitions stored here are deployed to the Fabric workspace as a post-deployment step in the [`fabric_solution_installer.ipynb`](../../infra/fabric/deploy/fabric_solution_installer.ipynb) notebook.

Definitions are obtained leveraging Fabric REST API GET DEFINITION operations, such as the generic [Get Item Definition](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/get-item-definition?tabs=HTTP) API or item-type-specific definition APIs.

## Ontology Definitions

Ontology definitions are downloaded using the `Get-FabricOntologyDefinition.ps1` script located in `infra\scripts\utils`.

**Prerequisites**: Authenticate using Azure Developer CLI or Azure CLI:
```powershell
azd auth login  # or: az login
```

**Usage**:
```powershell
.\infra\scripts\utils\Get-FabricOntologyDefinition.ps1 `
    -WorkspaceId "aaaabbbb-0000-cccc-1111-dddd2222eeee" `
    -OntologyId "bbbbcccc-1111-dddd-2222-eeee3333ffff"
```

Downloads to `src/fabric/definitions/[OntologyName].Ontology` using the ontology's display name from Fabric.

**Finding IDs**: Workspace and ontology IDs are in the Fabric portal URL:
```
https://app.fabric.microsoft.com/groups/{workspaceId}/ontologies/{ontologyId}
```

**Updating**: Re-run the script with the same parameters to update existing definitions.


