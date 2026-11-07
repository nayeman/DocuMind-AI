output "id" {
  description = "ID del servicio Azure AI Search"
  value       = azurerm_search_service.this.id
}

output "name" {
  description = "Nombre del servicio Azure AI Search"
  value       = azurerm_search_service.this.name
}

output "endpoint" {
  description = "Endpoint HTTPS del servicio Azure AI Search"
  value       = "https://${azurerm_search_service.this.name}.search.windows.net"
}
