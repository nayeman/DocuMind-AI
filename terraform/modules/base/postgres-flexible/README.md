# Módulo base: postgres-flexible

Crea un PostgreSQL Flexible Server, su base de datos y, si usa acceso público,
las reglas de firewall.

## Inputs

| Nombre | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `name` | `string` | Sí | Nombre del servidor |
| `resource_group_name` | `string` | Sí | Resource Group destino |
| `location` | `string` | Sí | Región Azure |
| `server_version` | `string` | No | Versión mayor (default `16`) |
| `administrator_login` | `string` | Sí | Usuario administrador |
| `administrator_password` | `string` | Sí | Password administrador (sensible) |
| `sku_name` | `string` | No | SKU (default `B_Standard_B1ms`) |
| `storage_mb` | `number` | No | Almacenamiento (default `32768`) |
| `backup_retention_days` | `number` | No | Retención de backups (default `7`) |
| `public_network_access_enabled` | `bool` | No | Acceso público (default `true`) |
| `delegated_subnet_id` | `string` | No | Subred delegada para acceso privado |
| `private_dns_zone_id` | `string` | No | Zona DNS privada para acceso privado |
| `database_name` | `string` | No | Nombre de la BD (default `newspilot`) |
| `database_charset` | `string` | No | Charset (default `UTF8`) |
| `database_collation` | `string` | No | Collation (default `en_US.utf8`) |
| `allowed_ip` | `string` | No | IP local permitida (default vacío) |
| `tags` | `map(string)` | No | Etiquetas del servidor |

## Outputs

| Nombre | Descripción |
|---|---|
| `id` | ID del servidor |
| `fqdn` | FQDN del servidor |
| `database_name` | Nombre de la base de datos |

## Ejemplo

```hcl
module "postgres" {
  source = "../../modules/base/postgres-flexible"

  name                 = "newspilot-pg-${local.suffix}"
  resource_group_name  = module.resource_group.name
  location             = module.resource_group.location
  administrator_login  = "newspilotadmin"
  administrator_password = random_password.postgres.result
  tags                 = merge(local.base_tags, local.security_tags)
}
```

> Las reglas de firewall y la base de datos no admiten etiquetas en Azure.
> `delegated_subnet_id` y `private_dns_zone_id` se deben definir juntos; al
> hacerlo, el acceso público debe quedar deshabilitado.
