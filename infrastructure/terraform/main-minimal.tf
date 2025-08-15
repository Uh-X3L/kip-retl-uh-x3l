# Minimal Azure Infrastructure for Local Docker + Azure SQL Setup
# This configuration provides minimal Azure organization resources
# while using existing Azure SQL Server with Entra ID authentication

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.80"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group (for organization only)
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  
  tags = var.tags
}

# Outputs for connection information
output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Resource group location"
  value       = azurerm_resource_group.main.location
}

output "azuresql_connection_info" {
  description = "Azure SQL connection information"
  value = {
    server_fqdn   = var.sql_server_fqdn
    database_name = var.sql_database_name
    auth_method   = "Entra ID"
    connection_string = "Server=${var.sql_server_fqdn};Database=${var.sql_database_name};Authentication=Active Directory Default;Encrypt=True;"
  }
  sensitive = false
}

output "development_setup_summary" {
  description = "Summary of your development setup"
  value = {
    architecture = "Local Docker containers + Azure SQL Server"
    containers = "Running locally on your PC"
    database = "Azure SQL Server with Entra ID authentication"
    infrastructure = "Minimal - single resource group for organization"
    monthly_cost = "~£0 (using existing resources only)"
    next_steps = [
      "Configure your local Docker containers to connect to Azure SQL",
      "Use 'terraform output azuresql_connection_info' for connection details",
      "Ensure your Entra ID has proper permissions on the Azure SQL Server"
    ]
  }
}

# Outputs

