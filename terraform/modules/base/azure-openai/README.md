# Módulo base: azure-openai

Crea una cuenta Azure OpenAI (Cognitive Services) y un deployment de chat.
La autenticación local está deshabilitada por defecto; asigna acceso mediante
Microsoft Entra ID.

## Inputs

| Nombre | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `name` | `string` | Sí | Nombre de la cuenta |
| `resource_group_name` | `string` | Sí | Resource Group destino |
| `location` | `string` | Sí | Región Azure |
| `custom_subdomain_name` | `string` | Sí | Subdominio personalizado |
| `sku_name` | `string` | No | SKU (default `S0`) |
| `public_network_access_enabled` | `bool` | No | Acceso público (default `true`) |
| `local_auth_enabled` | `bool` | No | API keys (default `false`) |
| `model_name` | `string` | Sí | Nombre del modelo/deployment |
| `model_version` | `string` | Sí | Versión del modelo |
| `capacity` | `number` | No | Capacidad (default `1`) |
| `version_upgrade_option` | `string` | No | Política de upgrade |
| `rai_policy_name` | `string` | No | Política RAI |
| `tags` | `map(string)` | No | Etiquetas del recurso |

## Outputs

| Nombre | Descripción |
|---|---|
| `id` | ID de la cuenta |
| `name` | Nombre de la cuenta |
| `endpoint` | Endpoint |

## Ejemplo

```hcl
module "foundry" {
  source = "../../modules/base/azure-openai"

  name                  = "newspilot-aoai-${local.suffix}"
  resource_group_name   = module.resource_group.name
  location              = module.resource_group.location
  custom_subdomain_name = "newspilot-aoai-${local.suffix}"
  model_name            = "gpt-4.1-mini"
  model_version         = "2025-04-14"
  tags                  = merge(local.base_tags, local.security_tags)
}
```
