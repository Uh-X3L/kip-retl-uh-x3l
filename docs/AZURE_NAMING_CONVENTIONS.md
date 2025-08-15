# Azure Naming Convention Guide

This project follows Microsoft's recommended naming conventions for Azure resources.

## Naming Convention Pattern
```
<resource-type>-<workload/application>-<environment>-<region>-<instance>
```

## Resource Type Abbreviations (Microsoft Standard)

| Resource Type | Abbreviation | Example |
|---------------|-------------|---------|
| Resource Group | `rg` | `rg-ai-agent-dev-uks-001` |
| Container Registry | `cr` | `craiagentuks001` (no hyphens, lowercase) |
| Container Apps Environment | `cae` | `cae-ai-agent-dev-uks-001` |
| Container App | `ca` | `ca-ai-agent-backend-dev-001` |
| SQL Server | `sql` | `sql-ai-agent-dev-uks-001` |
| SQL Database | `sqldb` | `sqldb-ai-agents-dev-001` |
| Application Insights | `appi` | `appi-ai-agent-dev-uks-001` |

## Region Abbreviations
- UK South: `uks`
- UK West: `ukw`
- West Europe: `we`
- North Europe: `ne`

## Environment Abbreviations
- Development: `dev`
- Staging: `stg`
- Production: `prd`

## Workload/Application Name
- Core application: `ai-agent`

## Instance Numbers
- Use 3-digit zero-padded numbers: `001`, `002`, etc.

## Special Cases

### Container Registry
- No hyphens allowed
- Lowercase alphanumeric only
- Pattern: `cr<workload><region><instance>`
- Example: `craiagentuks001`

### Tags
- Use lowercase with hyphens for consistency
- Follow kebab-case: `project`, `environment`, `managed-by`

## Complete Example Set

```terraform
# Resource Group
resource_group_name = "rg-ai-agent-dev-uks-001"

# Container Registry  
container_registry_name = "craiagentuks001"

# Container Apps
container_app_environment_name = "cae-ai-agent-dev-uks-001"
container_app_backend_name = "ca-ai-agent-backend-dev-001"

# Azure SQL
azuresql_server_name = "sql-ai-agent-dev-uks-001"
azuresql_database_name = "sqldb-ai-agents-dev-001"

# Application Insights (if enabled)
application_insights_name = "appi-ai-agent-dev-uks-001"
```

## Benefits of This Convention

1. **Consistency**: All resources follow the same pattern
2. **Clarity**: Easy to identify resource type, environment, and purpose
3. **Organization**: Resources are logically grouped and sorted
4. **Compliance**: Follows Microsoft's best practices
5. **Scalability**: Easy to add new environments or instances

## Tags Convention

```hcl
tags = {
  project     = "ai-agent-system"
  environment = "development" 
  location    = "uk-south"
  managed-by  = "terraform"
  owner       = "devops-team"
  cost-center = "development"
}
```

This naming convention ensures consistency, clarity, and compliance with Azure best practices across all resources.
