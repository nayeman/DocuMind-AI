# Guía Completa — DocuMind AI

Desde cero hasta recibir un mensaje en WhatsApp y ver la respuesta.

---

## Contenido

1. [Pre-requisitos](#1-pre-requisitos)
2. [Entorno local](#2-entorno-local)
3. [Infraestructura Azure con Terraform](#3-infraestructura-azure-con-terraform)
4. [Credenciales en Key Vault](#4-credenciales-en-key-vault)
5. [Imagen Docker → ACR](#5-imagen-docker--acr)
6. [Activar Container App](#6-activar-container-app)
7. [Configurar Webhook WhatsApp](#7-configurar-webhook-whatsapp)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Pre-requisitos

### 1.1 — Herramientas

| Herramienta | Versión mínima | Verificar | Instalar |
|---|---|---|---|
| **Azure CLI** | 2.60+ | `az version` | [docs.microsoft.com/cli/azure/install](https://docs.microsoft.com/cli/azure/install-azure-cli) |
| **Terraform** | 1.5+ | `terraform version` | [developer.hashicorp.com/terraform/install](https://developer.hashicorp.com/terraform/install) |
| **Docker** | 24+ | `docker version` | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **Python** | 3.13+ | `python --version` | [python.org/downloads](https://www.python.org/downloads/) |
| **uv** | 0.4+ | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **ngrok** _(solo dev local)_ | cualquiera | `ngrok version` | [ngrok.com/download](https://ngrok.com/download) |

### 1.2 — Cuenta y suscripción Azure

1. **Suscripción activa** con permisos de `Contributor` o `Owner`.
2. **Cuotas disponibles** en `eastus` para: Azure OpenAI, Container Apps, AI Search (Basic).
3. **Azure OpenAI habilitado** — requiere aprobación previa: [aka.ms/oai/access](https://aka.ms/oai/access).

### 1.3 — Cuenta Meta / WhatsApp Business

Necesitas una **Meta App** configurada en [developers.facebook.com](https://developers.facebook.com):

| Variable | Dónde encontrarlo |
|---|---|
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp → API Setup → Phone Number ID |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp → API Setup → Temporary / Permanent Token |
| `WHATSAPP_APP_SECRET` | App Settings → Basic → App Secret |
| `WHATSAPP_WEBHOOK_VERIFY_TOKEN` | Valor **que tú eliges** (cadena aleatoria segura) |

> [!TIP]
> Genera el verify token con: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 1.4 — Backend de estado Terraform

Crea el Storage Account para guardar el `tfstate` (**una sola vez**):

```bash
LOCATION="eastus"
RG_TF="rg-terraform-state"
SA_TF="stdocumindtfstate"    # solo alfanumérico, único globalmente
CONTAINER_TF="tfstate"

az login
az group create --name $RG_TF --location $LOCATION
az storage account create \
  --name $SA_TF \
  --resource-group $RG_TF \
  --location $LOCATION \
  --sku Standard_LRS \
  --allow-blob-public-access false

az storage container create \
  --name $CONTAINER_TF \
  --account-name $SA_TF
```

### 1.5 — Service Principal (opcional — solo CI/CD)

Para despliegue manual desde tu máquina basta con `az login`. Solo para pipelines:

```bash
az ad sp create-for-rbac \
  --name "sp-documind-tf" \
  --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>
```

> [!CAUTION]
> Nunca escribas `clientSecret` en archivos del repositorio. Úsalo solo en secretos del pipeline.

---

## 2. Entorno local

### 2.1 — Instalar dependencias

```bash
cd DocuMindAI
uv sync
```

### 2.2 — Variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con los valores de tus recursos Azure y Meta:

```dotenv
# --- App ---
APP_ENV=dev
APP_LOG_LEVEL=INFO
APP_HOST=0.0.0.0
APP_PORT=8000

# --- WhatsApp / Meta ---
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
WHATSAPP_ACCESS_TOKEN=tu_meta_access_token
WHATSAPP_APP_SECRET=tu_meta_app_secret
WHATSAPP_WEBHOOK_VERIFY_TOKEN=token_seguro_para_meta
WHATSAPP_API_VERSION=v20.0

# --- Azure Storage ---
AZURE_STORAGE_ACCOUNT_NAME=tustorageaccount
AZURE_STORAGE_CONTAINER_NAME=documind-documents

# --- Azure AI Search ---
AZURE_SEARCH_ENDPOINT=https://tusearch.search.windows.net
AZURE_SEARCH_INDEX_NAME=documind-index
AZURE_SEARCH_API_VERSION=2024-07-01

# --- Azure OpenAI ---
AZURE_OPENAI_ENDPOINT=https://tuopenai.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_EMBEDDING_DIMENSIONS=1536

# --- Azure Identity (dejar vacío si usas az login) ---
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_TENANT_ID=
```

### 2.3 — Tests y linters

```bash
uv run pytest -v
uv run ruff check src tests
uv run mypy src tests
```

### 2.4 — Servidor de desarrollo

```bash
uv run uvicorn documind.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"documind-ai","version":"0.1.0"}
```

### 2.5 — Webhook local con ngrok

Para exponer el servidor local a Meta durante el desarrollo:

```bash
ngrok http 8000
```

En [developers.facebook.com](https://developers.facebook.com) → WhatsApp → Configuration:
- **Callback URL:** `https://<tu-subdominio>.ngrok-free.app/webhook`
- **Verify Token:** el valor de `WHATSAPP_WEBHOOK_VERIFY_TOKEN`

Haz clic en **Verify and save** y suscríbete al campo `messages`.

---

## 3. Infraestructura Azure con Terraform

### 3.1 — Autenticarse en Azure

```bash
az login
az account show   # confirma que la suscripción correcta está activa

# Si tienes varias suscripciones:
az account set --subscription "<SUBSCRIPTION_ID>"
```

### 3.2 — Configurar variables

```bash
cd terraform/environments/dev
cp terraform.tfvars.example terraform.tfvars
```

Mínimo obligatorio en `terraform.tfvars`:

```hcl
owner_email              = "tu@email.com"
cost_center              = "CC-000001"
whatsapp_phone_number_id = "123456789"   # Phone Number ID de Meta (no sensible)
```

> [!NOTE]
> Los tokens y secretos de WhatsApp van **solo en Key Vault** (sección 4), nunca en `terraform.tfvars`.

### 3.3 — Backend de estado

```bash
# Dentro de terraform/environments/dev
cat > backend.conf << 'EOF'
resource_group_name  = "rg-terraform-state"
storage_account_name = "stdocumindtfstate"
container_name       = "tfstate"
key                  = "documind/dev/terraform.tfstate"
EOF
```

### 3.4 — Init, Plan y Apply

```bash
terraform init -backend-config=backend.conf
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
```

Terraform crea en orden:

1. Resource Group
2. Azure Container Registry (ACR)
3. User-Assigned Managed Identity
4. Key Vault
5. Azure AI Search
6. Storage Account
7. Azure OpenAI — deployments `gpt-4o` + `text-embedding-3-small`
8. Log Analytics + Alertas
9. RBAC assignments (Identity → ACR, Key Vault, AI Search, Storage, OpenAI)
10. Container App Environment _(la Container App se activa en la sección 6)_

### 3.5 — Capturar outputs

```bash
terraform output
```

| Output | Usado en |
|---|---|
| `acr_login_server` | Sección 5 — push imagen |
| `acr_name` | Sección 5 — az acr login |
| `key_vault_name` | Sección 4 — cargar secretos |
| `ai_search_endpoint` | `.env` local |
| `storage_account_name` | `.env` local |
| `container_app_fqdn` | Sección 7 — webhook URL |

---

## 4. Credenciales en Key Vault

Los secretos de WhatsApp **nunca** van en Terraform. Se cargan directamente en Key Vault:

```bash
KV_NAME=$(terraform output -raw key_vault_name)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Dar permisos de escritura a tu usuario (una sola vez)
az role assignment create \
  --role "Key Vault Secrets Officer" \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-documind/providers/Microsoft.KeyVault/vaults/$KV_NAME
```

Carga los tres secretos:

```bash
# 1. Access Token
az keyvault secret set \
  --vault-name $KV_NAME \
  --name "whatsapp-access-token" \
  --value "<WHATSAPP_ACCESS_TOKEN>"

# 2. App Secret
az keyvault secret set \
  --vault-name $KV_NAME \
  --name "whatsapp-app-secret" \
  --value "<WHATSAPP_APP_SECRET>"

# 3. Verify Token
az keyvault secret set \
  --vault-name $KV_NAME \
  --name "whatsapp-verify-token" \
  --value "<WHATSAPP_WEBHOOK_VERIFY_TOKEN>"
```

Verifica:

```bash
az keyvault secret list --vault-name $KV_NAME --query "[].name" -o tsv
# whatsapp-access-token
# whatsapp-app-secret
# whatsapp-verify-token
```

### 4.1 — Actualización rápida del Access Token temporal (cada 24 horas)

Como en desarrollo se utiliza el **Temporary Access Token** de Meta (que vence cada 24 horas en **WhatsApp → API Setup**), cámbialo rápidamente en cualquier momento ejecutando:

```bash
az keyvault secret set \
  --vault-name kv-documind-1inu5vh0 \
  --name "whatsapp-access-token" \
  --value "<PEGA_AQUI_TU_NUEVO_TOKEN>"
```

> [!TIP]
> En entornos Express de Azure, los secretos se inyectan en tiempo de aprovisionamiento de Container App. Tras actualizar el token en Key Vault, aplica el cambio para refrescar la revisión:
> ```bash
> cd terraform/environments/dev
> terraform apply -auto-approve
> ```
> O también puedes reiniciar la revisión activa:
> ```bash
> az containerapp revision restart \
>   --name ca-documind \
>   --resource-group rg-documind \
>   --revision $(az containerapp revision list --name ca-documind --resource-group rg-documind --query "[0].name" -o tsv)
> ```

> [!CAUTION]
> Nunca ejecutes `az keyvault secret show` en una terminal visible. Usa el portal de Azure o redirige el valor a una variable de shell.

---

## 5. Imagen Docker → ACR

### 5.1 — Autenticarse en ACR

```bash
ACR_NAME=$(terraform output -raw acr_name)
az acr login --name $ACR_NAME
```

### 5.2 — Build y Push

Desde la **raíz del proyecto**:

```bash
ACR_SERVER=$(terraform output -raw acr_login_server)
IMAGE_TAG=$(git rev-parse --short HEAD)   # o "v1.0.0"

# NOTA: Si estás en macOS (Apple Silicon M1/M2/M3/M4), DEBES especificar --platform linux/amd64
docker build \
  --platform linux/amd64 \
  -f docker/Dockerfile \
  -t $ACR_SERVER/documind-api:$IMAGE_TAG \
  .

docker push $ACR_SERVER/documind-api:$IMAGE_TAG
```

---

## 6. Activar Container App

Re-aplica Terraform pasando el tag de la imagen:

```bash
cd terraform/environments/dev

terraform apply \
  -var="image_tag=$IMAGE_TAG" \
  -auto-approve
```

Verifica que el servicio arrancó:

```bash
FQDN=$(terraform output -raw container_app_fqdn)
curl https://$FQDN/health
# {"status":"healthy","service":"documind-ai","version":"0.1.0"}
```

Si falla, revisa los logs en tiempo real:

```bash
az containerapp logs show \
  --name ca-documind \
  --resource-group rg-documind \
  --follow
```

---

## 7. Configurar Webhook WhatsApp

### 7.1 — URL del webhook

```bash
FQDN=$(terraform output -raw container_app_fqdn)
echo "Webhook URL: https://$FQDN/webhook"
```

### 7.2 — Registrar en Meta for Developers

1. Ve a [developers.facebook.com](https://developers.facebook.com) → tu App → **WhatsApp → Configuration**.
2. En **Webhook**:
   - **Callback URL:** `https://<FQDN>/webhook`
   - **Verify Token:** el valor que cargaste como `whatsapp-verify-token` en Key Vault
3. Clic en **Verify and save** — Meta envía un `GET /webhook?hub.challenge=...` que el servidor responde automáticamente.
4. En **Webhook fields**, suscríbete a `messages`.

### 7.3 — Test end-to-end

Envía un mensaje desde el número de prueba de tu Meta App al número configurado. DocuMind AI debe responder en WhatsApp.

Monitorea:

```bash
az containerapp logs show \
  --name ca-documind \
  --resource-group rg-documind \
  --follow
```

---

## 8. Troubleshooting

| Síntoma | Causa probable | Solución |
|---|---|---|
| `terraform apply` falla en Azure OpenAI | Cuota no aprobada | Solicitar acceso en [aka.ms/oai/access](https://aka.ms/oai/access) |
| Container App queda en estado `Failed` | Imagen no encontrada en ACR | Verificar `image_tag` correcto y que `az acr login` fue exitoso |
| `The container image does not provide a linux/amd64 variant` | Imagen construida en Mac (arm64) | Agregar `--platform linux/amd64` al comando `docker build` |
| `ExpressKeyVaultSecretsNotSupported` | Suscripción Azure Student (express env) | Terraform lee los secretos de Key Vault vía data sources y los inyecta cifrados directamente en Container App |
| `managed identity bootstrap failed` en ACR pull | Express env no soporta token pull de ACR con MSI | El módulo usa autenticación admin de ACR gestionada automáticamente en Terraform |
| Webhook 403 en Meta | HMAC signature inválido | Verificar que `whatsapp-app-secret` en KV coincide con el App Secret de Meta |
| Webhook verify falla | Verify token no coincide | El valor en KV (`whatsapp-verify-token`) debe ser idéntico al configurado en Meta |
| `az keyvault secret set` → 403 | Sin rol `Key Vault Secrets Officer` | Ejecutar el `az role assignment create` de la sección 4 |
| `Viewer cannot access Paid Message Account` / Token expirado | Token temporal de Meta vencido (24h) | Actualizar con `az keyvault secret set` (sección 4.1) y re-aplicar `terraform apply` |

