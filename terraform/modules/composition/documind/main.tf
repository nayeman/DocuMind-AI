locals {
  suffix             = random_string.suffix.result
  kv_suffix          = random_string.kv_suffix.result
  storage_name_clean = replace(lower(var.acr_name_prefix), "-", "")

  image = var.image_tag != "" ? "${module.acr.login_server}/documind-api:${var.image_tag}" : ""

  # ─── Secretos: valores directos leídos desde Key Vault por Terraform ──────────
  # (Azure express environments no soportan KV URI references en Container Apps)
  direct_secret_values = {
    "whatsapp-access-token" = data.azurerm_key_vault_secret.whatsapp_access_token.value
    "whatsapp-app-secret"   = data.azurerm_key_vault_secret.whatsapp_app_secret.value
    "whatsapp-verify-token" = data.azurerm_key_vault_secret.whatsapp_verify_token.value
  }

  # ─── Variables de entorno mapeadas a secretos internos del Container App ──────
  optional_secret_envs = {
    WHATSAPP_ACCESS_TOKEN         = "whatsapp-access-token"
    WHATSAPP_APP_SECRET           = "whatsapp-app-secret"
    WHATSAPP_WEBHOOK_VERIFY_TOKEN = "whatsapp-verify-token"
  }

  # ─── Variables de entorno planas (se omiten si están vacías) ─────────────────
  optional_plain_envs = {
    for name, value in {
      AZURE_CLIENT_ID                   = module.identity.client_id
      AZURE_SEARCH_ENDPOINT             = module.ai_search.endpoint
      AZURE_SEARCH_INDEX_NAME           = "documind-index"
      AZURE_STORAGE_ACCOUNT_NAME        = module.storage.name
      AZURE_OPENAI_ENDPOINT             = module.foundry.endpoint
      AZURE_OPENAI_CHAT_DEPLOYMENT      = var.chat_model_name
      AZURE_OPENAI_EMBEDDING_DEPLOYMENT = var.embedding_model_name
      WHATSAPP_PHONE_NUMBER_ID          = var.whatsapp_phone_number_id
      APP_ENV                           = var.environment
    } : name => value if value != ""
  }
}

# ─── Random suffixes para nombres únicos ────────────────────────────────────────
resource "random_string" "suffix" {
  length  = 4
  lower   = true
  upper   = false
  numeric = true
  special = false
}

resource "random_string" "kv_suffix" {
  length  = 8
  lower   = true
  upper   = false
  numeric = true
  special = false
}

# ─── Data source del tenant actual ──────────────────────────────────────────────
data "azurerm_client_config" "current" {}

# ─── Secretos de WhatsApp leídos desde Key Vault ────────────────────────────────
# Se leen aquí y se pasan como valores directos al Container App
# (Azure Student suscripción no soporta KV URI references en Container Apps)
data "azurerm_key_vault_secret" "whatsapp_access_token" {
  name         = "whatsapp-access-token"
  key_vault_id = module.key_vault.id
  depends_on   = [module.key_vault]
}

data "azurerm_key_vault_secret" "whatsapp_app_secret" {
  name         = "whatsapp-app-secret"
  key_vault_id = module.key_vault.id
  depends_on   = [module.key_vault]
}

data "azurerm_key_vault_secret" "whatsapp_verify_token" {
  name         = "whatsapp-verify-token"
  key_vault_id = module.key_vault.id
  depends_on   = [module.key_vault]
}

# ─── Resource Group ─────────────────────────────────────────────────────────────
module "resource_group" {
  source = "../../base/resource-group"

  name     = var.resource_group_name
  location = var.location
  tags     = local.base_tags
}

# ─── Azure Container Registry ───────────────────────────────────────────────────
module "acr" {
  source = "../../base/container-registry"

  name                = "${var.acr_name_prefix}${local.suffix}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  admin_enabled       = true
  tags                = local.base_tags
}

# ─── User-Assigned Managed Identity ─────────────────────────────────────────────
module "identity" {
  source = "../../base/user-assigned-identity"

  name                = "id-${var.container_app_name}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = local.base_tags
}

# ─── Key Vault ──────────────────────────────────────────────────────────────────
module "key_vault" {
  source = "../../base/key-vault"

  name                = "kv-documind-${local.kv_suffix}"
  tenant_id           = data.azurerm_client_config.current.tenant_id
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags = merge(local.base_tags, local.security_tags, {
    Description = "Key Vault de secretos de runtime — ${var.project_name} ${var.environment}"
  })
}

# ─── Azure AI Search ────────────────────────────────────────────────────────────
module "ai_search" {
  source = "../../base/ai-search"

  name                = "srch-documind-${local.suffix}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  sku                 = var.ai_search_sku
  tags = merge(local.base_tags, local.security_tags, {
    Description = "AI Search (vectorial) — ${var.project_name} ${var.environment}"
  })
}

# ─── Storage Account ────────────────────────────────────────────────────────────
module "storage" {
  source = "../../base/storage-account"

  name                = "st${local.storage_name_clean}${local.suffix}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  container_name      = "documind-documents"
  tags = merge(local.base_tags, local.security_tags, {
    Description = "Almacén de documentos originales — ${var.project_name} ${var.environment}"
  })
}

# ─── Azure OpenAI / Foundry (Chat + Embeddings en una sola cuenta) ────────────
module "foundry" {
  source = "../../base/azure-openai"

  name                    = "aoai-documind-${local.suffix}"
  resource_group_name     = module.resource_group.name
  location                = module.resource_group.location
  custom_subdomain_name   = "aoai-documind-${local.suffix}"
  model_name              = var.chat_model_name
  model_version           = var.chat_model_version
  embedding_model_name    = var.embedding_model_name
  embedding_model_version = var.embedding_model_version
  embedding_capacity      = var.embedding_capacity
  local_auth_enabled      = false
  tags = merge(local.base_tags, local.security_tags, {
    Description = "Azure OpenAI Foundry (${var.chat_model_name} + ${var.embedding_model_name}) — ${var.project_name} ${var.environment}"
  })
}

# ─── Log Analytics + Alertas ────────────────────────────────────────────────────
module "monitoring" {
  source = "../../base/monitoring"

  name                = "law-${var.container_app_name}-${var.environment}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  container_app_name  = var.container_app_name
  alerts_enabled      = var.alerts_enabled
  alert_email         = var.alert_email
  tags                = local.base_tags
}

# ─── RBAC: Identity → ACR (AcrPull) ─────────────────────────────────────────────
resource "azurerm_role_assignment" "acr_pull" {
  scope                = module.acr.id
  role_definition_name = "AcrPull"
  principal_id         = module.identity.principal_id
}

# ─── RBAC: Identity → Key Vault (Key Vault Secrets User) ────────────────────────
resource "azurerm_role_assignment" "key_vault_secrets_user" {
  scope                = module.key_vault.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = module.identity.principal_id
}

# ─── RBAC: Identity → AI Search (Index Data Contributor + Service Contributor) ─
resource "azurerm_role_assignment" "ai_search_contributor" {
  scope                = module.ai_search.id
  role_definition_name = "Search Index Data Contributor"
  principal_id         = module.identity.principal_id
}

resource "azurerm_role_assignment" "ai_search_service_contributor" {
  scope                = module.ai_search.id
  role_definition_name = "Search Service Contributor"
  principal_id         = module.identity.principal_id
}

# ─── RBAC: Identity → Storage Account (Storage Blob Data Contributor) ───────────
resource "azurerm_role_assignment" "storage_blob_contributor" {
  scope                = module.storage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = module.identity.principal_id
}

# ─── RBAC: Identity → Azure OpenAI (Cognitive Services OpenAI User) ─────────────
resource "azurerm_role_assignment" "openai_user" {
  scope                = module.foundry.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = module.identity.principal_id
}

# ─── Container Apps ─────────────────────────────────────────────────────────────
module "container_apps" {
  source = "../../base/container-apps"

  name                       = var.container_app_name
  environment_name           = "cae-${var.container_app_name}"
  resource_group_name        = module.resource_group.name
  location                   = module.resource_group.location
  image                      = local.image
  registry_server            = module.acr.login_server
  registry_username          = module.acr.admin_username
  registry_password          = module.acr.admin_password
  registry_identity_id       = module.identity.id
  agent_model                = var.chat_model_name
  direct_secret_values       = local.direct_secret_values
  optional_secret_envs       = local.optional_secret_envs
  optional_plain_envs        = local.optional_plain_envs
  min_replicas               = var.min_replicas
  max_replicas               = var.max_replicas
  log_analytics_workspace_id = module.monitoring.workspace_resource_id
  tags = merge(local.base_tags, {
    Description = "Container App API DocuMindAI — ${var.project_name} ${var.environment}"
  })

  depends_on = [
    azurerm_role_assignment.acr_pull,
    azurerm_role_assignment.key_vault_secrets_user,
    azurerm_role_assignment.ai_search_contributor,
    azurerm_role_assignment.ai_search_service_contributor,
    azurerm_role_assignment.storage_blob_contributor,
    azurerm_role_assignment.openai_user,
  ]
}
