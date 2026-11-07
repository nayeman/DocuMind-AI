variable "name" {
  description = "Nombre del servicio Azure AI Search"
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group donde se crea el servicio"
  type        = string
}

variable "location" {
  description = "Región Azure del servicio"
  type        = string
}

variable "sku" {
  description = "SKU del servicio AI Search (free, basic, standard, standard2, standard3)"
  type        = string
  default     = "basic"
}

variable "replica_count" {
  description = "Número de réplicas del índice"
  type        = number
  default     = 1
}

variable "partition_count" {
  description = "Número de particiones del índice"
  type        = number
  default     = 1
}

variable "tags" {
  description = "Etiquetas aplicadas al recurso"
  type        = map(string)
  default     = {}
}
