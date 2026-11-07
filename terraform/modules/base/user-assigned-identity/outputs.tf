output "id" {
  description = "ID de la identidad"
  value       = azurerm_user_assigned_identity.this.id
}

output "principal_id" {
  description = "Principal ID de la identidad"
  value       = azurerm_user_assigned_identity.this.principal_id
}

output "client_id" {
  description = "Client ID de la identidad"
  value       = azurerm_user_assigned_identity.this.client_id
}
