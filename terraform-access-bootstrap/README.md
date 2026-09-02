# Terraform access bootstrap

## Prerequisites

Install:

- [Terraform](https://developer.hashicorp.com/terraform/install) 1.6 or later.
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).

Sign in to the correct tenant and subscription:

```powershell
az login --tenant <tenant-id>
az account set --subscription <subscription-id>
```

## Required permissions to run this script

| Area | Minimum practical permission |
|---|---|
| Azure subscription/resource-group RBAC | `Owner` or `User Access Administrator` at the configured Azure scope, plus read access to that scope |
| Create role-assignable Entra groups | `Privileged Role Administrator` or `Global Administrator` |
| Add PIM eligible group memberships | `Privileged Role Administrator` or `Global Administrator` |
| Activate and assign Entra directory roles | `Privileged Role Administrator` or `Global Administrator` |
| Read users referenced by UPN/object ID | `Directory Readers`, or one of the directory admin roles above |

The tenant must allow PIM, and the operator must have an active Entra role with permission to manage privileged access. Complete MFA first if the tenant requires it via Conditional Access.

## Run (interactive, recommended for non-technical users)

```powershell
.\run.ps1
```

This prompts for subscription, environment name, an **existing** resource group, and the Foundry resource, then writes `terraform.tfvars` and runs `terraform init`/`plan`/`apply` for you. There is no location prompt and no "create new resource group" option — this script only assigns access to resources that already exist; it does not provision anything.

## Run (manual)

1. Copy the example parameters file:

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` and set at minimum: `subscription_id`, `resource_group_name`, `foundry_resource_id`, `owners`, `eligible_members`, `permanent_members`.

   Optional, only if needed: `search_service_resource_id` (AI Search grounding/RAG roles), `storage_account_resource_id` (blob roles), `admin_cognitive_services_role` (admins get `Cognitive Services User` on the Foundry resource), `fabric_capacity_resource_id` (Fabric capacity `Contributor`), `fabric_workspace_id` (see **Fabric workspace roles** below).

3. Run:

```powershell
terraform init
terraform fmt -check
terraform validate
terraform plan -out tfplan
terraform apply tfplan
```

## Test

1. Sign in as one of the `eligible_members` users.
2. In Entra PIM **My roles**, activate the contributor-group membership.
3. In Azure PIM, activate the assigned role.
4. Verify access:

```powershell
az login
az account show
az group list --subscription <subscription-id> --output table
```

5. After the activation expires, rerun the command and confirm the role is no longer active.

## Fabric workspace roles

Fabric workspace roles (Admin/Member/Contributor/Viewer) are **not** Azure RBAC — there is no Terraform provider for them. If you set `fabric_workspace_id`, `terraform apply` calls the Fabric REST API directly (via a `local-exec` provisioner running `az account get-access-token` + `Invoke-RestMethod`) to add the administrators group as a Fabric workspace **Admin**. This requires:

- The identity running `terraform apply` to be signed in via `az login`.
- That identity to already hold Fabric workspace Admin rights (to add other admins).

Leave `fabric_workspace_id` unset to skip this and assign Fabric workspace roles manually in the Fabric portal instead.

## Teardown

```powershell
terraform destroy
```

This removes the groups and access assignments created by this script. It does not delete Azure resources created by event participants.
