# Resource Group Validation

## Single Resource Group Strategy

This Terraform configuration creates exactly **ONE** resource group that contains all resources:

```
📦 rg-ai-agent-dev-uks-001
├── 🗃️ Container Registry: craiagentuks001
├── 📦 Container Apps Environment: cae-ai-agent-dev-uks-001
├── 🐳 Container App: ca-ai-agent-backend-dev-001 (optional)
├── 📊 Application Insights: appi-ai-agent-dev-uks-001 (optional)
└── 🔗 References to your existing Azure SQL Server (external)
```

## What Gets Created vs External

### ✅ Created in YOUR Resource Group:
- Resource Group: `rg-ai-agent-dev-uks-001`
- Container Registry (if using full DevOps)
- Container Apps Environment (if using full DevOps)
- Container Apps (if using full DevOps)
- Application Insights (optional)

### 🔗 External Resources (Your Existing):
- Azure SQL Server (in different resource group)
- Azure SQL Database (in your existing server)

## Terraform Resource Count

```bash
# Check what will be created
terraform plan -var-file="environments/development-local-docker.tfvars"

# Should show approximately:
# Plan: 1 to add, 0 to change, 0 to destroy
# (Just the resource group since you're using existing Azure SQL)
```

## Verification Commands

```bash
# After deployment, verify single resource group
az group list --query "[?name=='rg-ai-agent-dev-uks-001']" --output table

# List resources in the group
az resource list --resource-group "rg-ai-agent-dev-uks-001" --output table

# Should show minimal resources since using existing database
```

## Cost Impact

- **Your setup**: ~£0-5/month (just resource group + optional monitoring)
- **Full setup**: ~£50-150/month (includes new database + container apps)

Your configuration minimizes costs by:
1. Using existing Azure SQL Server
2. Running containers locally
3. Creating minimal Azure infrastructure
4. Single resource group for organization

This approach gives you infrastructure-as-code benefits without the costs of duplicate resources.
