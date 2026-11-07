# Módulo base: storage-account

Encapsula `azurerm_storage_account` + `azurerm_storage_container` para DocuMindAI.

## Variables de entrada

| Variable            | Tipo        | Default                | Descripción                                   |
|---------------------|-------------|------------------------|-----------------------------------------------|
| `name`              | string      | —                      | Nombre único de la cuenta (3-24 chars alfanum) |
| `resource_group_name` | string    | —                      | Resource Group de destino                     |
| `location`          | string      | —                      | Región Azure                                  |
| `container_name`    | string      | `"documind-documents"` | Nombre del contenedor Blob                    |
| `account_tier`      | string      | `"Standard"`           | Tier de la cuenta                             |
| `replication_type`  | string      | `"LRS"`                | Tipo de replicación                           |
| `tags`              | map(string) | `{}`                   | Etiquetas del recurso                         |

## Outputs

| Output                     | Sensible | Descripción                              |
|----------------------------|----------|------------------------------------------|
| `id`                       | No       | ID del recurso                           |
| `name`                     | No       | Nombre de la Storage Account             |
| `primary_connection_string`| Sí       | Connection string primaria               |
| `primary_blob_endpoint`    | No       | URL del endpoint Blob                    |
| `container_name`           | No       | Nombre del contenedor creado             |

## Uso

```hcl
module "storage" {
  source = "../../base/storage-account"

  name                = "stdocuminddevabcd"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  container_name      = "documind-documents"
  tags                = merge(local.base_tags, local.security_tags)
}
```

> [!CAUTION]
> El nombre de Storage Account debe ser globalmente único, 3-24 caracteres, solo letras minúsculas y dígitos.
