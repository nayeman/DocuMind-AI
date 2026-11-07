# Vista de Despliegue — DocuMind AI

## Arquitectura de Despliegue en Microsoft Azure

DocuMind AI se ejecuta en una arquitectura serverless basada en **Azure Container Apps (ACA)** conectada de forma segura a los servicios administrados de datos e IA en Azure.

```mermaid
flowchart TD
    subgraph Internet
        META[Meta WhatsApp Cloud API]
    end

    subgraph "Suscripción de Azure"
        subgraph "Red y Hosting"
            ING[ACA Ingress HTTPS Público]
            APP[Azure Container App: documind-ai<br/>FastAPI + Uvicorn]
            ACR[Azure Container Registry: documindacr]
        end

        subgraph "Seguridad e Identidad"
            UAMI[User Assigned Managed Identity]
            KV[Azure Key Vault]
        end

        subgraph "Datos e IA"
            BLOB[(Azure Blob Storage)]
            SEARCH[(Azure AI Search)]
            FND[Microsoft Foundry / Azure OpenAI]
        end

        subgraph "Observabilidad"
            LOGS[Log Analytics Workspace]
            APPINS[Application Insights]
        end
    end

    META -->|POST /webhook| ING
    ING --> APP
    ACR -.->|Pull Image| APP
    APP -->|Logs & Métricas| LOGS
    APP -->|Telemetría| APPINS

    APP <-->|Managed Identity| UAMI
    UAMI -->|Lectura de Secretos| KV
    UAMI -->|Storage Blob Data Contributor| BLOB
    UAMI -->|Search Index Data Contributor| SEARCH
    UAMI -->|Cognitive Services OpenAI User| FND
```

---

## Componentes de la Solución Desplegada

### 1. Ingress y Container App
- **Ingress:** HTTPS habilitado con terminación TLS automática en el dominio asignado por Azure Container Apps (`https://<app>.<region>.azurecontainerapps.io`).
- **Escalado:** Configuración de escalado basado en concurrencia de peticiones HTTP (0 a 10 réplicas según tráfico).
- **Health Check:** Endpoints expuestos en `/health` para sondas de liveness y readiness.

### 2. Contenedor Docker
- Basado en `python:3.12-slim` con empaquetado multi-etapa para generar imágenes ligeras y seguras.
- Ejecuta Uvicorn en el puerto 8000 sirviendo la aplicación FastAPI.

### 3. Conexiones Administradas
- **Sin credenciales:** La Container App asume la identidad administrada para autenticarse contra Blob Storage, AI Search y Azure OpenAI mediante tokens Entra ID de corta duración rotados automáticamente por Azure.
- **Secretos de Meta:** El token de acceso y el secreto de webhook de WhatsApp se guardan en Key Vault y se inyectan como variables de entorno seguras en la Container App.
