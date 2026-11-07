# Módulo base: container-apps

`infrastructure_subnet_id` crea un entorno nuevo sobre una VNet y requiere una
subred exclusiva delegada a `Microsoft.App/environments`. Con
`workload_profile_enabled = true`, el módulo crea el perfil `Consumption` para
ese entorno.

Crea un Container App Environment y, si `image` no está vacío, una Container App
con secretos, variables de entorno, probes e ingress.

## Inputs

| Nombre | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `name` | `string` | Sí | Nombre de la Container App |
| `environment_name` | `string` | Sí | Nombre del Environment |
| `resource_group_name` | `string` | Sí | Resource Group destino |
| `location` | `string` | Sí | Región Azure |
| `image` | `string` | No | Imagen; vacío = no crear la app |
| `container_cpu` | `number` | No | CPU (default `0.5`) |
| `container_memory` | `string` | No | Memoria (default `1Gi`) |
| `registry_server` | `string` | Sí | Login server del registry |
| `registry_identity_id` | `string` | Sí | Identidad administrada con rol `AcrPull` |
| `agent_model` | `string` | Sí | Modelo de los agentes |
| `sources_file` | `string` | No | Ruta del archivo de fuentes |
| `linkedin_enabled` | `bool` | No | Habilita LinkedIn |
| `postgres_dsn` | `string` | Sí | DSN de PostgreSQL (sensible) |
| `secret_refs` | `map(string)` | No | URI versionless de Key Vault por nombre de secreto |
| `optional_secret_envs` | `map(string)` | No | Envs que referencian secretos |
| `optional_plain_envs` | `map(string)` | No | Envs planas opcionales |
| `min_replicas` | `number` | No | Réplicas mínimas |
| `max_replicas` | `number` | No | Réplicas máximas |
| `ingress_port` | `number` | No | Puerto (default `8000`) |
| `tags` | `map(string)` | No | Etiquetas |

## Outputs

| Nombre | Descripción |
|---|---|
| `id` | ID de la Container App |
| `name` | Nombre de la Container App |
| `fqdn` | FQDN público |
| `environment_id` | ID del Environment |

## Ejemplo

```hcl
module "container_apps" {
  source = "../../modules/base/container-apps"

  name                 = "ca-newspilot"
  environment_name     = "cae-ca-newspilot"
  resource_group_name  = module.resource_group.name
  location             = module.resource_group.location
  image                = "${module.acr.login_server}/newspilot-api:wa4"
  registry_server      = module.acr.login_server
  registry_identity_id = module.identity.id
  agent_model          = "gpt-4.1-mini"
  postgres_dsn         = local.postgres_dsn
  secret_refs          = { "whatsapp-token" = "https://vault.vault.azure.net/secrets/whatsapp-token" }
  tags                 = merge(local.base_tags, local.security_tags)
}
```
