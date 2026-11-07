# Módulo base: container-registry

Crea un Azure Container Registry con SKU configurable.

## Inputs

| Nombre | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `name` | `string` | Sí | Nombre del ACR (solo alfanumérico) |
| `resource_group_name` | `string` | Sí | Resource Group destino |
| `location` | `string` | Sí | Región Azure |
| `sku` | `string` | No | SKU (default `Basic`) |
| `admin_enabled` | `bool` | No | Credenciales admin (default `false`) |
| `tags` | `map(string)` | No | Etiquetas del recurso |

## Outputs

| Nombre | Descripción |
|---|---|
| `id` | ID del ACR |
| `name` | Nombre del ACR |
| `login_server` | Login server |

## Ejemplo

```hcl
module "acr" {
  source = "../../modules/base/container-registry"

  name                = "newspilotacr${local.suffix}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = local.base_tags
}
```
