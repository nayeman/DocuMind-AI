variable "name" {
  description = "Nombre de la Container App"
  type        = string
}

variable "environment_name" {
  description = "Nombre del Container App Environment"
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group donde se despliega"
  type        = string
}

variable "location" {
  description = "Región Azure"
  type        = string
}

variable "infrastructure_subnet_id" {
  description = "ID de la subred delegada para el entorno de Container Apps"
  type        = string
  default     = null
}

variable "log_analytics_workspace_id" {
  description = "ID del recurso Log Analytics Workspace que recibe los logs del entorno"
  type        = string
  default     = null
}

variable "workload_profile_enabled" {
  description = "Crea el perfil Consumption necesario para Container Apps sobre VNet"
  type        = bool
  default     = false
}

variable "image" {
  description = "Imagen del contenedor; vacío = no crear la Container App"
  type        = string
  default     = ""
}

variable "container_cpu" {
  description = "CPU del contenedor"
  type        = number
  default     = 0.5
}

variable "container_memory" {
  description = "Memoria del contenedor"
  type        = string
  default     = "1Gi"
}

variable "registry_server" {
  description = "Login server del registry"
  type        = string
}

variable "registry_username" {
  description = "Usuario admin para autenticación con el ACR"
  type        = string
  default     = null
}

variable "registry_password" {
  description = "Contraseña admin para autenticación con el ACR"
  type        = string
  default     = null
  sensitive   = true
}

variable "registry_identity_id" {
  description = "ID de la identidad administrada con permiso AcrPull"
  type        = string
}

variable "agent_model" {
  description = "Nombre del deployment de chat en Azure OpenAI"
  type        = string
}

variable "direct_secret_values" {
  description = "Mapa nombre de secreto -> valor directo (compatible con express environments)"
  type        = map(string)
  default     = {}
  sensitive   = true
}

variable "optional_secret_envs" {
  description = "Mapa env->nombre de secreto opcional"
  type        = map(string)
  default     = {}
}

variable "optional_plain_envs" {
  description = "Mapa env->valor de variables planas opcionales"
  type        = map(string)
  default     = {}
}

variable "min_replicas" {
  description = "Réplicas mínimas"
  type        = number
  default     = 1
}

variable "max_replicas" {
  description = "Réplicas máximas"
  type        = number
  default     = 1
}

variable "ingress_port" {
  description = "Puerto interno y de ingress"
  type        = number
  default     = 8000
}

variable "tags" {
  description = "Etiquetas aplicadas a los recursos"
  type        = map(string)
  default     = {}
}
