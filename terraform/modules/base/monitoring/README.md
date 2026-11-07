# Módulo base: monitoring

Crea un Log Analytics Workspace. La composición enlaza el entorno nuevo de
Container Apps de la ruta privada. Si `alerts_enabled` y
`alert_email` tienen valor, crea un action group por correo y una alerta de
errores de aprovisionamiento de revisiones.

## Inputs

| Nombre | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `name` | `string` | Sí | Nombre del workspace |
| `resource_group_name` | `string` | Sí | Resource Group destino |
| `location` | `string` | Sí | Región Azure |
| `container_app_name` | `string` | Sí | App incluida en la alerta |
| `alerts_enabled` | `bool` | No | Habilita alertas con receptor configurado |
| `alert_email` | `string` | No | Correo receptor; vacío no crea alertas |
| `tags` | `map(string)` | No | Etiquetas |

## Outputs

| Nombre | Descripción |
|---|---|
| `workspace_resource_id` | ID del recurso Azure |
| `workspace_id` | Customer ID para consultas |
