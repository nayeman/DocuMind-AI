output "id" {
  description = "ID de la Container App"
  value       = try(azurerm_container_app.this[0].id, "")
}

output "name" {
  description = "Nombre de la Container App"
  value       = var.name
}

output "fqdn" {
  description = "FQDN público de la Container App (vacío si image está vacío)"
  value       = try(azurerm_container_app.this[0].ingress[0].fqdn, "")
}

output "environment_id" {
  description = "ID del Container App Environment"
  value       = azurerm_container_app_environment.this.id
}
