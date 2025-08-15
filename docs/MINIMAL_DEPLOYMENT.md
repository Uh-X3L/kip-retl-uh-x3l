# Minimal Azure Deployment Guide

## Cost-Effective Setup for Current AI Agent System

This minimal configuration is designed for your current system which consists of:
- Python agents (GitHub integration, optimization system)
- No web frontend/backend yet
- Minimal infrastructure needs

### Current Reality vs Full DevOps Infrastructure

**What you currently have:**
- Python agents in notebooks
- GitHub integration tools
- Local development environment
- No FastAPI backend or React frontend yet

**What the full DevOps infrastructure assumes:**
- Web applications ready for containerization
- CI/CD for application deployment
- Production-ready monitoring and scaling

### Cost-Effective Approach

The minimal configuration (`main-minimal.tf`) provides:

1. **PostgreSQL Database Only** (~$20/month)
   - Burstable tier (B_Standard_B1ms)
   - 32GB storage minimum
   - No high availability
   - No geo-redundancy

2. **Optional Container Instance** (~$10/month, disabled by default)
   - For running Python agents in cloud
   - 0.5 CPU, 1GB RAM
   - Public IP for remote access

### Deployment Options

#### Option 1: Database Only (Recommended for now)
```bash
cd infrastructure/terraform
terraform init
terraform plan -var-file="environments/development-minimal.tfvars"
terraform apply -var-file="environments/development-minimal.tfvars"
```

Cost: ~$20/month

#### Option 2: Database + Container Runner
Set `enable_container_runner = true` in tfvars file.

Cost: ~$30/month

### How Docker, Azure, and Terraform Work Together

#### Current System Architecture:
```
Local Development
├── Python Agents (test2.ipynb)
├── GitHub Tools (helpers/github_app_tools.py)
└── Local Database (optional)

→ Future: Cloud Database for agent data persistence
```

#### Terraform Role:
- **Infrastructure as Code**: Defines what Azure resources to create
- **State Management**: Tracks what exists in Azure
- **Variables**: Allows different environments (dev/prod)

#### Docker Role (for future use):
- **Containerization**: Packages your Python agents with dependencies
- **Portability**: Same container runs locally and in Azure
- **Isolation**: Each service runs in its own container

#### Azure Integration:
- **PostgreSQL**: Stores agent data, GitHub integration state
- **Container Instances**: Runs your Python agents 24/7 in cloud
- **Resource Groups**: Organizes all resources together

### What Would You Store in the Database?

For your current agent system:

```sql
-- Agent execution logs
CREATE TABLE agent_executions (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(100),
    execution_time TIMESTAMP,
    status VARCHAR(50),
    result_data JSONB
);

-- GitHub integration state
CREATE TABLE github_state (
    id SERIAL PRIMARY KEY,
    repository VARCHAR(200),
    last_sync TIMESTAMP,
    branch_info JSONB
);

-- Optimization results
CREATE TABLE optimization_results (
    id SERIAL PRIMARY KEY,
    optimization_type VARCHAR(100),
    input_parameters JSONB,
    results JSONB,
    created_at TIMESTAMP
);
```

### Next Steps

1. **For immediate use**: Deploy database only
2. **For cloud agents**: Enable container runner
3. **For full web app**: Use the complete DevOps infrastructure when you build FastAPI/React apps

### Cost Comparison

| Configuration | Monthly Cost | Use Case |
|---------------|-------------|----------|
| Database Only | ~$20 | Current agent system |
| Database + Container | ~$30 | Cloud-hosted agents |
| Full Infrastructure | ~$150+ | Production web application |

The minimal setup gives you cloud persistence for your agents without the overhead of web application infrastructure you don't need yet.
