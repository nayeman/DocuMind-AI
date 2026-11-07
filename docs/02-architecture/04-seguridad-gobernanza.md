# Seguridad y Gobernanza — DocuMind AI

La seguridad y la privacidad de los documentos procesados constituyen el núcleo de diseño de DocuMind AI.

---

## 1. Principios de Seguridad

- **Aislamiento Multi-Tenant:** Cada usuario se identifica por su número de teléfono. Las rutas en Blob Storage y los filtros OData en Azure AI Search imponen un límite infranqueable entre usuarios.
- **Autenticación sin Contraseñas:** Se utiliza Microsoft Entra ID y Managed Identity en Azure Container Apps. Ninguna clave de Azure se almacena en el código ni en variables planas.
- **Validación Criptográfica de Entrada:** Toda solicitud entrante desde Meta debe contener una firma HMAC-SHA256 válida coincidente con el secreto de la aplicación.
- **Principio de Mínimo Privilegio:** Los roles RBAC de Azure están acotados a los alcances exactos requeridos (Data Contributor, OpenAI User).

---

## 2. Matriz de Riesgos y Controles Implementados

| Riesgo | Impacto | Control Implementado | Estado |
|---|---|---|---|
| **Falsificación de solicitudes (Spoofing de Webhook)** | Alto | Verificación de firma `X-Hub-Signature-256` con `hmac.compare_digest` en [`api/security.py`](../../src/documind/api/security.py). Rechazo inmediato con HTTP 401 si la firma no coincide o falta el secreto. | Implementado |
| **Acceso cruzado entre usuarios (Fuga de datos)** | Crítico | Aislamiento en Blob Storage por prefijo `{user_phone}/` y filtro forzado en Azure AI Search: `user_phone eq '{safe_phone}'`. | Implementado |
| **Inyección OData en filtros de búsqueda** | Alto | Sanitización de comillas simples (`user_phone.replace("'", "''")`) antes de componer la cláusula de filtro en [`clients/ai_search.py`](../../src/documind/clients/ai_search.py). | Implementado |
| **Ataque de salto de directorio (Path Traversal)** | Alto | Sanitización con `Path(filename).name` y filtrado alfanumérico en `user_phone` al construir rutas de blob. | Implementado |
| **Fuga de información en errores (CWE-209)** | Medio | Captura de excepciones globales en [`main.py`](../../src/documind/main.py); respuesta genérica `"Internal server error"` al cliente mientras el detalle técnico se envía a logs internos. | Implementado |
| **Archivos maliciosos o sobrecarga de recursos** | Medio | Lista blanca de extensiones permitidas (`pdf`, `docx`, `txt`) y validación estricta de tamaño máximo (20 MB). | Implementado |
| **Alucinación o invención de respuestas** | Medio | Umbral de score mínimo (`0.75`), prompt de sistema anti-alucinaciones y exigencia de citas por documento y página. | Implementado |
| **Exposición de credenciales en repositorios** | Crítico | Exclusión estricta de `.env` en `.gitignore`, inyección de secretos vía Key Vault en producción y plantilla segura `.env.example`. | Implementado |

---

## 3. Retención y Manejo de Datos

- **Documentos Originales:** Almacenados en Azure Blob Storage con cifrado en reposo (SSE con claves administradas por Microsoft).
- **Fragmentos Vectoriales:** Almacenados en Azure AI Search; pueden eliminarse por documento o por usuario si se solicita.
- **Tránsito de Datos:** Todas las comunicaciones externas (Meta WhatsApp, Azure SDK) se realizan exclusivamente sobre TLS 1.3 / HTTPS.
