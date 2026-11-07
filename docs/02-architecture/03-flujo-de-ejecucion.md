# Flujos de Ejecución — DocuMind AI

DocuMind AI opera en dos flujos principales activados por eventos de webhook de WhatsApp: **Ingesta Documental** y **Consulta RAG**.

---

## 1. Flujo de Ingesta Documental

Se ejecuta cuando un usuario envía un documento adjunto (PDF, DOCX o TXT).

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario WhatsApp
    participant WA as Meta WhatsApp Cloud API
    participant API as FastAPI (Webhook)
    participant DOC as DocumentService
    participant BLOB as Azure Blob Storage
    participant EXT as Extraction & Chunking
    participant FND as Microsoft Foundry
    participant SRCH as Azure AI Search

    U->>WA: Envía documento (ej. contrato.pdf)
    WA->>API: POST /webhook (Payload con media_id y firma HMAC)
    Note over API: Valida firma HMAC-SHA256
    API-->>WA: HTTP 200 OK (Inmediato)
    
    API-)DOC: BackgroundTask: process_document()
    DOC->>WA: Descarga archivo binario con media_id
    DOC->>BLOB: Sube archivo a {phone}/{doc_id}/{filename}
    DOC->>EXT: Extrae texto con números de página
    DOC->>EXT: Fragmenta en tokens (512 tokens, 64 overlap)
    DOC->>FND: Genera embeddings en batch (1536 dims)
    DOC->>SRCH: Indexa chunks con filtro user_phone
    DOC->>WA: Envía confirmación: "Documento indexado con éxito"
    WA->>U: Notificación en WhatsApp
```

### Pasos de la Ingesta

1. **Recepción:** El webhook valida la firma HMAC del encabezado `X-Hub-Signature-256`. Si es válida, responde `200 OK` de inmediato a Meta para evitar reintentos.
2. **Descarga de Media:** En una tarea en segundo plano (`BackgroundTasks`), se consulta la URL del recurso en Graph API y se descargan los bytes con token de autorización.
3. **Persistencia Original:** Los bytes se guardan en el contenedor de Blob Storage bajo el prefijo aislado del usuario (`safe_phone/document_id/safe_filename`).
4. **Parseo y Chunking:** Se extrae el texto por página y se divide en fragmentos con `tiktoken`.
5. **Vectorización e Indexación:** Los fragmentos se envían en lote a Microsoft Foundry para obtener sus vectores y se indexan en Azure AI Search.
6. **Notificación:** Se envía un mensaje al usuario confirmando que su documento está listo para recibir preguntas.

---

## 2. Flujo de Consulta RAG

Se ejecuta cuando el usuario envía un mensaje de texto con una pregunta.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario WhatsApp
    participant WA as Meta WhatsApp Cloud API
    participant API as FastAPI (Webhook)
    participant RAG as RAGService
    participant FND as Microsoft Foundry
    participant SRCH as Azure AI Search

    U->>WA: Pregunta: "¿Cuáles son las cláusulas de pago?"
    WA->>API: POST /webhook (Mensaje de texto)
    Note over API: Valida firma HMAC-SHA256
    API-->>WA: HTTP 200 OK
    
    API-)RAG: BackgroundTask: answer_question()
    RAG->>WA: Envía typing indicator / marca de lectura
    RAG->>FND: Genera embedding de la consulta
    RAG->>SRCH: Búsqueda vectorial filtrada: user_phone eq '{phone}'
    
    alt Similitud < 0.75 o sin documentos
        RAG->>WA: Envía: "No encontré información relevante en tus documentos."
    else Fragmentos relevantes encontrados
        RAG->>FND: Genera respuesta con prompt de sistema + fragmentos
        Note over FND: Cita fuentes [archivo, pág. N]
        RAG->>WA: Envía respuesta estructurada
    end
    WA->>U: Mensaje final en WhatsApp
```

### Pasos de la Consulta

1. **Indicador Visual:** Se envía un indicador de escritura para brindar retroalimentación inmediata al usuario.
2. **Embedding de la Pregunta:** Se convierte la consulta en un vector mediante Microsoft Foundry (`text-embedding-3-small`).
3. **Búsqueda Vectorial Aislada:** Se ejecuta una consulta de similitud de coseno en Azure AI Search aplicando obligatoriamente el filtro `user_phone eq '{sender_phone}'` para garantizar que ningún usuario acceda a documentos ajenos.
4. **Evaluación de Relevancia:** Si el score de similitud no supera el umbral configurado (`0.75`), se responde con cortesía indicando que no hay suficiente evidencia.
5. **Generación con Referencias:** Si hay contexto válido, se llama al modelo de lenguaje (`gpt-4o`) con un prompt estricto que prohíbe alucinaciones y exige citas del documento y página.
