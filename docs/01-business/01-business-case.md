# Caso de Negocio — DocuMind AI

## Problema

Consultar y extraer información de documentos extensos (PDF, manuales, contratos, minutas en DOCX o notas en TXT) consume tiempo considerable y exige el uso de software específico o pantallas de escritorio. Los usuarios necesitan resolver preguntas puntuales sobre sus documentos de manera inmediata desde su canal de comunicación diario.

## Solución Propuesta

**DocuMind AI** es un asistente conversacional en WhatsApp que implementa Recuperación Aumentada por Generación (RAG):

1. El usuario envía un archivo (PDF, DOCX o TXT) por WhatsApp.
2. El sistema lo almacena, extrae el texto, genera fragmentos y crea embeddings vectoriales.
3. El usuario formula preguntas en lenguaje natural por chat.
4. El motor recupera los fragmentos pertinentes y genera una respuesta fundamentada citando el documento y la página.

## Valor Esperado

- **Cero fricción:** Interacción directa vía WhatsApp sin instalar apps adicionales ni crear cuentas independientes.
- **Respuestas fundamentadas:** Citas explícitas de la fuente y página correspondiente, reduciendo alucinaciones.
- **Aislamiento de información:** Cada usuario solo accede a los documentos cargados desde su propio número.

## Restricciones

- **Formatos soportados:** PDF, DOCX y TXT (hasta 20 MB por archivo).
- **Canal:** Meta WhatsApp Cloud API.
- **Nube:** Microsoft Azure administrado mediante Terraform y autenticado vía Entra ID (Managed Identity).
