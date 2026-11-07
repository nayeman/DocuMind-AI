variable "name" {
  description = "Nombre globalmente único de la Storage Account (3-24 chars, solo minúsculas y dígitos)"
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group donde se crea la Storage Account"
  type        = string
}

variable "location" {
  description = "Región Azure de la Storage Account"
  type        = string
}

variable "container_name" {
  description = "Nombre del contenedor Blob para documentos"
  type        = string
  default     = "documind-documents"
}

variable "account_tier" {
  description = "Tier de la Storage Account (Standard o Premium)"
  type        = string
  default     = "Standard"
}

variable "replication_type" {
  description = "Tipo de replicación (LRS, GRS, ZRS, etc.)"
  type        = string
  default     = "LRS"
}

variable "tags" {
  description = "Etiquetas aplicadas a la Storage Account"
  type        = map(string)
  default     = {}
}
