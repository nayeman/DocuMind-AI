# 001 — Configuración y Ejecución Local — DocuMind AI

Guía paso a paso para configurar, probar y ejecutar DocuMind AI en tu entorno local.

---

## 1. Requisitos Previos

- **Python:** 3.12 o superior.
- **Gestor de paquetes:** [`uv`](https://docs.astral.sh/uv/) instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
- **Azure CLI:** `az login` (opcional en desarrollo local si usas `DefaultAzureCredential` con tu cuenta de Azure).
- **Cuenta Meta WhatsApp Business:** Número de teléfono de prueba y token de acceso en Meta for Developers (para pruebas end-to-end con WhatsApp real).

---

## 2. Instalación de Dependencias

Clona el repositorio y sincroniza el entorno virtual con `uv`:

```bash
cd DocuMindAI
uv sync
```

---

## 3. Configuración de Variables de Entorno

Copia la plantilla `.env.example` para generar tu archivo `.env`:

```bash
cp .env.example .env
```

Edita `.env` con los valores correspondientes a tus recursos:

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

# --- Microsoft Foundry / Azure OpenAI ---
AZURE_OPENAI_ENDPOINT=https://tuopenai.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_EMBEDDING_DIMENSIONS=1536

# --- Azure Identity (Opcional en local) ---
# Dejar vacío si tienes sesión activa con `az login` (DefaultAzureCredential)
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_TENANT_ID=
```

---

## 4. Ejecución de Pruebas Automatizadas

Ejecuta la suite de pruebas unitarias y de integración (se ejecutan sin necesidad de red externa usando fakes y mocks):

```bash
uv run pytest -v
```

Verifica linters y análisis de tipos:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src tests
```

---

## 5. Iniciar el Servidor de Desarrollo

Levanta la aplicación FastAPI con recarga automática:

```bash
uv run uvicorn documind.main:app --reload --host 0.0.0.0 --port 8000
```

Verifica que el servicio esté respondiendo:

```bash
curl http://localhost:8000/health
# Respuesta esperada: {"status":"healthy","service":"documind-ai","version":"0.1.0"}
```

---

## 6. Probar Webhooks con Meta WhatsApp

Para exponer tu servidor local a Meta durante el desarrollo:

1. Inicia un túnel HTTPS (ejemplo con `ngrok`):
   ```bash
   ngrok http 8000
   ```
2. En la consola de **Meta for Developers** (WhatsApp > Configuration):
   - **Callback URL:** `https://<tu-subdominio-ngrok>.ngrok-free.app/webhook`
   - **Verify Token:** El valor configurado en `WHATSAPP_WEBHOOK_VERIFY_TOKEN`.
3. Haz clic en **Verify and save**. Meta enviará una solicitud `GET /webhook` que tu servidor validará respondiendo con el challenge.
4. Suscríbete al campo `messages` del webhook para comenzar a recibir mensajes y documentos enviados al número de prueba.
