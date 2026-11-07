variable "name" {
  description = "Nombre del Azure Container Registry (solo alfanumérico)"
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group donde se crea el ACR"
  type        = string
}

variable "location" {
  description = "Región Azure del ACR"
  type        = string
}

variable "sku" {
  description = "SKU del ACR"
  type        = string
  default     = "Basic"
}

variable "admin_enabled" {
  description = "Habilita credenciales admin del ACR (solo para una excepción aprobada)"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Etiquetas aplicadas al ACR"
  type        = map(string)
  default     = {}
}
