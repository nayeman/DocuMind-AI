output "id" {
  description = "ID de la cuenta Azure OpenAI"
  value       = azurerm_cognitive_account.this.id
}

output "name" {
  description = "Nombre de la cuenta Azure OpenAI"
  value       = azurerm_cognitive_account.this.name
}

output "endpoint" {
  description = "Endpoint de la cuenta Azure OpenAI"
  value       = azurerm_cognitive_account.this.endpoint
}
