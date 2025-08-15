# Minimal Variables for Local Docker + Azure SQL Setup
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "UK South"
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
  default     = "rg-ai-agent-dev-uks-001"
}

# Azure SQL Server Configuration (existing server with Entra ID auth)
variable "existing_azuresql_server_name" {
  description = "Name of existing Azure SQL Server"
  type        = string
  default     = null
}

variable "existing_azuresql_database_name" {
  description = "Name of existing Azure SQL Database"
  type        = string
  default     = null
}

variable "existing_azuresql_server_fqdn" {
  description = "FQDN of existing Azure SQL Server (e.g., your-server.database.windows.net)"
  type        = string
  default     = null
}

variable "use_entra_id_auth" {
  description = "Use Entra ID authentication instead of SQL authentication"
  type        = bool
  default     = true
}

# Tags for organization
variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    project     = "ai-agent-system"
    environment = "development"
    setup       = "local-docker"
    owner       = "devops-team"
    location    = "uk-south"
    managed-by  = "terraform"
  }
}
