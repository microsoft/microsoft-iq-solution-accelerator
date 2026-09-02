variable "environment" {
  description = "Short environment name included in Entra group display names."
  type        = string
  default     = "hackathon"

  validation {
    condition     = can(regex("^[a-z0-9-]{2,20}$", var.environment))
    error_message = "environment must contain 2-20 lowercase letters, numbers, or hyphens."
  }
}

variable "subscription_id" {
  description = "Azure subscription ID where Azure RBAC access is assigned."
  type        = string
}

variable "resource_group_name" {
  description = "Optional resource group to scope Azure RBAC assignments. Leave null for subscription scope."
  type        = string
  default     = null
}

variable "group_prefix" {
  description = "Prefix used in all Entra security-group display names."
  type        = string
  default     = "hackathon"
}

variable "owners" {
  description = "UPNs or Entra object IDs of the owners for each created PIM group."
  type        = set(string)
}

variable "eligible_members" {
  description = "UPNs or Entra object IDs made eligible for time-bound PIM group membership."
  type        = set(string)
  default     = []
}

variable "permanent_members" {
  description = "UPNs or Entra object IDs assigned permanently to the reader group."
  type        = set(string)
  default     = []
}

variable "pim_eligibility_duration" {
  description = "ISO 8601 duration for eligible Azure RBAC and PIM group membership."
  type        = string
  default     = "P30D"
}

variable "azure_role_definitions" {
  description = "Built-in Azure role names assigned as eligible PIM roles to the contributor group. Use least privilege."
  type        = set(string)
  default = [
    "Azure AI Developer",
    "Cognitive Services OpenAI User",
  ]
}

variable "foundry_resource_id" {
  description = "Azure AI Foundry resource ID. When supplied, Foundry roles are assigned at this resource; otherwise they use the configured Azure scope."
  type        = string
  default     = null
}

variable "fabric_capacity_resource_id" {
  description = "Optional Azure resource ID of the Fabric capacity. Supply it only when Azure RBAC on the capacity is required."
  type        = string
  default     = null
}

variable "search_service_resource_id" {
  description = "Optional Azure AI Search resource ID. Supply it only when the Foundry agent uses Search for grounding/RAG."
  type        = string
  default     = null
}

variable "search_role_definitions" {
  description = "Built-in Azure role names assigned as eligible PIM roles on the Search resource. Only applied when search_service_resource_id is set."
  type        = set(string)
  default = [
    "Search Index Data Reader",
    "Search Index Data Contributor",
    "Search Service Contributor",
  ]
}

variable "storage_account_resource_id" {
  description = "Optional Azure Storage account resource ID. Supply it only when the Foundry agent reads/writes blobs (e.g., file uploads, RAG sources)."
  type        = string
  default     = null
}

variable "storage_role_definitions" {
  description = "Built-in Azure role names assigned as eligible PIM roles on the Storage account. Only applied when storage_account_resource_id is set."
  type        = set(string)
  default = [
    "Storage Blob Data Reader",
    "Storage Blob Data Contributor",
  ]
}

variable "admin_cognitive_services_role" {
  description = "Whether to grant the administrators group eligible 'Cognitive Services User' access on the Foundry resource, for post-deploy management (matches microsoft-iq-solution-accelerator pattern)."
  type        = bool
  default     = false
}

variable "fabric_workspace_id" {
  description = "Optional Fabric workspace ID. When supplied, the administrators group is added as a Fabric workspace Admin via the Fabric REST API (requires the caller running terraform apply to be logged in with 'az login' and hold Fabric workspace admin rights)."
  type        = string
  default     = null
}

variable "directory_role_templates" {
  description = "Entra directory-role template IDs assigned permanently to the PIM administrator group. Use only roles approved by your tenant."
  type        = set(string)
  default     = []
}
