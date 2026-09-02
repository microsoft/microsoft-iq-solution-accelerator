data "azurerm_subscription" "current" {
  subscription_id = var.subscription_id
}

data "azurerm_resource_group" "target" {
  count = var.resource_group_name == null ? 0 : 1
  name  = var.resource_group_name
}

locals {
  azure_scope   = var.resource_group_name == null ? data.azurerm_subscription.current.id : data.azurerm_resource_group.target[0].id
  foundry_scope = var.foundry_resource_id == null ? local.azure_scope : var.foundry_resource_id

  group_names = {
    administrators = "${var.group_prefix}-${var.environment}-fabric-foundry-pim-administrators"
    contributors   = "${var.group_prefix}-${var.environment}-fabric-foundry-pim-contributors"
    readers        = "${var.group_prefix}-${var.environment}-fabric-foundry-readers"
  }

  role_assignments = {
    for role_name in var.azure_role_definitions :
    role_name => {
      role_name = role_name
    }
  }
}

data "azuread_client_config" "current" {}

data "azuread_user" "owners" {
  for_each            = var.owners
  user_principal_name = can(regex("@", each.value)) ? each.value : null
  object_id           = can(regex("@", each.value)) ? null : each.value
}

data "azuread_user" "eligible_members" {
  for_each            = var.eligible_members
  user_principal_name = can(regex("@", each.value)) ? each.value : null
  object_id           = can(regex("@", each.value)) ? null : each.value
}

data "azuread_user" "permanent_members" {
  for_each            = var.permanent_members
  user_principal_name = can(regex("@", each.value)) ? each.value : null
  object_id           = can(regex("@", each.value)) ? null : each.value
}

resource "azuread_group" "pim" {
  for_each = local.group_names

  display_name            = each.value
  description             = "PIM role-assignable group for ${var.environment} access."
  security_enabled        = true
  mail_enabled            = false
  assignable_to_role      = true
  prevent_duplicate_names = true
  owners                  = [for owner in data.azuread_user.owners : owner.object_id]
}

resource "azuread_group_member" "readers" {
  for_each = data.azuread_user.permanent_members

  group_object_id  = azuread_group.pim["readers"].object_id
  member_object_id = each.value.object_id
}

# Eligible memberships are activated through Entra PIM; they are not permanent group memberships.
resource "azuread_privileged_access_group_eligibility_schedule" "eligible_members" {
  for_each = data.azuread_user.eligible_members

  group_id        = azuread_group.pim["contributors"].object_id
  principal_id    = each.value.object_id
  assignment_type = "member"
  duration        = var.pim_eligibility_duration
  justification   = "Eligible hackathon contributor access managed through Terraform."
}

data "azurerm_role_definition" "azure_roles" {
  for_each = local.role_assignments

  name = each.value.role_name
}

resource "azurerm_pim_eligible_role_assignment" "azure_roles" {
  for_each = local.role_assignments

  scope              = local.foundry_scope
  role_definition_id = "${local.foundry_scope}${data.azurerm_role_definition.azure_roles[each.key].id}"
  principal_id       = azuread_group.pim["contributors"].object_id
  justification      = "Eligible ${each.value.role_name} access for ${var.environment}."

  schedule {
    expiration {
      duration_days = 30
    }
  }
}

# This is intentionally separate from Foundry permissions. Fabric workspace roles
# are assigned by the Fabric service, not Azure RBAC. Capacity RBAC is optional.
data "azurerm_role_definition" "fabric_capacity_contributor" {
  count = var.fabric_capacity_resource_id == null ? 0 : 1

  name = "Contributor"
}

resource "azurerm_pim_eligible_role_assignment" "fabric_capacity_contributor" {
  count = var.fabric_capacity_resource_id == null ? 0 : 1

  scope              = var.fabric_capacity_resource_id
  role_definition_id = "${var.fabric_capacity_resource_id}${data.azurerm_role_definition.fabric_capacity_contributor[0].id}"
  principal_id       = azuread_group.pim["administrators"].object_id
  justification      = "Eligible Fabric capacity administration for ${var.environment}."

  schedule {
    expiration {
      duration_days = 30
    }
  }
}

# Optional: Azure AI Search roles for the contributor group, only when the Foundry
# agent uses Search for grounding/RAG.
data "azurerm_role_definition" "search_roles" {
  for_each = var.search_service_resource_id == null ? {} : { for r in var.search_role_definitions : r => r }

  name = each.value
}

resource "azurerm_pim_eligible_role_assignment" "search_roles" {
  for_each = var.search_service_resource_id == null ? {} : { for r in var.search_role_definitions : r => r }

  scope              = var.search_service_resource_id
  role_definition_id = "${var.search_service_resource_id}${data.azurerm_role_definition.search_roles[each.key].id}"
  principal_id       = azuread_group.pim["contributors"].object_id
  justification      = "Eligible ${each.value} access for ${var.environment}."

  schedule {
    expiration {
      duration_days = 30
    }
  }
}

# Optional: Storage roles for the contributor group, only when the Foundry agent
# reads/writes blobs (file uploads, RAG sources).
data "azurerm_role_definition" "storage_roles" {
  for_each = var.storage_account_resource_id == null ? {} : { for r in var.storage_role_definitions : r => r }

  name = each.value
}

resource "azurerm_pim_eligible_role_assignment" "storage_roles" {
  for_each = var.storage_account_resource_id == null ? {} : { for r in var.storage_role_definitions : r => r }

  scope              = var.storage_account_resource_id
  role_definition_id = "${var.storage_account_resource_id}${data.azurerm_role_definition.storage_roles[each.key].id}"
  principal_id       = azuread_group.pim["contributors"].object_id
  justification      = "Eligible ${each.value} access for ${var.environment}."

  schedule {
    expiration {
      duration_days = 30
    }
  }
}

# Optional: matches the microsoft-iq-solution-accelerator pattern of granting the
# deploying/admin user 'Cognitive Services User' for post-deploy management of the
# Foundry resource itself (separate from data-plane developer roles above).
data "azurerm_role_definition" "admin_cognitive_services_user" {
  count = var.admin_cognitive_services_role && var.foundry_resource_id != null ? 1 : 0

  name = "Cognitive Services User"
}

resource "azurerm_pim_eligible_role_assignment" "admin_cognitive_services_user" {
  count = var.admin_cognitive_services_role && var.foundry_resource_id != null ? 1 : 0

  scope              = var.foundry_resource_id
  role_definition_id = "${var.foundry_resource_id}${data.azurerm_role_definition.admin_cognitive_services_user[0].id}"
  principal_id       = azuread_group.pim["administrators"].object_id
  justification      = "Eligible Foundry resource management for ${var.environment}."

  schedule {
    expiration {
      duration_days = 30
    }
  }
}

# Fabric workspace roles (Admin/Member/Contributor/Viewer) are NOT Azure RBAC and have
# no Terraform provider. This calls the Fabric REST API directly, mirroring the
# step_workspace_admins.py pattern used elsewhere: it adds the administrators group
# as a Fabric workspace Admin. Requires the identity running `terraform apply` to be
# logged in via `az login` and already hold Fabric workspace admin rights.
resource "null_resource" "fabric_workspace_admin_group" {
  count = var.fabric_workspace_id == null ? 0 : 1

  triggers = {
    workspace_id = var.fabric_workspace_id
    group_id     = azuread_group.pim["administrators"].object_id
  }

  provisioner "local-exec" {
    interpreter = ["pwsh", "-Command"]
    command     = <<-EOT
      $ErrorActionPreference = "Stop"
      $token = (az account get-access-token --resource "https://api.fabric.microsoft.com" --query accessToken -o tsv)
      $headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }
      $body = @{
        principal = @{ id = "${azuread_group.pim["administrators"].object_id}"; type = "Group" }
        role      = "Admin"
      } | ConvertTo-Json
      Invoke-RestMethod -Method Post -Uri "https://api.fabric.microsoft.com/v1/workspaces/${var.fabric_workspace_id}/roleAssignments" -Headers $headers -Body $body
    EOT
  }
}

# Directory roles must first be activated in the tenant, then can be assigned to a role-assignable group.
resource "azuread_directory_role" "directory_roles" {
  for_each = var.directory_role_templates

  template_id = each.value
}

resource "azuread_directory_role_assignment" "pim_administrator_roles" {
  for_each = azuread_directory_role.directory_roles

  role_id             = each.value.template_id
  principal_object_id = azuread_group.pim["administrators"].object_id
}
