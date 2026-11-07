# Documentación de DocuMind AI

Documentación técnica y de producto para **DocuMind AI**: Asistente inteligente de consulta documental en WhatsApp potenciado por Microsoft Azure y arquitectura RAG.

---

## Estructura

```text
docs/
├── README.md
├── 01-business/       # Caso de negocio, kickoff, historias de usuario, criterios y roadmap
│   ├── 01-business-case.md
│   ├── 02-kickoff.md
│   ├── 03-user-stories.md
│   ├── 04-acceptance-criteria.md
│   ├── 05-success-metrics.md
│   ├── 06-project-roadmap.md
│   └── 07-stakeholders.md
│
├── 02-architecture/  # Arquitectura, infraestructura, flujos, seguridad, despliegue y pruebas
│   ├── 01-vision-general.md
│   ├── 02-infraestructura.md
│   ├── 03-flujo-de-ejecucion.md
│   ├── 04-seguridad-gobernanza.md
│   ├── 06-vista-despliegue.md
│   ├── 08-estrategia-pruebas.md
│   └── adr/           # Decisiones de arquitectura (ADRs)
│
└── 05-guias/          # Guías operativas y configuración
    └── 001-setup.md
```

---

## Orden de Lectura Recomendado

1. **Visión de Producto:** [`01-business/01-business-case.md`](01-business/01-business-case.md) y [`01-business/03-user-stories.md`](01-business/03-user-stories.md).
2. **Arquitectura del Sistema:** [`02-architecture/01-vision-general.md`](02-architecture/01-vision-general.md) y [`02-architecture/03-flujo-de-ejecucion.md`](02-architecture/03-flujo-de-ejecucion.md).
3. **Infraestructura y Seguridad:** [`02-architecture/02-infraestructura.md`](02-architecture/02-infraestructura.md) y [`02-architecture/04-seguridad-gobernanza.md`](02-architecture/04-seguridad-gobernanza.md).
4. **Puesta en Marcha Local:** [`05-guias/001-setup.md`](05-guias/001-setup.md).
