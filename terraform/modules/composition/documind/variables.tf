variable "environment" {
  description = "Entorno de despliegue (dev, stg, qa, uat, prod, dr)"
  type        = string
  validation {
    condition     = contains(["dev", "stg", "qa", "uat", "prod", "dr"], var.environment)
    error_message = "Permitidos: dev, stg, qa, uat, prod, dr."
  }
}

variable "project_name" {
  description = "Nombre del proyecto (ej. documind)"
  type        = string
}

variable "owner_email" {
  description = "Correo del responsable técnico o de negocio"
  type        = string
}

variable "cost_center" {
  description = "Centro de costos. Formato: CC-XXXXXX"
  type        = string
  validation {
    condition     = can(regex("^CC-[0-9]{4,6}$", var.cost_center))
    error_message = "CostCenter debe ser CC-XXXXXX (4-6 dígitos)."
  }
}

variable "location" {
  description = "Región Azure donde se despliegan los recursos"
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Nombre del Resource Group principal"
  type        = string
  default     = "rg-documind"
}

variable "container_app_name" {
  description = "Nombre de la Container App"
  type        = string
  default     = "ca-documind"
}

variable "acr_name_prefix" {
  description = "Prefijo del Azure Container Registry (solo alfanumérico)"
  type        = string
  default     = "documindacr"
}

variable "image_tag" {
  description = "Tag de la imagen publicada en ACR; vacío = no crear Container App todavía"
  type        = string
  default     = ""
}

variable "chat_model_name" {
  description = "Nombre del modelo/deployment de chat en Azure OpenAI"
  type        = string
  default     = "gpt-4o"
}

variable "chat_model_version" {
  description = "Versión del modelo de chat"
  type        = string
  default     = "2024-11-20"
}

variable "embedding_model_name" {
  description = "Nombre del modelo/deployment de embeddings en Azure OpenAI"
  type        = string
  default     = "text-embedding-3-small"
}

variable "embedding_model_version" {
  description = "Versión del modelo de embeddings"
  type        = string
  default     = "1"
}

variable "ai_search_sku" {
  description = "SKU del servicio Azure AI Search (free, basic, standard)"
  type        = string
  default     = "basic"
}

variable "whatsapp_phone_number_id" {
  description = "Phone Number ID de WhatsApp Cloud API"
  type        = string
  default     = ""
}

variable "min_replicas" {
  description = "Réplicas mínimas de la Container App"
  type        = number
  default     = 1
}

variable "max_replicas" {
  description = "Réplicas máximas de la Container App"
  type        = number
  default     = 1
}

variable "alerts_enabled" {
  description = "Crea alertas de Azure Monitor cuando también se configure alert_email"
  type        = bool
  default     = false
}

variable "embedding_capacity" {
  description = "Capacidad del deployment de embeddings"
  type        = number
  default     = 20
}

variable "alert_email" {
  description = "Correo del receptor de alertas de Azure Monitor; vacío impide crear alertas"
  type        = string
  default     = ""
}
