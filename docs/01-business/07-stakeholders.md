# Responsables y Decisiones — DocuMind AI

## Responsable del Proyecto

- **Líder Técnico, Arquitectura y Producto:** Naren Fragozo.
- **Alcance del Rol:** Definición de arquitectura cloud en Azure, implementación del backend FastAPI, pipeline RAG, infraestructura en Terraform y pruebas de calidad.

## Decisiones Clave de Producto y Diseño

1. **Canal único WhatsApp en MVP:** Se priorizó WhatsApp como interfaz conversacional por su ubicuidad, eliminando la necesidad de desarrollar y mantener un frontend web en la primera versión.
2. **Ecosistema Unificado Microsoft Azure:** Se seleccionó Azure para todo el ciclo de vida del backend (Container Apps, Blob Storage, AI Search, Microsoft Foundry, Key Vault) para aprovechar la seguridad integrada con Entra ID y Managed Identity.
3. **Aislamiento Estricto por Teléfono:** Cada archivo cargado y cada fragmento vectorial se asocia al número del remitente; las búsquedas filtran obligatoriamente por este valor sin permitir cruces de contexto.
4. **Respuestas con Citas Obligatorias:** El prompt del sistema fuerza al modelo a citar el documento y número de página, o manifestar la ausencia de evidencia si la similitud no supera el umbral configurado.
