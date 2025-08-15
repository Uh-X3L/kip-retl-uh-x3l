# Minimal Development Environment Configuration
environment = "development"
location = "East US 2"  # Usually cheapest region

# Resource names
resource_group_name = "ai-agent-minimal-dev-rg"
postgresql_server_name = "ai-agent-minimal-db-dev"
postgresql_database_name = "ai_agents_dev"

# Database Mode Options:
# - "create_new": Always create a new PostgreSQL server
# - "use_existing": Use an existing PostgreSQL server (requires existing_* variables)
# - "create_if_not_exists": Create server if it doesn't exist, use if it does
database_mode = "create_if_not_exists"

# Database configuration (for new servers)
postgresql_admin_username = "adminuser"
# NOTE: Set postgresql_admin_password via environment variable:
# export TF_VAR_postgresql_admin_password="your-secure-password"

# Existing Database Configuration (uncomment and fill if using existing)
# database_mode = "use_existing"
# existing_postgresql_server_id = "/subscriptions/YOUR-SUB-ID/resourceGroups/YOUR-RG/providers/Microsoft.DBforPostgreSQL/flexibleServers/YOUR-SERVER"
# existing_postgresql_fqdn = "your-existing-server.postgres.database.azure.com"
# existing_postgresql_admin_username = "your-existing-username"
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
  Purpose     = "Cost-Effective-Development"
}
