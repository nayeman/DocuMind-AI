output "container_app_fqdn" {
  description = "FQDN público de la Container App (vacío si image_tag no está definido)"
  value       = module.container_apps.fqdn
}

output "acr_login_server" {
  description = "Login server del Azure Container Registry"
  value       = module.acr.login_server
}

output "acr_name" {
  description = "Nombre del Azure Container Registry"
  value       = module.acr.name
}

output "ai_search_endpoint" {
  description = "Endpoint HTTPS del servicio Azure AI Search"
  value       = module.ai_search.endpoint
}

output "storage_account_name" {
  description = "Nombre de la Storage Account de documentos"
  value       = module.storage.name
}

output "resource_group_name" {
  description = "Nombre del Resource Group desplegado"
  value       = module.resource_group.name
}

output "key_vault_name" {
  description = "Nombre del Key Vault de secretos de runtime"
  value       = module.key_vault.name
}

output "identity_client_id" {
  description = "Client ID de la User-Assigned Managed Identity"
  value       = module.identity.client_id
}

output "openai_chat_endpoint" {
  description = "Endpoint de la cuenta Azure OpenAI para chat"
  value       = module.foundry.endpoint
}

output "openai_embeddings_endpoint" {
  description = "Endpoint de la cuenta Azure OpenAI para embeddings"
  value       = module.foundry.endpoint
}

output "log_analytics_workspace_id" {
  description = "Customer ID del Log Analytics Workspace"
  value       = module.monitoring.workspace_id
}
