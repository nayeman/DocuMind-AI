output "id" {
  description = "ID del servicio Azure AI Search"
  value       = azurerm_search_service.this.id
}

output "name" {
  description = "Nombre del servicio Azure AI Search"
  value       = azurerm_search_service.this.name
}

output "primary_key" {
  description = "Clave de administración primaria del servicio"
  value       = azurerm_search_service.this.primary_key
  sensitive   = true
}

output "query_key" {
  description = "Clave de consulta del servicio"
  value       = tolist(azurerm_search_service.this.query_keys)[0].key
  sensitive   = true
}

output "endpoint" {
  description = "Endpoint HTTPS del servicio Azure AI Search"
  value       = "https://${azurerm_search_service.this.name}.search.windows.net"
}
