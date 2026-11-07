# Historias de Usuario — DocuMind AI

## Ingesta y Gestión de Documentos

1. **US-01 Carga de documentos:** Como usuario de WhatsApp, quiero enviar un documento en formato PDF, DOCX o TXT para que el asistente lo procese y esté disponible para consultas.
2. **US-02 Confirmación de indexación:** Como usuario, quiero recibir un mensaje de confirmación una vez que mi documento haya sido analizado e indexado, indicando cuántos fragmentos se generaron.
3. **US-03 Validación de formato y tamaño:** Como usuario, quiero recibir un mensaje claro de error si envío un archivo con formato no soportado (distinto a PDF, DOCX o TXT) o que supere los 20 MB.

## Consulta y Recuperación (RAG)

4. **US-04 Preguntas en lenguaje natural:** Como usuario, quiero hacer preguntas sobre el contenido de mis documentos directamente en el chat y recibir respuestas claras y concisas.
5. **US-05 Citas y referencias:** Como usuario, quiero que cada respuesta mencione explícitamente el documento y el número de página de donde proviene la información.
6. **US-06 Respuesta sin evidencia:** Como usuario, quiero que el asistente me indique honestamente cuando la respuesta no se encuentre en mis documentos, evitando inventar información.
7. **US-07 Señal de procesamiento:** Como usuario, quiero ver un indicador de lectura/escritura en WhatsApp mientras se procesa mi consulta para saber que el sistema está respondiendo.

## Seguridad y Privacidad

8. **US-08 Aislamiento de documentos por usuario:** Como usuario, quiero tener la garantía de que mis documentos y preguntas son privados y no pueden ser consultados por ningún otro número de teléfono.
