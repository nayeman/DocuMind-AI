# Kickoff del Proyecto — DocuMind AI

## Información General

- **Fecha:** Noviembre 2026
- **Responsable:** Naren Fragozo (Arquitectura y Desarrollo)
- **Repositorio:** `DocuMindAI`

## Objetivo del Proyecto

Desarrollar y desplegar un MVP funcional de asistente documental para WhatsApp respaldado por Microsoft Azure, modelos generativos de Microsoft Foundry y búsqueda vectorial en Azure AI Search, con infraestructura administrada vía Terraform.

## Alcance del MVP

### Incluido en el MVP

- **Entrada WhatsApp:** Recepción de eventos de mensajes y documentos vía Meta WhatsApp Cloud API.
- **Almacenamiento:** Carga de documentos en Azure Blob Storage organizados por número de usuario.
- **Procesamiento Documental:** Extracción de texto (`pypdf`, `python-docx`), chunking basado en tokens (`tiktoken`) y generación de embeddings (1536 dimensiones).
- **Indexación Vectorial:** Almacenamiento y búsqueda por similitud en Azure AI Search con filtro estricto por `user_phone`.
- **RAG Pipeline:** Generación de respuestas mediante Microsoft Foundry (`gpt-4o` / Azure OpenAI) con contexto documental y referencias a páginas.
- **Infraestructura como Código:** Despliegue automatizado con Terraform en Azure (Container Apps, Storage, AI Search, Foundry, Key Vault).

### Fuera de Alcance Inicial

- Interfaz web o portal administrativo independiente.
- Reconocimiento óptico de caracteres (OCR) para imágenes o PDFs escaneados complejos.
- Integración con repositorios empresariales como SharePoint o Google Drive.
- Agentes multi-paso o herramientas de ejecución de código.
