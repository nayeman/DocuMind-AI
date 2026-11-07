resource "azurerm_log_analytics_workspace" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

locals {
  alerts_enabled = var.alerts_enabled && var.alert_email != ""
}

resource "azurerm_monitor_action_group" "this" {
  count = local.alerts_enabled ? 1 : 0

  name                = "ag-${var.name}"
  resource_group_name = var.resource_group_name
  short_name          = "newspilot"
  tags                = var.tags

  email_receiver {
    name                    = "operator"
    email_address           = var.alert_email
    use_common_alert_schema = true
  }
}

resource "azurerm_monitor_scheduled_query_rules_alert_v2" "revision_failures" {
  count = local.alerts_enabled ? 1 : 0

  name                = "aca-revision-failures-${var.name}"
  resource_group_name = var.resource_group_name
  location            = var.location
  display_name        = "Container App revision failures: ${var.container_app_name}"
  description         = "A Container App revision for ${var.container_app_name} failed to provision."
  severity            = 1
  enabled             = true

  evaluation_frequency  = "PT5M"
  window_duration       = "PT5M"
  scopes                = [azurerm_log_analytics_workspace.this.id]
  skip_query_validation = true
  tags                  = var.tags

  criteria {
    query = <<-KQL
      ContainerAppSystemLogs_CL
      | where TimeGenerated > ago(5m)
      | where ContainerAppName_s == "${var.container_app_name}"
      | where Log_s has_any ("ContainerCrashing", "ErrImagePull", "Timeout")
    KQL

    time_aggregation_method = "Count"
    operator                = "GreaterThan"
    threshold               = 0

    failing_periods {
      minimum_failing_periods_to_trigger_alert = 1
      number_of_evaluation_periods             = 1
    }
  }

  action {
    action_groups = [azurerm_monitor_action_group.this[0].id]
  }
}
