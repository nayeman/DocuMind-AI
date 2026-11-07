output "vnet_id" {
  description = "ID de la red virtual"
  value       = azurerm_virtual_network.this.id
}

output "container_apps_subnet_id" {
  description = "ID de la subred delegada para Container Apps"
  value       = azurerm_subnet.container_apps.id
}

output "postgres_subnet_id" {
  description = "ID de la subred delegada para PostgreSQL Flexible"
  value       = azurerm_subnet.postgres.id
}

output "postgres_private_dns_zone_id" {
  description = "ID de la zona DNS privada de PostgreSQL"
  value       = azurerm_private_dns_zone.postgres.id
}
