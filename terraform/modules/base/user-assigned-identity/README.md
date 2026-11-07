# Módulo base: user-assigned-identity

Crea una identidad administrada user-assigned para permisos RBAC.

## Inputs

| Nombre | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `name` | `string` | Sí | Nombre de la identidad |
| `resource_group_name` | `string` | Sí | Resource Group destino |
| `location` | `string` | Sí | Región Azure |
| `tags` | `map(string)` | No | Etiquetas del recurso |

## Outputs

| Nombre | Descripción |
|---|---|
| `id` | ID de la identidad |
| `principal_id` | Principal ID |
| `client_id` | Client ID |

## Ejemplo

```hcl
module "identity" {
  source = "../../modules/base/user-assigned-identity"

  name                = "id-ca-newspilot"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = local.base_tags
}
```
