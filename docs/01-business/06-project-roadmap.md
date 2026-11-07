# Hoja de Ruta — DocuMind AI

## Fase 1 — Core Documental & Pipeline RAG (Completado)

- [x] Configuración del proyecto con Python 3.12, `uv`, linters (`ruff`) y tipado estricto (`mypy`).
- [x] Extracción de texto de documentos PDF (`pypdf`), DOCX (`python-docx`) y TXT.
- [x] Estrategia de chunking por tokens con `tiktoken`.
- [x] Enriquecimiento de fragmentos con embeddings vectoriales (1536 dimensiones).
- [x] Pipeline RAG con recuperación en Azure AI Search y generación con Microsoft Foundry.
- [x] Aislamiento multi-tenant por número de teléfono en storage y búsqueda vectorial.

## Fase 2 — API Webhook & Seguridad (Completado)

- [x] Endpoints FastAPI para verificación y recepción de webhooks de Meta WhatsApp Cloud API.
- [x] Verificación de firma criptográfica HMAC-SHA256 (`x-hub-signature-256`).
- [x] Procesamiento asíncrono en background mediante `BackgroundTasks`.
- [x] Clientes Azure desacoplados y autenticados vía `TokenCredential` (Entra ID / Managed Identity).
- [x] Poda de dependencias innecesarias (`python-multipart`, `azure-keyvault-secrets`).

## Fase 3 — Infraestructura como Código (Completado)

- [x] Módulos Terraform base: Resource Group, ACA, ACR, Blob Storage, AI Search, Foundry, Key Vault, Application Insights.
- [x] Módulo de composición DocuMind con asignaciones RBAC de Managed Identity.
- [x] Configuración de entornos (`dev`, `staging`, `prod`).

## Fase 4 — Observabilidad & Mejoras Futuras

- [ ] Métricas en tiempo real y paneles en Application Insights / Azure Monitor.
- [ ] Soporte para documentos con tablas complejas y OCR para imágenes escaneadas.
- [ ] Opciones interactivas de mensajes de WhatsApp (botones de sugerencias o resumen rápido).
