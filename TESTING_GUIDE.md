# 🧪 Testing Guide for Issue #70 DevOps Implementation

## 🎯 Overview
This guide helps you test the complete Docker + Azure + Terraform integration step by step.

## Prerequisites
- Docker Desktop installed and running
- Azure CLI installed (`az --version`)
- Terraform installed (`terraform --version`)
- Azure subscription with Contributor access

## 🐳 **Phase 1: Test Docker Layer (Local)**

### 1.1 Test Docker Build
```bash
# Build the application image
docker build -f docker/Dockerfile -t ai-agent-system:test .

# Verify image was created
docker images | grep ai-agent-system
```

### 1.2 Test Local Development Environment
```bash
# Start all services locally
docker-compose -f docker/docker-compose.yml up -d

# Check services are running
docker-compose ps

# Test endpoints
curl http://localhost:8000/health      # Backend health check
curl http://localhost:3000             # Frontend (if available)

# Check logs
docker-compose logs ai-agent-backend

# Cleanup
docker-compose down
```

### 1.3 Test Production Docker Configuration
```bash
# Test production compose (without external dependencies)
docker-compose -f docker/docker-compose.prod.yml config

# This validates the syntax without running
```

## 🏗️ **Phase 2: Test Terraform Layer (Infrastructure)**

### 2.1 Validate Terraform Configuration
```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Validate syntax and configuration
terraform validate

# Check formatting
terraform fmt -check

# Plan infrastructure (dry run)
terraform plan -var-file="development.tfvars"
```

### 2.2 Test Azure Authentication
```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Verify access
az account show
```

### 2.3 Deploy Development Infrastructure
```bash
# Deploy to development environment
terraform apply -var-file="development.tfvars"

# Verify resources were created
az resource list --resource-group ai-agent-dev-rg --output table

# Get infrastructure outputs
terraform output
```

## ☁️ **Phase 3: Test Azure Integration (End-to-End)**

### 3.1 Test Container Registry
```bash
# Get registry login server from Terraform output
REGISTRY=$(terraform output -raw container_registry_login_server)

# Login to Azure Container Registry
az acr login --name ${REGISTRY}

# Build and push image
docker build -f ../../docker/Dockerfile -t ${REGISTRY}/ai-agent-system:latest ../..
docker push ${REGISTRY}/ai-agent-system:latest

# Verify image in registry
az acr repository list --name ${REGISTRY%%.azurecr.io}
```

### 3.2 Test Container App Deployment
```bash
# Get container app info
az containerapp show \
  --name ai-agent-dev-backend \
  --resource-group ai-agent-dev-rg \
  --query "properties.configuration.ingress.fqdn" -o tsv

# Update container app with new image
az containerapp update \
  --name ai-agent-dev-backend \
  --resource-group ai-agent-dev-rg \
  --image ${REGISTRY}/ai-agent-system:latest

# Test the deployed application
APP_URL=$(az containerapp show \
  --name ai-agent-dev-backend \
  --resource-group ai-agent-dev-rg \
  --query "properties.configuration.ingress.fqdn" -o tsv)

curl https://${APP_URL}/health
```

### 3.3 Test Database Connectivity
```bash
# Get database connection info from Terraform
DB_HOST=$(terraform output -raw postgresql_server_fqdn)
DB_NAME=$(terraform output -raw postgresql_database_name)

# Test connection (requires psql client)
psql "postgresql://adminuser:your-password@${DB_HOST}:5432/${DB_NAME}" -c "SELECT version();"
```

## 🔄 **Phase 4: Test CI/CD Pipeline**

### 4.1 Test GitHub Actions Workflows
```bash
# Push changes to trigger CI
git add .
git commit -m "test: trigger CI pipeline"
git push origin feature/issue-70-devops-setup

# Monitor workflow in GitHub Actions tab
# https://github.com/Uh-X3L/kip-retl-uh-x3l/actions
```

### 4.2 Manual Workflow Testing
```bash
# Test CI workflow locally (if using act)
act -j test

# Or test individual components
docker run --rm -v $(pwd):/workspace -w /workspace python:3.10-slim bash -c "
  pip install -r src/backend/requirements.txt
  python -m pytest tests/
"
```

## 📊 **Phase 5: Test Monitoring and Observability**

### 5.1 Test Application Insights
```bash
# Get Application Insights info
INSIGHTS_KEY=$(terraform output -raw application_insights_instrumentation_key)

# View metrics in Azure portal
az monitor app-insights query \
  --app ${INSIGHTS_KEY} \
  --analytics-query "requests | limit 10"
```

### 5.2 Test Log Analytics
```bash
# Query container logs
az monitor log-analytics query \
  --workspace $(terraform output -raw log_analytics_workspace_id) \
  --analytics-query "ContainerAppConsoleLogs_CL | limit 100"
```

## 🛠️ **Phase 6: Test Multi-Environment Setup**

### 6.1 Test Staging Environment
```bash
# Deploy staging infrastructure
terraform apply -var-file="staging.tfvars"

# Deploy application to staging
# (Similar process as development but with staging resources)
```

### 6.2 Test Production Environment
```bash
# Plan production deployment (review carefully)
terraform plan -var-file="production.tfvars"

# Deploy to production (when ready)
terraform apply -var-file="production.tfvars"
```

## 🔧 **Troubleshooting Common Issues**

### Docker Issues
```bash
# If build fails
docker build --no-cache -f docker/Dockerfile .

# If containers won't start
docker-compose logs
docker system prune  # Clean up space

# If port conflicts
docker-compose down && docker-compose up -d
```

### Terraform Issues
```bash
# If state is corrupted
terraform refresh

# If resources already exist
terraform import <resource_type>.<name> <azure_resource_id>

# If planning fails
terraform validate
terraform fmt
```

### Azure Issues
```bash
# If authentication fails
az login --tenant your-tenant-id

# If resources not found
az account show
az resource list --output table

# If container app fails
az containerapp logs show --name ai-agent-dev-backend --resource-group ai-agent-dev-rg
```

## ✅ **Validation Checklist**

- [ ] Docker image builds successfully
- [ ] Local development environment starts
- [ ] Terraform plan validates without errors
- [ ] Azure resources are created correctly
- [ ] Container image pushes to Azure Container Registry
- [ ] Application deploys to Azure Container Apps
- [ ] Health endpoints respond correctly
- [ ] Database connection works
- [ ] Monitoring and logs are collected
- [ ] CI/CD pipeline runs successfully

## 🎯 **Success Criteria**

Your implementation is working correctly when:

1. **Local Development**: `docker-compose up` starts all services
2. **Infrastructure**: `terraform apply` creates Azure resources
3. **Deployment**: Application runs on Azure Container Apps
4. **Monitoring**: Logs and metrics appear in Azure Monitor
5. **CI/CD**: GitHub Actions deploy automatically on push

## 📞 **Getting Help**

If you encounter issues:
1. Check the specific error messages
2. Review the troubleshooting section above
3. Verify Azure permissions and quotas
4. Check Docker and Terraform versions
5. Review the generated documentation in `/docs`

---

*This testing guide ensures your Issue #70 DevOps implementation works correctly across all environments.*
