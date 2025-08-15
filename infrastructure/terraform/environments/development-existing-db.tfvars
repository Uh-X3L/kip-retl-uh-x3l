# Example: Using Existing PostgreSQL Server
environment = "development"
location = "East US 2"

# Resource names (for new resources like resource group)
resource_group_name = "ai-agent-minimal-dev-rg"
postgresql_database_name = "ai_agents_dev"

# Database Mode: Use existing server
database_mode = "use_existing"

# Existing Database Configuration
# Replace these with your actual existing server details
existing_postgresql_server_id = "/subscriptions/YOUR-SUBSCRIPTION-ID/resourceGroups/YOUR-EXISTING-RG/providers/Microsoft.DBforPostgreSQL/flexibleServers/YOUR-EXISTING-SERVER"
existing_postgresql_fqdn = "your-existing-server.postgres.database.azure.com"
existing_postgresql_admin_username = "your-existing-username"
# NOTE: Set existing_postgresql_admin_password via environment variable:
# export TF_VAR_existing_postgresql_admin_password="your-existing-password"

# Cost saving: Disable container runner by default
enable_container_runner = false

# Tags for cost tracking
tags = {
  Project     = "AI-Agent-System"
  Environment = "development"
  CostTier    = "Minimal"
  Owner       = "DevOps"
  Purpose     = "Using-Existing-Database"
}
