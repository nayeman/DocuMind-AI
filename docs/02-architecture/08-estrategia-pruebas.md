# Estrategia de Pruebas — DocuMind AI

La suite de pruebas de DocuMind AI garantiza la solidez del pipeline RAG, la seguridad del webhook de WhatsApp y la correcta integración de los clientes de Azure.

---

## 1. Pirámide de Pruebas

```text
       / \
      / E2E \       --> Pruebas de integración de Webhook y flujo HTTP
     /-------\
    /  Serv.  \     --> Pruebas de DocumentService y RAGService con fakes
   /-----------\
  /   Unitarias \   --> Pruebas de extracción, chunking y clientes Azure/WhatsApp
 /---------------\
```

---

## 2. Tipos de Pruebas y Cobertura

| Archivo de Prueba | Nivel | Qué valida |
|---|---|---|
| [`tests/test_extraction.py`](../../tests/test_extraction.py) | Unitario | Extracción de texto y conteo de páginas en PDF, DOCX y TXT; manejo de archivos vacíos o corruptos. |
| [`tests/test_chunking.py`](../../tests/test_chunking.py) | Unitario | División determinística de fragmentos con `tiktoken`, solapamiento de tokens y metadatos de chunk. |
| [`tests/unit/test_clients.py`](../../tests/unit/test_clients.py) | Unitario | Clientes de Azure (`BlobStorageClient`, `AISearchClient`, `FoundryClient`, `resolve_azure_credential`) y `WhatsAppClient` con mocks. |
| [`tests/unit/test_document_service.py`](../../tests/unit/test_document_service.py) | Servicio | Orquestación completa de ingesta con test doubles (`FakeBlob`, `FakeSearch`, `FakeFoundry`); validación de extensiones y límites de tamaño. |
| [`tests/unit/test_rag_service.py`](../../tests/unit/test_rag_service.py) | Servicio | Búsqueda vectorial, filtrado por score mínimo, prompts con citas de página y respuesta ante falta de documentos. |
| [`tests/test_webhook.py`](../../tests/test_webhook.py) | Integración | Endpoint `GET /webhook` (verificación de Meta), `POST /webhook` (firma HMAC-SHA256, mensajes de texto y documentos). |

---

## 3. Comandos de Verificación de Calidad

### Ejecución de Pruebas
```bash
uv run pytest -v
```

### Linters y Formato
```bash
uv run ruff check src tests
uv run ruff format --check src tests
```

### Análisis Estático de Tipos
```bash
uv run mypy src tests
```
