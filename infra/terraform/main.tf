locals {
  resource_group_name = "${var.project_name}-${var.environment}-rg"
  service_plan_name   = "${var.project_name}-${var.environment}-functions-plan"

  base_tags = merge(
    {
      application = "FinBridge Cloud"
      environment = var.environment
      purpose     = "synthetic-candidate-demo"
      managed_by  = "terraform"
    },
    var.tags,
  )

  container_names = toset([
    "raw",
    "processed",
    "quarantine",
    "audit",
  ])
}

resource "azurerm_resource_group" "finbridge" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.base_tags
}

resource "azurerm_storage_account" "finbridge" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.finbridge.name
  location                 = azurerm_resource_group.finbridge.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  min_tls_version          = "TLS1_2"

  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = true

  blob_properties {
    versioning_enabled = true
  }

  tags = local.base_tags
}

resource "azurerm_storage_container" "finbridge" {
  for_each = local.container_names

  name                  = each.value
  storage_account_id    = azurerm_storage_account.finbridge.id
  container_access_type = "private"
}

resource "azurerm_service_plan" "functions" {
  name                = local.service_plan_name
  resource_group_name = azurerm_resource_group.finbridge.name
  location            = azurerm_resource_group.finbridge.location
  os_type             = "Linux"
  sku_name            = "Y1"
  tags                = local.base_tags
}

resource "azurerm_linux_function_app" "finbridge" {
  name                = var.function_app_name
  resource_group_name = azurerm_resource_group.finbridge.name
  location            = azurerm_resource_group.finbridge.location
  service_plan_id     = azurerm_service_plan.functions.id

  storage_account_name       = azurerm_storage_account.finbridge.name
  storage_account_access_key = azurerm_storage_account.finbridge.primary_access_key

  functions_extension_version = "~4"
  https_only                  = true

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME       = "python"
    AzureWebJobsFeatureFlags       = "EnableWorkerIndexing"
    FINBRIDGE_STORAGE              = azurerm_storage_account.finbridge.primary_connection_string
    FINBRIDGE_RAW_CONTAINER        = azurerm_storage_container.finbridge["raw"].name
    FINBRIDGE_PROCESSED_CONTAINER  = azurerm_storage_container.finbridge["processed"].name
    FINBRIDGE_QUARANTINE_CONTAINER = azurerm_storage_container.finbridge["quarantine"].name
    FINBRIDGE_AUDIT_CONTAINER      = azurerm_storage_container.finbridge["audit"].name
  }

  site_config {
    application_stack {
      python_version = "3.12"
    }
  }

  tags = local.base_tags
}
