# Database Configuration Guide

## 🎯 Three Database Modes Available

### 1. **Create New Database** (`create_new`)
- Always creates a fresh PostgreSQL server
- Use when you want a dedicated database for this project
- Cost: ~$20/month

### 2. **Use Existing Database** (`use_existing`)
- Points to your existing PostgreSQL server
- Only creates the database/schema within existing server
- Cost: ~$0/month (no additional server costs)

### 3. **Create If Not Exists** (`create_if_not_exists`) - Default
- Checks if server exists, creates if it doesn't
- Best for development - creates when needed, reuses if available
- Cost: ~$20/month (only if creating new)

## 🔧 Configuration Examples

### Option A: Use Your Existing Database
```hcl
# In development-existing-db.tfvars
database_mode = "use_existing"
existing_postgresql_server_id = "/subscriptions/YOUR-SUB-ID/resourceGroups/YOUR-RG/providers/Microsoft.DBforPostgreSQL/flexibleServers/YOUR-SERVER"
existing_postgresql_fqdn = "your-server.postgres.database.azure.com"
existing_postgresql_admin_username = "your-username"
```

### Option B: Create New Database (Clean Slate)
```hcl
# In development-minimal.tfvars
database_mode = "create_new"
postgresql_server_name = "ai-agent-new-db"
postgresql_admin_username = "adminuser"
```

### Option C: Smart Create (Recommended)
```hcl
# In development-minimal.tfvars
database_mode = "create_if_not_exists"  # Default
postgresql_server_name = "ai-agent-minimal-db-dev"
```

## 🚀 Deployment Commands

### Deploy with Existing Database:
```bash
cd infrastructure/terraform

# Set password for existing DB
export TF_VAR_existing_postgresql_admin_password="your-existing-password"

# Deploy
terraform init
terraform plan -var-file="environments/development-existing-db.tfvars"
terraform apply -var-file="environments/development-existing-db.tfvars"
```

### Deploy with New Database:
```bash
cd infrastructure/terraform

# Set password for new DB
export TF_VAR_postgresql_admin_password="your-new-secure-password"

# Deploy
terraform init
terraform plan -var-file="environments/development-minimal.tfvars"
terraform apply -var-file="environments/development-minimal.tfvars"
```

## 🔍 Find Your Existing Database Info

If you want to use an existing database, find these details:

```bash
# List your PostgreSQL servers
az postgres flexible-server list --output table

# Get specific server details
az postgres flexible-server show \
  --name "your-server-name" \
  --resource-group "your-rg-name" \
  --query "{id:id, fqdn:fullyQualifiedDomainName, adminLogin:administratorLogin}"
```

## 💡 What Happens in Each Mode

### Use Existing (`use_existing`):
1. ✅ References your existing PostgreSQL server
2. ✅ Creates only the `ai_agents_dev` database within it
3. ✅ No additional server costs
4. ✅ Can coexist with other databases on same server

### Create New (`create_new`):
1. ✅ Creates new PostgreSQL server
2. ✅ Creates the `ai_agents_dev` database
3. ✅ Full control over server configuration
4. 💰 Additional ~$20/month cost

### Create If Not Exists (`create_if_not_exists`):
1. 🔍 Checks if server exists
2. ✅ Creates server if missing
3. ✅ Uses existing server if found
4. ✅ Always creates the database
5. 💰 Cost varies based on whether server exists

## 🎯 Recommended Approach

**For your AI agent system:**

1. **If you have an existing PostgreSQL server**: Use `use_existing` mode
2. **If this is your first deployment**: Use `create_if_not_exists` mode
3. **If you want complete isolation**: Use `create_new` mode

The system will handle database creation gracefully in all modes!
