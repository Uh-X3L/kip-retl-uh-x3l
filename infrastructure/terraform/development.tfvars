# Development Environment Configuration
environment = "development"
location    = "East US 2"

# Resource Names
resource_group_name              = "ai-agent-development-rg"
container_registry_name          = "aiagentdevelopmentacr"
container_app_environment_name   = "ai-agent-development-env"
container_app_backend_name       = "ai-agent-development-backend"

# Database Configuration
postgresql_server_name    = "ai-agent-development-postgresql"
postgresql_database_name  = "ai_agents_development"
postgresql_admin_username = "adminuser"

# Cache Configuration
redis_cache_name = "ai-agent-development-redis"

# Monitoring Configuration
log_analytics_name        = "ai-agent-development-logs"
application_insights_name = "ai-agent-development-insights"

# Tags
tags = {
  Environment = "development"
  Project     = "AI-Agent-System"
  ManagedBy   = "Terraform"
  Owner       = "Development-Team"
}
