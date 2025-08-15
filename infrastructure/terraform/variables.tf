# General Variables
variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "development"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US 2"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "ai-agent-rg"
}

# Container Registry
variable "container_registry_name" {
  description = "Name of the Azure Container Registry"
  type        = string
  default     = "aiagentacr"
}

# Container Apps
variable "container_app_environment_name" {
  description = "Name of the Container Apps Environment"
  type        = string
  default     = "ai-agent-env"
}

variable "container_app_backend_name" {
  description = "Name of the backend container app"
  type        = string
  default     = "ai-agent-backend"
}

# Database
variable "postgresql_server_name" {
  description = "Name of the PostgreSQL server"
  type        = string
  default     = "ai-agent-postgresql"
}

variable "postgresql_database_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "ai_agents"
}

variable "postgresql_admin_username" {
  description = "Administrator username for PostgreSQL"
  type        = string
  default     = "adminuser"
}

variable "postgresql_admin_password" {
  description = "Administrator password for PostgreSQL"
  type        = string
  sensitive   = true
  default     = null
}

# Redis Cache
variable "redis_cache_name" {
  description = "Name of the Redis cache"
  type        = string
  default     = "ai-agent-redis"
}

# Monitoring
variable "log_analytics_name" {
  description = "Name of the Log Analytics workspace"
  type        = string
  default     = "ai-agent-logs"
}

variable "application_insights_name" {
  description = "Name of the Application Insights instance"
  type        = string
  default     = "ai-agent-insights"
}

# Tags
variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "AI-Agent-System"
    Environment = "development"
    ManagedBy   = "Terraform"
    Owner       = "DevOps-Team"
  }
}
