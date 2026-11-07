output "id" {
  description = "ID del ACR"
  value       = azurerm_container_registry.this.id
}

output "name" {
  description = "Nombre del ACR"
  value       = azurerm_container_registry.this.name
}

output "login_server" {
  description = "Login server del ACR"
  value       = azurerm_container_registry.this.login_server
}
