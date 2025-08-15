# Staging Environment Configuration
environment = "staging"
location    = "East US 2"

# Resource Names
resource_group_name              = "ai-agent-staging-rg"
container_registry_name          = "aiagentstagingacr"
container_app_environment_name   = "ai-agent-staging-env"
container_app_backend_name       = "ai-agent-staging-backend"

# Database Configuration
postgresql_server_name    = "ai-agent-staging-postgresql"
postgresql_database_name  = "ai_agents_staging"
postgresql_admin_username = "adminuser"

# Cache Configuration
redis_cache_name = "ai-agent-staging-redis"

# Monitoring Configuration
log_analytics_name        = "ai-agent-staging-logs"
application_insights_name = "ai-agent-staging-insights"

# Tags
tags = {
  Environment = "staging"
  Project     = "AI-Agent-System"
  ManagedBy   = "Terraform"
  Owner       = "Staging-Team"
}
