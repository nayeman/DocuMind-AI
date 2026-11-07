variable "name" {
  description = "Nombre de la identidad user-assigned"
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group donde se crea la identidad"
  type        = string
}

variable "location" {
  description = "Región Azure de la identidad"
  type        = string
}

variable "tags" {
  description = "Etiquetas aplicadas a la identidad"
  type        = map(string)
  default     = {}
}
