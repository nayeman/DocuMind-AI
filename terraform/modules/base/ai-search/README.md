# Módulo base: ai-search

Encapsula `azurerm_search_service` para DocuMindAI.

## Variables de entrada

| Variable           | Tipo     | Default    | Descripción                              |
|--------------------|----------|------------|------------------------------------------|
| `name`             | string   | —          | Nombre único del servicio AI Search      |
| `resource_group_name` | string | —         | Resource Group de destino                |
| `location`         | string   | —          | Región Azure                             |
| `sku`              | string   | `"basic"`  | SKU del servicio                         |
| `replica_count`    | number   | `1`        | Número de réplicas                       |
| `partition_count`  | number   | `1`        | Número de particiones                    |
| `tags`             | map(string) | `{}`    | Etiquetas del recurso                    |

## Outputs

| Output          | Sensible | Descripción                                  |
|-----------------|----------|----------------------------------------------|
| `id`            | No       | ID del recurso                               |
| `name`          | No       | Nombre del servicio                          |
| `primary_key`   | Sí       | Clave de administración primaria             |
| `query_key`     | Sí       | Clave de consulta (solo lectura)             |
| `endpoint`      | No       | URL `https://<name>.search.windows.net`      |

## Uso

```hcl
module "ai_search" {
  source = "../../base/ai-search"

  name                = "srch-documind-dev-abcd"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  sku                 = "basic"
  tags                = local.base_tags
}
```

> [!NOTE]
> En producción considera `sku = "standard"` con más réplicas para alta disponibilidad.
