# Módulo base: resource-group

Crea un Azure Resource Group con etiquetas.

## Inputs

| Nombre | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `name` | `string` | Sí | Nombre del Resource Group |
| `location` | `string` | Sí | Región Azure |
| `tags` | `map(string)` | No | Etiquetas del recurso |

## Outputs

| Nombre | Descripción |
|---|---|
| `id` | ID del Resource Group |
| `name` | Nombre del Resource Group |
| `location` | Región del Resource Group |

## Ejemplo

```hcl
module "resource_group" {
  source = "../../modules/base/resource-group"

  name     = "rg-newspilot"
  location = "brazilsouth"
  tags     = local.base_tags
}
```
