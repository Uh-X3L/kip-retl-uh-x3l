# Development Configuration for Local Docker + Azure SQL
environment = "development"
location = "UK South"

# Resource names (minimal - just for organization)
resource_group_name = "rg-ai-agent-dev-uks-001"

# Database Mode: Use existing Azure SQL Server
database_mode = "use_existing_azuresql"

# Your existing Azure SQL Server configuration
# Replace these with your actual Azure SQL Server details
existing_azuresql_server_name = "your-sql-server-name"
existing_azuresql_server_fqdn = "your-sql-server.database.windows.net"
existing_azuresql_database_name = "your-database-name"
existing_azuresql_admin_username = "your-admin-username"
# NOTE: Set password via environment variable for security:
# export TF_VAR_existing_azuresql_admin_password="your-password"

# Container runner: Disabled (running locally via Docker)
enable_container_runner = false

# Tags for organization
tags = {
  project     = "ai-agent-system"
  environment = "development"
  setup       = "local-docker-azure-sql"
  owner       = "devops-team"
  purpose     = "development-with-existing-database"
  location    = "uk-south"
  managed-by  = "terraform"
}
