# Infraestructura en Microsoft Azure — DocuMind AI

Toda la infraestructura cloud se aprovisiona y administra mediante **Terraform** bajo un diseño modular y parametrizado por entornos (`dev`, `staging`, `prod`).

---

## Recursos Cloud Aprovisionados

| Recurso Azure | Servicio | Propósito en DocuMind AI |
|---|---|---|
| `azurerm_resource_group` | Resource Group | Agrupación lógica y delimitación del ciclo de vida de los recursos. |
| `azurerm_container_app` | Azure Container Apps | Ejecución serverless de la imagen Docker de FastAPI con autoescalado HTTP. |
| `azurerm_container_registry` | Container Registry (ACR) | Almacén privado de imágenes de contenedor de la aplicación. |
| `azurerm_storage_account` | Blob Storage | Almacenamiento seguro de documentos originales (PDF, DOCX, TXT). |
| `azurerm_search_service` | Azure AI Search | Servicio administrado para indexación vectorial y búsqueda HNSW. |
| `azapi_resource` / `azurerm_cognitive_account` | Microsoft Foundry / AI Services | Alojamiento y despliegue de modelos de embeddings y chat completion. |
| `azurerm_key_vault` | Azure Key Vault | Almacenamiento centralizado de secretos (tokens y app secret de Meta). |
| `azurerm_user_assigned_identity` | Managed Identity | Identidad para autenticación sin contraseñas entre servicios de Azure. |
| `azurerm_log_analytics_workspace` | Log Analytics | Centralización de logs, trazas y métricas operativas. |
| `azurerm_application_insights` | Application Insights | Monitoreo del rendimiento de la API y diagnóstico de errores. |

---

## Estructura de Terraform

El código IaC se organiza en `terraform/`:

```text
terraform/
├── environments/
│   ├── dev/          # Variables y tfvars de desarrollo
│   ├── staging/      # Variables de pruebas
│   └── prod/         # Configuración de producción
└── modules/
    ├── base/         # Módulos atómicos reutilizables (rg, aca, search, blob, etc.)
    └── composition/  # Módulo integrador documind con roles RBAC
```

---

## Autenticación y Asignaciones RBAC

Para eliminar credenciales en código y variables planas, Container Apps utiliza una **Identidad Administrada Asignada por el Usuario** con los siguientes roles de mínimo privilegio:

| Rol RBAC | Recurso Destino | Justificación |
|---|---|---|
| `Storage Blob Data Contributor` | Storage Account | Permite subir y leer documentos binarios. |
| `Search Index Data Contributor` | AI Search Service | Permite crear índices, subir documentos vectoriales y buscar. |
| `Search Service Contributor` | AI Search Service | Permite consultar metadatos y administrar esquemas. |
| `Cognitive Services OpenAI User` | Foundry / AI Services | Permite generar embeddings y consumir chat completions. |
| `Key Vault Secrets User` | Key Vault | Permite a Container Apps resolver secretos en tiempo de despliegue. |
