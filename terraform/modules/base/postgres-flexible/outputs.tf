output "id" {
  description = "ID del servidor PostgreSQL Flexible"
  value       = azurerm_postgresql_flexible_server.this.id
}

output "fqdn" {
  description = "FQDN del servidor PostgreSQL Flexible"
  value       = azurerm_postgresql_flexible_server.this.fqdn
}

output "database_name" {
  description = "Nombre de la base de datos"
  value       = azurerm_postgresql_flexible_server_database.this.name
}
