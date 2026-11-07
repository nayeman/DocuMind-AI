variable "name" {
  description = "Nombre globalmente único del Key Vault"
  type        = string
}

variable "location" {
  description = "Región Azure"
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group donde se despliega"
  type        = string
}

variable "tenant_id" {
  description = "Tenant Entra ID asociado al Key Vault"
  type        = string
}

variable "tags" {
  description = "Etiquetas aplicadas al recurso"
  type        = map(string)
  default     = {}
}
