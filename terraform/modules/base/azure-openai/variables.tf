variable "name" {
  description = "Nombre de la cuenta Azure OpenAI"
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group donde se crea la cuenta"
  type        = string
}

variable "location" {
  description = "Región Azure de la cuenta"
  type        = string
}

variable "custom_subdomain_name" {
  description = "Subdominio personalizado de la cuenta"
  type        = string
}

variable "sku_name" {
  description = "SKU de la cuenta Azure OpenAI"
  type        = string
  default     = "S0"
}

variable "public_network_access_enabled" {
  description = "Habilita acceso público a la cuenta"
  type        = bool
  default     = true
}

variable "local_auth_enabled" {
  description = "Habilita autenticación con API key"
  type        = bool
  default     = false
}

variable "model_name" {
  description = "Nombre del modelo/deployment principal (ej. chat)"
  type        = string
}

variable "model_version" {
  description = "Versión del modelo principal"
  type        = string
}

variable "capacity" {
  description = "Capacidad del deployment principal (unidades)"
  type        = number
  default     = 1
}

variable "embedding_model_name" {
  description = "Nombre opcional del modelo/deployment de embeddings (ej. text-embedding-3-small)"
  type        = string
  default     = ""
}

variable "embedding_model_version" {
  description = "Versión opcional del modelo de embeddings"
  type        = string
  default     = "1"
}

variable "embedding_capacity" {
  description = "Capacidad del deployment de embeddings"
  type        = number
  default     = 1
}

variable "version_upgrade_option" {
  description = "Política de actualización del modelo"
  type        = string
  default     = "OnceNewDefaultVersionAvailable"
}

variable "rai_policy_name" {
  description = "Política de Responsible AI"
  type        = string
  default     = "Microsoft.DefaultV2"
}

variable "tags" {
  description = "Etiquetas aplicadas a la cuenta"
  type        = map(string)
  default     = {}
}
