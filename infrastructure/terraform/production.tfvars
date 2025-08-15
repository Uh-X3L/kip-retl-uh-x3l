# Production Environment Configuration
environment = "production"
location    = "East US 2"

# Resource Names
resource_group_name              = "ai-agent-production-rg"
container_registry_name          = "aiagentproductionacr"
container_app_environment_name   = "ai-agent-production-env"
container_app_backend_name       = "ai-agent-production-backend"

# Database Configuration
postgresql_server_name    = "ai-agent-production-postgresql"
postgresql_database_name  = "ai_agents_production"
postgresql_admin_username = "adminuser"

# Cache Configuration
redis_cache_name = "ai-agent-production-redis"

# Monitoring Configuration
log_analytics_name        = "ai-agent-production-logs"
application_insights_name = "ai-agent-production-insights"

# Tags
tags = {
  Environment = "production"
  Project     = "AI-Agent-System"
  ManagedBy   = "Terraform"
  Owner       = "Production-Team"
}
