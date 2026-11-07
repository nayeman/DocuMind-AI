output "container_app_fqdn" {
  description = "FQDN público de la Container App"
  value       = module.documind.container_app_fqdn
}

output "acr_login_server" {
  description = "Login server del Azure Container Registry"
  value       = module.documind.acr_login_server
}

output "acr_name" {
  description = "Nombre del Azure Container Registry"
  value       = module.documind.acr_name
}

output "ai_search_endpoint" {
  description = "Endpoint HTTPS del servicio Azure AI Search"
  value       = module.documind.ai_search_endpoint
}

output "storage_account_name" {
  description = "Nombre de la Storage Account de documentos"
  value       = module.documind.storage_account_name
}

output "resource_group_name" {
  description = "Nombre del Resource Group desplegado"
  value       = module.documind.resource_group_name
}

output "key_vault_name" {
  description = "Nombre del Key Vault de secretos de runtime"
  value       = module.documind.key_vault_name
}
