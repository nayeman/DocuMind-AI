resource "azurerm_cognitive_account" "this" {
  name                          = var.name
  location                      = var.location
  resource_group_name           = var.resource_group_name
  kind                          = "OpenAI"
  sku_name                      = var.sku_name
  custom_subdomain_name         = var.custom_subdomain_name
  public_network_access_enabled = var.public_network_access_enabled
  local_auth_enabled            = var.local_auth_enabled
  tags                          = var.tags
}

resource "azurerm_cognitive_deployment" "chat" {
  name                 = var.model_name
  cognitive_account_id = azurerm_cognitive_account.this.id

  model {
    format  = "OpenAI"
    name    = var.model_name
    version = var.model_version
  }

  scale {
    type     = "GlobalStandard"
    capacity = var.capacity
  }

  version_upgrade_option = var.version_upgrade_option
  rai_policy_name        = var.rai_policy_name
}

resource "azurerm_cognitive_deployment" "embedding" {
  count                = var.embedding_model_name != "" ? 1 : 0
  name                 = var.embedding_model_name
  cognitive_account_id = azurerm_cognitive_account.this.id

  model {
    format  = "OpenAI"
    name    = var.embedding_model_name
    version = var.embedding_model_version
  }

  scale {
    type     = "GlobalStandard"
    capacity = var.embedding_capacity
  }

  version_upgrade_option = var.version_upgrade_option
  rai_policy_name        = var.rai_policy_name
}
