# Criterios de Aceptación — DocuMind AI

## 1. Webhook y Recepción de Mensajes

- [ ] El endpoint `GET /webhook` valida correctamente el `hub.challenge` y `hub.verify_token` configurados en Meta.
- [ ] El endpoint `POST /webhook` valida la firma criptográfica HMAC-SHA256 (`x-hub-signature-256`) usando `whatsapp_app_secret`. Solicitudes con firmas inválidas reciben HTTP 401.
- [ ] La respuesta HTTP 200 a Meta se emite de inmediato; el procesamiento de documentos o consultas se delega a `BackgroundTasks`.

## 2. Ingesta de Documentos

- [ ] Soporta extensiones `.pdf`, `.docx` y `.txt`.
- [ ] Rechaza archivos que superen los 20 MB y notifica al usuario por WhatsApp.
- [ ] Almacena el binario original en Azure Blob Storage bajo la ruta aislada: `{user_phone}/{document_id}/{filename}`.
- [ ] Extrae el texto respetando los números de página cuando aplica (PDF).
- [ ] Fragmenta el texto en chunks de 512 tokens con solapamiento de 64 tokens (`tiktoken`).
- [ ] Genera embeddings vectoriales de 1536 dimensiones mediante Microsoft Foundry / Azure OpenAI.
- [ ] Indexa los fragmentos en Azure AI Search asociando el campo `user_phone`.
- [ ] Envía un mensaje de confirmación al usuario indicando el nombre del archivo y número de chunks indexados.

## 3. Consulta RAG

- [ ] Envía señal de procesamiento (`send_typing_indicator` / marca de leído) al recibir una pregunta.
- [ ] Genera el embedding de la pregunta del usuario.
- [ ] Ejecuta búsqueda vectorial HNSW en Azure AI Search aplicando el filtro de seguridad obligatorio: `user_phone eq '{phone}'`.
- [ ] Si la similitud máxima no alcanza el umbral de relevancia (0.75) o el índice está vacío, responde con mensaje de cortesía indicando que no hay información suficiente.
- [ ] Si existen fragmentos relevantes, genera la respuesta con Microsoft Foundry incluyendo las fuentes citadas (ej. `[archivo.pdf, pág. 3]`).

## 4. Seguridad y Despliegue

- [ ] Cero credenciales o claves privadas registradas en código o control de versiones.
- [ ] Infraestructura aprovisionada mediante Terraform con autenticación Entra ID / Managed Identity.
