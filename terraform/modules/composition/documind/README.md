# Módulo de composición: documind

Composición completa de infraestructura Azure para **DocuMindAI** — asistente documental por WhatsApp.

## Arquitectura

```
┌──────────────────────────────────────────────────────────────────┐
│  Resource Group (rg-documind)                                    │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────┐   │
│  │  Container   │   │    Azure     │   │   Azure OpenAI     │   │
│  │   Registry   │   │  Container   │   │   Chat (gpt-4o)    │   │
│  │    (ACR)     │   │    Apps      │   │                    │   │
│  └──────────────┘   └──────────────┘   └────────────────────┘   │
│                            │                                     │
│  ┌──────────────┐   ┌──────┴───────┐   ┌────────────────────┐   │
│  │  Key Vault   │   │  User-Assign │   │   Azure OpenAI     │   │
│  │  (Secretos)  │   │   Identity   │   │ Embeddings (3-sm)  │   │
│  └──────────────┘   └─────────────-┘   └────────────────────┘   │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────┐   │
│  │  AI Search   │   │   Storage    │   │  Log Analytics     │   │
│  │  (Vectorial) │   │   Account    │   │   Workspace        │   │
│  └──────────────┘   └──────────────┘   └────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## Recursos creados

| Recurso                       | Módulo base              | Tags                           |
|-------------------------------|--------------------------|--------------------------------|
| Resource Group                | `resource-group`         | `base_tags`                    |
| Container Registry            | `container-registry`     | `base_tags`                    |
| User-Assigned Identity        | `user-assigned-identity` | `base_tags`                    |
| Key Vault                     | `key-vault`              | `base_tags + security_tags`    |
| Azure AI Search               | `ai-search`              | `base_tags + security_tags`    |
| Storage Account + Container   | `storage-account`        | `base_tags + security_tags`    |
| Azure OpenAI (chat)           | `azure-openai`           | `base_tags + security_tags`    |
| Azure OpenAI (embeddings)     | `azure-openai`           | `base_tags + security_tags`    |
| Log Analytics + Alertas       | `monitoring`             | `base_tags`                    |
| Container App + Environment   | `container-apps`         | `base_tags`                    |

## RBAC configurado

| Asignación                              | Rol                              |
|-----------------------------------------|----------------------------------|
| Identity → ACR                          | `AcrPull`                        |
| Identity → Key Vault                    | `Key Vault Secrets User`         |
| Identity → AI Search                    | `Search Index Data Contributor`  |
| Identity → Storage Account             | `Storage Blob Data Contributor`  |
| Identity → Azure OpenAI Chat            | `Cognitive Services OpenAI User` |
| Identity → Azure OpenAI Embeddings      | `Cognitive Services OpenAI User` |

## Variables requeridas

| Variable       | Descripción                              |
|----------------|------------------------------------------|
| `environment`  | `dev`, `stg`, `prod` (validado)          |
| `project_name` | Nombre del proyecto                      |
| `owner_email`  | Correo del responsable                   |
| `cost_center`  | Formato `CC-XXXXXX`                      |

## Secretos en Key Vault

Los siguientes secretos deben crearse **manualmente** o por pipeline CI/CD antes de desplegar la Container App:

- `whatsapp-access-token` — Token de acceso de la API de WhatsApp Cloud
- `whatsapp-app-secret` — App Secret para validar firmas de webhooks
- `whatsapp-verify-token` — Verify Token para el handshake del webhook

> [!CAUTION]
> **Nunca** escribas estos valores en archivos `.tfvars`. Usa `az keyvault secret set` o variables secretas del pipeline.

## Uso

```hcl
module "documind" {
  source = "../../modules/composition/documind"

  environment  = "dev"
  project_name = "documind"
  owner_email  = "owner@example.com"
  cost_center  = "CC-001234"

  location            = "eastus"
  resource_group_name = "rg-documind"
  container_app_name  = "ca-documind"
  acr_name_prefix     = "documindacr"
  image_tag           = "v1.0.0"

  chat_model_name      = "gpt-4o"
  chat_model_version   = "2024-11-20"
  embedding_model_name = "text-embedding-3-small"
  embedding_model_version = "1"

  whatsapp_phone_number_id = "PLACEHOLDER — completar: Phone Number ID de WhatsApp"
}
```

> [!NOTE]
> `image_tag = ""` omite la creación de la Container App, útil para aprovisionar la infraestructura base antes de publicar la primera imagen.
