# Módulo base: Key Vault

Crea un Key Vault con RBAC, soft delete y purge protection. No crea secretos
con Terraform porque `azurerm_key_vault_secret.value` se conserva en texto plano
en el state. Los valores se cargan después del primer apply desde `.env` usando
`scripts/sync-keyvault-secrets.py`.
