output "workspace_resource_id" {
  description = "ID del recurso Log Analytics Workspace"
  value       = azurerm_log_analytics_workspace.this.id
}

output "workspace_id" {
  description = "Customer ID del Log Analytics Workspace"
  value       = azurerm_log_analytics_workspace.this.workspace_id
}
