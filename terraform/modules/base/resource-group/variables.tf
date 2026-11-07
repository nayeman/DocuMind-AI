variable "name" {
  description = "Nombre del Resource Group"
  type        = string
}

variable "location" {
  description = "Región Azure del Resource Group"
  type        = string
}

variable "tags" {
  description = "Etiquetas aplicadas al Resource Group"
  type        = map(string)
  default     = {}
}
