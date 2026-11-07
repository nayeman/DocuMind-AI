# Métricas de Éxito — DocuMind AI

## Métricas de Calidad de la Experiencia

- **Latencia de Respuesta RAG:** Tiempo total desde que el usuario envía la pregunta hasta que recibe la respuesta en WhatsApp inferior a 4 segundos.
- **Tasa de Respuestas Fundamentadas:** 100% de las respuestas generadas deben contener referencias al documento y página de origen.
- **Cero Alucinaciones:** Ante preguntas sobre temas no contenidos en los documentos cargados, el sistema debe abstenerse de especular e informar la falta de evidencia en el 100% de los casos evaluados.

## Métricas Operativas y Técnicas

- **Aislamiento de Privacidad:** Cero filtraciones de documentos o respuestas entre diferentes números de teléfono (100% de cumplimiento en filtros de búsqueda y rutas de blob).
- **Tasa de Éxito en Ingesta:** Mayor a 98% en documentos válidos de formatos soportados (PDF, DOCX, TXT <= 20 MB).
- **Disponibilidad del Servicio:** Disponibilidad de la API en Azure Container Apps superior al 99.5%.
- **Cobertura de Pruebas Automatizadas:** 100% de pruebas unitarias y de integración pasando en el pipeline de CI.
