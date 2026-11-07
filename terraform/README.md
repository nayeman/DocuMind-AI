# Terraform — NewsPilot

Infraestructura de NewsPilot en Azure organizada en módulos reutilizables y
entornos aislados.

## Estructura

```text
terraform/
├── modules/
│   ├── base/                  ← un módulo por servicio Azure
│   └── composition/newspilot/ ← orquesta base + RBAC para el dominio
└── environments/{dev,stg,prod}/ ← roots que solo llaman a la composición
```

- `modules/base/*`: definición genérica y parametrizada de cada servicio.
- `modules/composition/newspilot`: llama a los base, aplica tags y RBAC.
- `environments/*`: únicos roots ejecutables; contienen provider y `module "newspilot"`.

## Uso

```bash
make tf-init ENV=dev BACKEND_CONFIG=../../backend.dev.hcl
make tf-validate ENV=dev
make tf-plan ENV=dev
make tf-apply ENV=dev
```

`tf-plan`/`tf-apply` inyectan `image_tag=$(git rev-parse --short HEAD)`. Para
la primera aplicación, sin imagen publicada, usa `make tf-apply ENV=dev IMAGE_TAG=`
y después `make build-push ENV=dev && make tf-apply ENV=dev`.

O directamente:

```bash
TF=terraform/environments/dev
terraform -chdir=$TF init
terraform -chdir=$TF plan -var="image_tag=$(git rev-parse --short HEAD)"
terraform -chdir=$TF apply -var="image_tag=$(git rev-parse --short HEAD)"
```

## Secretos

`.env` configura la aplicación local y no se ejecuta ni se pasa a Terraform.
Los secretos de runtime se cargan directamente a Key Vault con
`make tf-secrets-sync ENV=dev`; Terraform recibe solo las URI versionless.
No guardes secretos de runtime en `TF_VAR_*`, `*.tfvars` ni argumentos `-var`.
Para desarrollo local, copia
`.env.example` a `.env` y completa allí los secretos de la aplicación. Para cada entorno, copia
`terraform/environments/<env>/terraform.tfvars.example` a
`terraform/environments/<env>/terraform.tfvars` y ajusta los valores no
sensibles. Los `.tfvars` reales están excluidos de Git. La contraseña de
PostgreSQL aún se genera y consume dentro de Terraform y permanece en state;
su migración a una autenticación que no exponga credenciales en state sigue
pendiente.

`.env` evita que los secretos entren al repositorio. Los secretos de runtime
ya no se envían a Terraform; el state sigue conteniendo la contraseña/DSN de
PostgreSQL. Al migrar un entorno existente, rota los secretos de runtime que
antes llegaron al state; las versiones previas del backend pueden conservarlos.
`sensitive` solo oculta valores en la salida; no cifra ni elimina datos del
state. Para entornos compartidos usa backend remoto Azure Storage con cifrado, acceso RBAC mínimo,
red restringida y recuperación protegida. No compartas ni publiques el state,
los planes ni logs de CI. El state local también contiene secretos: mantenlo
fuera de Git y en un disco protegido. `make tf-plan/tf-apply` usa `umask 077`
para crear archivos accesibles solo por el usuario actual; si ejecutas
Terraform directamente, configura antes `umask 077` también.

Si alguno de los `.tfvars` versionados contenía credenciales reales, quitarlo
del commit actual no las borra del historial: revoca/rota esas credenciales y
limpia el historial remoto según la política del repositorio.

## Backend remoto

Los roots declaran el backend `azurerm` sin valores incrustados. Copia
`terraform/backend.hcl.example` a `terraform/backend.<env>.hcl`, completa los
datos no secretos del Storage Account, e inicializa/migra el state:

```bash
make tf-init ENV=prod BACKEND_CONFIG=../../backend.prod.hcl
```

La autenticación del backend usa Entra ID/CLI (`az login`); no guardes access
keys en el archivo backend. Revisa un plan después de la migración para
confirmar que no propone recrear recursos.

## Migración privada de PostgreSQL en producción

`private_network_enabled = true` en `prod` crea en paralelo una VNet, subredes
delegadas, DNS privado, un PostgreSQL con sufijo `-private` y una Container App
con el mismo sufijo. El PostgreSQL y la Container App públicos permanecen
activos: Terraform no los destruye en esta etapa.

Antes de aplicar, revisa que los CIDR de `network_address_space`,
`container_apps_subnet_prefix` y `postgres_subnet_prefix` no se solapen con
redes existentes. Luego sigue este orden:

```bash
# 1. Mover el state local al backend remoto antes de cualquier cambio.
make tf-init ENV=prod BACKEND_CONFIG=../../backend.prod.hcl

# 2. Revisar el plan: debe crear recursos con sufijo -private y no destruir
#    el Postgres ni la Container App pública.
make tf-plan ENV=prod

# 3. Solo después de aprobar el plan, crear la ruta privada.
make tf-apply ENV=prod

# 4. Comprobar el endpoint nuevo antes de cambiar el callback de Meta.
terraform -chdir=terraform/environments/prod output -raw container_app_fqdn
```

Actualiza el callback de WhatsApp al FQDN nuevo, comprueba `/health`, `/ready`
y el flujo completo de conversación. El retiro del PostgreSQL público y de la
Container App anterior requiere un plan y una autorización separados, después
de confirmar que no queda cola ni conversación que conservar.

## Readiness

La Container App usa `/health` para liveness y `/ready` para readiness. `/ready`
comprueba Postgres mediante el pool del checkpointer y devuelve `503` si no
responde.
