variable "project_name" {
  description = "Stable resource-name prefix for the synthetic FinBridge candidate demo."
  type        = string
  default     = "finbridge"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.project_name))
    error_message = "project_name must start with a lowercase letter and contain only lowercase letters, digits and hyphens."
  }
}

variable "environment" {
  description = "Deployment environment label used in deterministic Azure resource names."
  type        = string
  default     = "candidate"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,12}$", var.environment))
    error_message = "environment must start with a lowercase letter and contain only lowercase letters, digits and hyphens."
  }
}

variable "location" {
  description = "Azure region for the optional cloud-mode infrastructure."
  type        = string
  default     = "westeurope"
}

variable "storage_account_name" {
  description = "Globally unique Azure Storage account name. Override for real apply if the default is unavailable."
  type        = string
  default     = "finbridgecandidate01"

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "storage_account_name must be 3-24 lowercase alphanumeric characters."
  }
}

variable "function_app_name" {
  description = "Globally unique Linux Function App name. Override for real apply if the default is unavailable."
  type        = string
  default     = "finbridge-candidate-fn"

  validation {
    condition     = length(var.function_app_name) >= 2 && length(var.function_app_name) <= 32
    error_message = "function_app_name must be between 2 and 32 characters."
  }
}

variable "tags" {
  description = "Additional Azure resource tags."
  type        = map(string)
  default     = {}
}
