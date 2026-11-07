resource "azurerm_container_app_environment" "this" {
  name                       = var.environment_name
  location                   = var.location
  resource_group_name        = var.resource_group_name
  infrastructure_subnet_id   = var.infrastructure_subnet_id
  log_analytics_workspace_id = var.log_analytics_workspace_id
  tags                       = var.tags

  dynamic "workload_profile" {
    for_each = var.workload_profile_enabled ? [true] : []

    content {
      name                  = "Consumption"
      workload_profile_type = "Consumption"
    }
  }
}

resource "azurerm_container_app" "this" {
  count = var.image != "" ? 1 : 0

  name                         = var.name
  container_app_environment_id = azurerm_container_app_environment.this.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  workload_profile_name        = var.workload_profile_enabled ? "Consumption" : null
  tags                         = var.tags

  identity {
    type         = "UserAssigned"
    identity_ids = [var.registry_identity_id]
  }

  registry {
    server   = var.registry_server
    identity = var.registry_identity_id
  }

  secret {
    name  = "postgres-dsn"
    value = var.postgres_dsn
  }

  dynamic "secret" {
    for_each = var.secret_refs
    content {
      name                = secret.key
      key_vault_secret_id = secret.value
      identity            = var.registry_identity_id
    }
  }

  template {
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    container {
      name   = var.name
      image  = var.image
      cpu    = var.container_cpu
      memory = var.container_memory

      env {
        name  = "AGENT_MODEL"
        value = var.agent_model
      }

      env {
        name  = "SOURCES_FILE"
        value = var.sources_file
      }

      env {
        name  = "LINKEDIN_ENABLED"
        value = tostring(var.linkedin_enabled)
      }

      env {
        name  = "APP_ENVIRONMENT"
        value = "azure"
      }

      env {
        name  = "WHATSAPP_REQUIRE_SIGNATURE"
        value = "true"
      }

      env {
        name  = "RUN_ENDPOINT_ENABLED"
        value = "false"
      }

      env {
        name        = "POSTGRES_DSN"
        secret_name = "postgres-dsn"
      }

      env {
        name  = "POSTGRES_REQUIRED"
        value = "true"
      }

      dynamic "env" {
        for_each = var.optional_secret_envs
        content {
          name        = env.key
          secret_name = env.value
        }
      }

      dynamic "env" {
        for_each = var.optional_plain_envs
        content {
          name  = env.key
          value = env.value
        }
      }

      liveness_probe {
        transport = "HTTP"
        port      = var.ingress_port
        path      = "/health"
      }

      readiness_probe {
        transport = "HTTP"
        port      = var.ingress_port
        path      = "/ready"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = var.ingress_port

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}
