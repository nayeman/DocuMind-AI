variable "name" {
  description = "Nombre de la red virtual"
  type        = string
}

variable "resource_group_name" {
  description = "Grupo de recursos donde se crea la red"
  type        = string
}

variable "location" {
  description = "Región Azure de la red virtual"
  type        = string
}

variable "address_space" {
  description = "Espacio de direcciones CIDR de la red virtual"
  type        = string

  validation {
    condition     = can(cidrhost(var.address_space, 0))
    error_message = "address_space debe ser un bloque CIDR válido."
  }
}

variable "container_apps_subnet_prefix" {
  description = "CIDR exclusivo para el entorno de Container Apps"
  type        = string

  validation {
    condition     = can(cidrhost(var.container_apps_subnet_prefix, 0))
    error_message = "container_apps_subnet_prefix debe ser un bloque CIDR válido."
  }
}

variable "postgres_subnet_prefix" {
  description = "CIDR exclusivo y delegado para PostgreSQL Flexible"
  type        = string

  validation {
    condition     = can(cidrhost(var.postgres_subnet_prefix, 0))
    error_message = "postgres_subnet_prefix debe ser un bloque CIDR válido."
  }
}

variable "postgres_private_dns_zone_name" {
  description = "Zona DNS privada para PostgreSQL Flexible"
  type        = string

  validation {
    condition     = endswith(var.postgres_private_dns_zone_name, ".postgres.database.azure.com")
    error_message = "La zona DNS debe terminar en .postgres.database.azure.com."
  }
}

variable "tags" {
  description = "Etiquetas aplicadas a los recursos de red que las soportan"
  type        = map(string)
  default     = {}
}
