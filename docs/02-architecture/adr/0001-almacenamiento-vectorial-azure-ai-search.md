# ADR-0001: Adopción de Azure AI Search y Azure Blob Storage para RAG con Aislamiento de Usuario

- **Estado:** Aceptada
- **Fecha:** 2026-11-07
- **Responsables de la decisión:** Naren Fragozo
- **Sustituye:** —
- **Sustituido por:** —

---

## Contexto

DocuMind AI requiere procesar documentos no estructurados (PDF, DOCX, TXT) cargados por usuarios a través de WhatsApp y responder preguntas sobre su contenido mediante un flujo RAG.
Los requisitos críticos del sistema son:
1. Almacenar los archivos originales de forma duradera y económica.
2. Indexar representaciones vectoriales densas (1536 dimensiones) para búsqueda por similitud semántica de baja latencia.
3. Garantizar un aislamiento estricto de documentos y fragmentos entre números de teléfono de WhatsApp (multi-tenancy a nivel de aplicación).
4. Integrarse de forma nativa con la identidad administrada de Azure (Entra ID / Managed Identity) para evitar claves estáticas en el backend.

---

## Decisión

1. **Azure Blob Storage:** Utilizar un contenedor privado de Azure Blob Storage (`documind-documents`) para almacenar los binarios originales, organizando las rutas con el prefijo del usuario: `{user_phone}/{document_id}/{filename}`.
2. **Azure AI Search:** Utilizar Azure AI Search como base de datos vectorial mediante un índice optimizado con el algoritmo HNSW (`VectorSearchProfile`), almacenando metadatos (`document_id`, `filename`, `page`, `user_phone`, `text`) junto con el vector `Collection(Edm.Single)`.
3. **Filtro de Seguridad Obligatorio:** Toda consulta RAG debe ejecutar un filtro estricto por `user_phone eq '{sender_phone}'` en Azure AI Search, garantizando que el usuario solo pueda recuperar fragmentos de sus propios documentos.

---

## Consecuencias

### Positivas
- Solución administrada y escalable dentro del mismo ecosistema cloud y grupo de recursos de Azure.
- Seguridad robusta mediante asignaciones de roles RBAC con Managed Identity (`Storage Blob Data Contributor`, `Search Index Data Contributor`).
- Búsqueda vectorial HNSW de alto rendimiento y bajo overhead operacional.
- Trazabilidad y auditoría integradas con Azure Monitor y Log Analytics.

### Negativas / Consideraciones
- Costo base asociado a la instancia de Azure AI Search (tier Basic/Standard).
- Los nombres de archivo y números de teléfono deben sanitizarse para evitar vulnerabilidades de salto de directorio o inyección OData en las consultas.

---

## Alternativas Consideradas

- **ChromaDB / SQLite local:** Descartada para producción debido a la falta de persistencia distribuida en Azure Container Apps y problemas de escalabilidad con múltiples instancias.
- **PostgreSQL con pgvector:** Descartada para simplificar la infraestructura inicial y aprovechar las capacidades administradas de indexación vectorial de Azure AI Search dentro del ecosistema nativo de Microsoft Foundry.

