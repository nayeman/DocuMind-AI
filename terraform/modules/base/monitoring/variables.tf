variable "name" {
  description = "Nombre del Log Analytics Workspace"
  type        = string
}

variable "resource_group_name" {
  description = "Nombre del Resource Group destino"
  type        = string
}

variable "location" {
  description = "Región Azure"
  type        = string
}

variable "container_app_name" {
  description = "Nombre de la Container App incluida en la consulta de alerta"
  type        = string
}

variable "alerts_enabled" {
  description = "Crea alertas solo si también se proporciona alert_email"
  type        = bool
  default     = false
}

variable "alert_email" {
  description = "Correo que recibe las alertas; no se crea ningún receptor si está vacío"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Etiquetas aplicadas a los recursos"
  type        = map(string)
  default     = {}
}
