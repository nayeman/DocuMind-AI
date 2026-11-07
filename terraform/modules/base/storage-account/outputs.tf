output "id" {
  description = "ID de la Storage Account"
  value       = azurerm_storage_account.this.id
}

output "name" {
  description = "Nombre de la Storage Account"
  value       = azurerm_storage_account.this.name
}

output "primary_connection_string" {
  description = "Cadena de conexión primaria de la Storage Account"
  value       = azurerm_storage_account.this.primary_connection_string
  sensitive   = true
}

output "primary_blob_endpoint" {
  description = "Endpoint primario del servicio Blob"
  value       = azurerm_storage_account.this.primary_blob_endpoint
}

output "container_name" {
  description = "Nombre del contenedor Blob creado"
  value       = azurerm_storage_container.documents.name
}
