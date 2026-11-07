# 003 — Despliegue en Azure — DocuMind AI

Guía completa para levantar la infraestructura, publicar la imagen y configurar WhatsApp.

> [!IMPORTANT]
> Completa la [guía de pre-requisitos](002-prerequisitos.md) antes de continuar.

---

## Fases de despliegue

```
Fase 1 → Infraestructura Azure (Terraform)
Fase 2 → Credenciales en Key Vault (az CLI)
Fase 3 → Imagen Docker → ACR
Fase 4 → Container App activa (Terraform apply con image_tag)
Fase 5 → Webhook WhatsApp → test end-to-end
```

---

## Fase 1 — Infraestructura Azure con Terraform

### 1.1 — Autenticarse en Azure

```bash
az login
az account show   # confirma que la suscripción correcta está activa
```

Si tienes varias suscripciones:

```bash
az account set --subscription "<SUBSCRIPTION_ID>"
```

### 1.2 — Configurar variables Terraform

```bash
cd terraform/environments/dev
cp terraform.tfvars.example terraform.tfvars
```

Edita `terraform.tfvars` con tus valores. Los únicos **obligatorios** son:

```hcl
owner_email  = "tu@email.com"
cost_center  = "CC-000001"       # formato CC-XXXXXX
```

> [!NOTE]
> `whatsapp_phone_number_id` es público (no sensible) — ponlo aquí.
> Los tokens y secretos de WhatsApp van **solo en Key Vault** (Fase 2).

### 1.3 — Configurar backend de estado

Crea el archivo `backend.conf` (no se commitea — está en `.gitignore`):

```bash
cat > backend.conf << 'EOF'
resource_group_name  = "rg-terraform-state"
storage_account_name = "stdocumindtfstate"
container_name       = "tfstate"
key                  = "documind/dev/terraform.tfstate"
EOF
```

### 1.4 — Init, Plan y Apply

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
7. Azure OpenAI (Foundry) — deployments `gpt-4o` + `text-embedding-3-small`
8. Log Analytics + Alertas
9. RBAC assignments (Identity → ACR, Key Vault, AI Search, Storage, OpenAI)
10. Container App Environment _(la Container App en sí se crea en Fase 4)_

### 1.5 — Capturar outputs

Al finalizar el apply, anota los outputs que usarás en pasos siguientes:

```bash
terraform output
```

| Output | Usado en |
|---|---|
| `acr_login_server` | Fase 3 — push imagen |
| `acr_name` | Fase 3 — az acr login |
| `key_vault_name` | Fase 2 — cargar secretos |
| `ai_search_endpoint` | `.env` local |
| `storage_account_name` | `.env` local |
| `container_app_fqdn` | Fase 5 — webhook URL |

---

## Fase 2 — Credenciales en Key Vault

Los secretos de WhatsApp **nunca** van en `terraform.tfvars`. Se cargan directamente en Key Vault:

```bash
# Variables
KV_NAME=$(terraform output -raw key_vault_name)   # desde terraform/environments/dev
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Dar acceso a tu usuario actual para set secrets (una sola vez)
az role assignment create \
  --role "Key Vault Secrets Officer" \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-documind/providers/Microsoft.KeyVault/vaults/$KV_NAME
```

Carga los tres secretos:

```bash
# 1. Access Token de WhatsApp (token de larga duración desde Meta)
az keyvault secret set \
  --vault-name $KV_NAME \
  --name "whatsapp-access-token" \
  --value "<WHATSAPP_ACCESS_TOKEN>"

# 2. App Secret (desde Meta for Developers → App Settings → Basic)
az keyvault secret set \
  --vault-name $KV_NAME \
  --name "whatsapp-app-secret" \
  --value "<WHATSAPP_APP_SECRET>"

# 3. Verify Token (cadena que tú elegiste — debe coincidir con la que configurarás en Meta)
az keyvault secret set \
  --vault-name $KV_NAME \
  --name "whatsapp-verify-token" \
  --value "<WHATSAPP_WEBHOOK_VERIFY_TOKEN>"
```

Verifica que quedaron:

```bash
az keyvault secret list --vault-name $KV_NAME --query "[].name" -o tsv
# Debe mostrar:
# whatsapp-access-token
# whatsapp-app-secret
# whatsapp-verify-token
```

> [!CAUTION]
> Nunca ejecutes `az keyvault secret show` con el valor en la terminal si hay alguien mirando tu pantalla. Usa el portal de Azure o `--query value` y redirígelo a una variable.

---

## Fase 3 — Imagen Docker → ACR

### 3.1 — Autenticarse en ACR

```bash
ACR_NAME=$(cd terraform/environments/dev && terraform output -raw acr_name)
az acr login --name $ACR_NAME
```

### 3.2 — Build y Push

Desde la **raíz del proyecto**:

```bash
ACR_SERVER=$(cd terraform/environments/dev && terraform output -raw acr_login_server)
IMAGE_TAG="v1.0.0"   # o: $(git rev-parse --short HEAD)

docker build \
  -f docker/Dockerfile \
  -t $ACR_SERVER/documind-api:$IMAGE_TAG \
  .

docker push $ACR_SERVER/documind-api:$IMAGE_TAG
```

> [!TIP]
> Usa el commit SHA como tag para trazabilidad: `IMAGE_TAG=$(git rev-parse --short HEAD)`

---

## Fase 4 — Activar Container App

Ahora que la imagen existe en ACR, re-aplica Terraform con el `image_tag`:

```bash
cd terraform/environments/dev

terraform apply \
  -var="image_tag=$IMAGE_TAG" \
  -auto-approve
```

Terraform creará la `azurerm_container_app` con la imagen publicada.

Verifica que arrancó:

```bash
FQDN=$(terraform output -raw container_app_fqdn)
curl https://$FQDN/health
# {"status":"healthy","service":"documind-ai","version":"0.1.0"}
```

Si el healthcheck falla, revisa los logs:

```bash
az containerapp logs show \
  --name ca-documind \
  --resource-group rg-documind \
  --follow
```

---

## Fase 5 — Configurar Webhook WhatsApp

### 5.1 — URL del webhook

```bash
FQDN=$(cd terraform/environments/dev && terraform output -raw container_app_fqdn)
echo "Webhook URL: https://$FQDN/webhook"
```

### 5.2 — Registrar en Meta for Developers

1. Ve a [developers.facebook.com](https://developers.facebook.com) → tu App → **WhatsApp → Configuration**.
2. En **Webhook**:
   - **Callback URL:** `https://<FQDN>/webhook`
   - **Verify Token:** el valor que cargaste en Key Vault como `whatsapp-verify-token`
3. Clic en **Verify and save** — Meta hará un `GET /webhook?hub.challenge=...` que el servidor responderá automáticamente.
4. En **Webhook fields**, suscríbete a `messages`.

### 5.3 — Test: enviar un mensaje y ver la respuesta

Desde el número de teléfono de prueba de tu Meta App, envía un mensaje de texto al número configurado. Deberías recibir la respuesta de DocuMind AI en WhatsApp.

Monitorea en tiempo real:

```bash
az containerapp logs show \
  --name ca-documind \
  --resource-group rg-documind \
  --follow
```

---

## Troubleshooting rápido

| Síntoma | Causa probable | Solución |
|---|---|---|
| `terraform apply` falla en Azure OpenAI | Cuota no aprobada | Solicitar acceso en [aka.ms/oai/access](https://aka.ms/oai/access) |
| Container App queda en estado `Failed` | Imagen no encontrada en ACR | Verificar `image_tag` correcto y que `az acr login` fue exitoso |
| Webhook 403 en Meta | HMAC signature inválido | Verificar que `whatsapp-app-secret` en KV coincide con el App Secret de Meta |
| Webhook verify falla | Verify token no coincide | El valor en KV (`whatsapp-verify-token`) debe ser idéntico al que pusiste en Meta |
| `az keyvault secret set` → 403 | Sin rol `Key Vault Secrets Officer` | Ejecutar el `az role assignment create` del Paso 2.1 |
