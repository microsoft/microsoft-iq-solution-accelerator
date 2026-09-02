output "azure_rbac_scope" {
  description = "Scope at which Foundry PIM eligible roles were assigned."
  value       = local.foundry_scope
}

output "pim_group_ids" {
  description = "Object IDs for the created role-assignable Entra security groups."
  value = {
    for key, group in azuread_group.pim : key => group.object_id
  }
}

output "pim_group_display_names" {
  description = "Display names for the created role-assignable Entra security groups."
  value = {
    for key, group in azuread_group.pim : key => group.display_name
  }
}
