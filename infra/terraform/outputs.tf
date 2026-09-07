output "resource_group_name" {
  description = "Azure Resource Group containing the optional FinBridge cloud mode."
  value       = azurerm_resource_group.finbridge.name
}

output "storage_account_name" {
  description = "Storage account backing FinBridge raw/processed/quarantine/audit evidence."
  value       = azurerm_storage_account.finbridge.name
}

output "storage_container_names" {
  description = "Private evidence containers used by the Python storage ports."
  value       = sort([for container in azurerm_storage_container.finbridge : container.name])
}

output "function_app_name" {
  description = "Linux Azure Function App hosting the thin Blob-trigger adapter."
  value       = azurerm_linux_function_app.finbridge.name
}

output "function_app_default_hostname" {
  description = "Default Azure hostname of the Function App."
  value       = azurerm_linux_function_app.finbridge.default_hostname
}
