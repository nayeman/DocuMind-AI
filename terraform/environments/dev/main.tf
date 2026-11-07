terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

module "documind" {
  source = "../../modules/composition/documind"

  environment  = var.environment
  project_name = var.project_name
  owner_email  = var.owner_email
  cost_center  = var.cost_center

  location            = var.location
  resource_group_name = var.resource_group_name
  container_app_name  = var.container_app_name
  acr_name_prefix     = var.acr_name_prefix
  image_tag           = var.image_tag

  chat_model_name         = var.chat_model_name
  chat_model_version      = var.chat_model_version
  chat_capacity           = var.chat_capacity
  embedding_model_name    = var.embedding_model_name
  embedding_model_version = var.embedding_model_version
  embedding_capacity      = var.embedding_capacity

  ai_search_sku            = var.ai_search_sku
  whatsapp_phone_number_id = var.whatsapp_phone_number_id

  min_replicas   = var.min_replicas
  max_replicas   = var.max_replicas
  alerts_enabled = var.alerts_enabled
  alert_email    = var.alert_email
}
