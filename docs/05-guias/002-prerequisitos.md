# 002 — Pre-requisitos — DocuMind AI

Herramientas y cuentas que necesitas **antes** de desplegar o desarrollar.

---

## 1. Herramientas de línea de comandos

| Herramienta | Versión mínima | Verificar | Instalar |
|---|---|---|---|
| **Azure CLI** | 2.60+ | `az version` | [docs.microsoft.com/cli/azure/install](https://docs.microsoft.com/cli/azure/install-azure-cli) |
| **Terraform** | 1.5+ | `terraform version` | [developer.hashicorp.com/terraform/install](https://developer.hashicorp.com/terraform/install) |
| **Docker** | 24+ | `docker version` | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **Python** | 3.13+ | `python --version` | [python.org/downloads](https://www.python.org/downloads/) |
| **uv** | 0.4+ | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **ngrok** _(solo dev)_ | cualquiera | `ngrok version` | [ngrok.com/download](https://ngrok.com/download) |

---

## 2. Cuenta y suscripción Azure

1. **Suscripción activa** con permisos de `Contributor` o `Owner` en el scope donde vas a desplegar.
2. **Cuotas disponibles** en la región `eastus` para:
   - Azure OpenAI (`gpt-4o` + `text-embedding-3-small`)
   - Azure Container Apps
   - Azure AI Search (SKU Basic)
3. **Azure OpenAI habilitado** — el servicio requiere aprobación previa: [aka.ms/oai/access](https://aka.ms/oai/access).

---

## 3. Cuenta Meta / WhatsApp Business

Necesitas un **Meta App** configurada en [developers.facebook.com](https://developers.facebook.com):

| Dato | Dónde encontrarlo |
|---|---|
| `WHATSAPP_PHONE_NUMBER_ID` | Meta for Developers → WhatsApp → API Setup → Phone Number ID |
| `WHATSAPP_ACCESS_TOKEN` | Meta for Developers → WhatsApp → API Setup → Temporary / Permanent Token |
| `WHATSAPP_APP_SECRET` | Meta for Developers → App Settings → Basic → App Secret |
| `WHATSAPP_WEBHOOK_VERIFY_TOKEN` | Valor **que tú eliges** (cadena aleatoria segura) |

> [!TIP]
> Genera el verify token con: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

---

## 4. Backend de estado Terraform (Azure Storage)

Terraform guarda el `tfstate` en Azure Blob Storage. Créalo **una sola vez** antes del primer `terraform init`:

```bash
# Variables — ajusta a tu suscripción
LOCATION="eastus"
RG_TF="rg-terraform-state"
SA_TF="stdocumindtfstate"       # solo alfanumérico, único globalmente
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

Anota los valores — los necesitas en la [guía de despliegue](003-despliegue.md).

---

## 5. Service Principal (opcional — CI/CD)

Solo necesario si despliegas desde un pipeline (GitHub Actions, etc.). Para despliegue manual desde tu máquina basta con `az login`.

```bash
az ad sp create-for-rbac \
  --name "sp-documind-tf" \
  --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>
```

Guarda el JSON resultante — contiene `clientId`, `clientSecret`, `tenantId`.

> [!CAUTION]
> Nunca escribas estos valores en archivos del repositorio. Úsalos solo como secretos del pipeline o variables de entorno temporales.
