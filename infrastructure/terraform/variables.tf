# Simplified Variables for Azure SQL Setup
variable "location" {
  description = "Azure region"
  type        = string
  default     = "UK South"
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
  default     = "rg-ai-agent-uks-001"
}

# Azure SQL Server Configuration
variable "sql_server_name" {
  description = "Name of Azure SQL Server"
  type        = string
  default     = null
}

variable "sql_database_name" {
  description = "Name of Azure SQL Database"
  type        = string
  default     = null
}

variable "sql_server_fqdn" {
  description = "FQDN of Azure SQL Server (e.g., your-server.database.windows.net)"
  type        = string
  default     = null
}

# Tags
variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    project    = "ai-agent-system"
    managed-by = "terraform"
  }
}
