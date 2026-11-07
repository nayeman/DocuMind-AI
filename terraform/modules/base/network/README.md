# Módulo base: network

Crea la red privada del despliegue: una subred delegada para Container Apps,
otra para PostgreSQL Flexible y la zona DNS privada enlazada a la VNet.

| Input | Descripción |
|---|---|
| `address_space` | CIDR de la VNet |
| `container_apps_subnet_prefix` | CIDR exclusivo delegado a `Microsoft.App/environments` |
| `postgres_subnet_prefix` | CIDR exclusivo delegado a PostgreSQL Flexible |
| `postgres_private_dns_zone_name` | Zona terminada en `.postgres.database.azure.com` |

Las subredes no se comparten con otros recursos. El tamaño mínimo de la
subred de Container Apps para perfiles de carga es `/27`; PostgreSQL Flexible
admite `/28` como mínimo.
