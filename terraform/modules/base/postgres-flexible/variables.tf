variable "name" {
  description = "Nombre del servidor PostgreSQL Flexible"
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group donde se crea el servidor"
  type        = string
}

variable "location" {
  description = "Región Azure del servidor"
  type        = string
}

variable "server_version" {
  description = "Versión mayor de PostgreSQL"
  type        = string
  default     = "16"
}

variable "administrator_login" {
  description = "Usuario administrador de PostgreSQL"
  type        = string
}

variable "administrator_password" {
  description = "Password del administrador de PostgreSQL"
  type        = string
  sensitive   = true
}

variable "sku_name" {
  description = "SKU del servidor PostgreSQL Flexible"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "storage_mb" {
  description = "Almacenamiento en MB"
  type        = number
  default     = 32768
}

variable "backup_retention_days" {
  description = "Días de retención de backups"
  type        = number
  default     = 7
}

variable "public_network_access_enabled" {
  description = "Habilita acceso público al servidor"
  type        = bool
  default     = true
}

variable "delegated_subnet_id" {
  description = "ID de la subred delegada para acceso privado; null usa red pública"
  type        = string
  default     = null

  validation {
    condition     = (var.delegated_subnet_id == null) == (var.private_dns_zone_id == null)
    error_message = "delegated_subnet_id y private_dns_zone_id deben definirse juntos."
  }
}

variable "private_dns_zone_id" {
  description = "ID de la zona DNS privada para acceso privado; null usa red pública"
  type        = string
  default     = null
}

variable "allow_azure_services" {
  description = "Permite el firewall 0.0.0.0 (servicios Azure). Desactivar con VNet/private endpoint."
  type        = bool
  default     = true
}

variable "database_name" {
  description = "Nombre de la base de datos"
  type        = string
  default     = "newspilot"
}

variable "database_charset" {
  description = "Charset de la base de datos"
  type        = string
  default     = "UTF8"
}

variable "database_collation" {
  description = "Collation de la base de datos"
  type        = string
  default     = "en_US.utf8"
}

variable "allowed_ip" {
  description = "IP pública opcional para acceso local"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Etiquetas aplicadas al servidor"
  type        = map(string)
  default     = {}
}
