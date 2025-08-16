# Autonomous Agent Communication System - Deployment Guide

## Overview

This guide helps you deploy and configure the autonomous agent communication system for production use. The system provides minimal viable communication protocol using Azure SQL Server as the message store.

## Prerequisites

### Required Azure Resources

1. **Azure SQL Database**
   - Service Tier: Standard S2 or higher (for production)
   - Backup: Automated daily backups enabled
   - Security: Entra ID authentication enabled

2. **Azure Key Vault** (recommended)
   - Store connection strings securely
   - Manage agent authentication secrets

3. **Azure Application Insights** (optional)
   - Monitor agent performance
   - Track message throughput

### Required Python Packages

```bash
pip install pyodbc pandas azure-identity azure-keyvault-secrets
```

## Database Setup

### 1. Create Azure SQL Database

```bash
# Using Azure CLI
az sql server create \
    --name your-server-name \
    --resource-group your-rg \
    --location eastus \
    --admin-user sqladmin \
    --admin-password YourSecurePassword123!

az sql db create \
    --resource-group your-rg \
    --server your-server-name \
    --name agent-communication \
    --service-objective S2
```

### 2. Deploy Database Schema

```bash
# Connect to your Azure SQL Database and run
sqlcmd -S your-server-name.database.windows.net -d agent-communication -U sqladmin -P YourSecurePassword123! -i schema.sql
```

### 3. Configure Firewall Rules

```bash
# Allow Azure services
az sql server firewall-rule create \
    --resource-group your-rg \
    --server your-server-name \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Allow your development machine (optional)
az sql server firewall-rule create \
    --resource-group your-rg \
    --server your-server-name \
    --name AllowDeveloperAccess \
    --start-ip-address YOUR.IP.ADDRESS \
    --end-ip-address YOUR.IP.ADDRESS
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Azure SQL Connection
AZURE_SQL_SERVER=your-server-name.database.windows.net
AZURE_SQL_DATABASE=agent-communication
AZURE_SQL_USERNAME=sqladmin
AZURE_SQL_PASSWORD=YourSecurePassword123!

# Agent Configuration
AGENT_COMMUNICATION_MODE=sql  # or 'mock' for development
AGENT_DEFAULT_TIMEOUT=300     # seconds
AGENT_MAX_RETRIES=3
AGENT_HEARTBEAT_INTERVAL=30   # seconds

# Optional: Azure Key Vault
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
AZURE_CLIENT_ID=your-app-client-id
AZURE_CLIENT_SECRET=your-app-secret
AZURE_TENANT_ID=your-tenant-id

# Optional: Application Insights
APPLICATIONINSIGHTS_CONNECTION_STRING=your-app-insights-connection-string
```

### Connection String Examples

#### SQL Server Authentication
```
Driver={ODBC Driver 17 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=agent-communication;Uid=sqladmin;Pwd=YourPassword;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
```

#### Entra ID Authentication (Recommended for Production)
```
Driver={ODBC Driver 17 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=agent-communication;Authentication=ActiveDirectoryIntegrated;Encrypt=yes;TrustServerCertificate=no;
```

## Integration with Existing Code

### 1. Update BackendSupervisorAgent

```python
# In helpers/backend_supervisor_role_tools.py
from helpers.agent_communication import SupervisorCoordinator

class BackendSupervisorAgent:
    def __init__(self):
        super().__init__()
        
        # Initialize autonomous communication
        self.agent_id = "backend-supervisor-001"
        self.coordinator = SupervisorCoordinator(self.agent_id)
        
        # Register this supervisor
        self.coordinator.agent_registry.register_agent(
            agent_id=self.agent_id,
            agent_role=AgentRole.SUPERVISOR,
            capabilities=["project_management", "code_generation", "task_delegation"],
            max_concurrent_tasks=10
        )
    
    def create_comprehensive_project(self, project_idea, requirements):
        """Enhanced with autonomous task delegation"""
        # Original implementation...
        
        # Add autonomous coordination
        task_id = self.coordinator.assign_task(
            task_type="comprehensive_project",
            description=project_idea,
            parameters={
                "requirements": requirements,
                "complexity": "high",
                "timeline": "standard"
            },
            required_capabilities=["programming", "architecture"],
            priority=MessagePriority.HIGH
        )
        
        return {
            "autonomous_task_id": task_id,
            "coordination_enabled": True,
            "expected_agents": self.coordinator.get_coordination_stats()["active_agents"]
        }
```

### 2. Create Worker Agents

```python
# Create specialized worker agents
from helpers.agent_communication import AgentRole, AgentRegistry

def create_backend_worker():
    """Create a backend development worker agent"""
    registry = AgentRegistry()
    
    agent_id = "worker-backend-001"
    registry.register_agent(
        agent_id=agent_id,
        agent_role=AgentRole.WORKER,
        capabilities=["python", "fastapi", "database", "api_development"],
        max_concurrent_tasks=3
    )
    
    return BackendWorkerAgent(agent_id, registry)

def create_frontend_worker():
    """Create a frontend development worker agent"""
    registry = AgentRegistry()
    
    agent_id = "worker-frontend-001"
    registry.register_agent(
        agent_id=agent_id,
        agent_role=AgentRole.WORKER,
        capabilities=["javascript", "react", "ui_development", "styling"],
        max_concurrent_tasks=2
    )
    
    return FrontendWorkerAgent(agent_id, registry)
```

## Monitoring and Maintenance

### Health Checks

```python
def health_check():
    """Verify system health"""
    coordinator = SupervisorCoordinator("health-check")
    
    checks = {
        "database_connection": False,
        "message_queue_operational": False,
        "agent_registry_accessible": False,
        "recent_activity": False
    }
    
    try:
        # Test database connection
        stats = coordinator.queue_manager.get_queue_stats()
        checks["database_connection"] = True
        checks["message_queue_operational"] = stats["total_messages"] >= 0
        
        # Test agent registry
        registry_stats = coordinator.agent_registry.get_registry_stats()
        checks["agent_registry_accessible"] = True
        checks["recent_activity"] = registry_stats["total_agents"] > 0
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
    
    return checks
```

### Performance Monitoring

```python
def monitor_performance():
    """Monitor system performance metrics"""
    coordinator = SupervisorCoordinator("performance-monitor")
    
    # Queue performance
    queue_stats = coordinator.queue_manager.get_queue_stats()
    
    # Agent performance
    registry_stats = coordinator.agent_registry.get_registry_stats()
    
    # Coordination performance
    coord_stats = coordinator.get_coordination_stats()
    
    metrics = {
        "message_throughput": queue_stats.get("messages_per_minute", 0),
        "agent_utilization": registry_stats.get("average_load", 0),
        "task_completion_rate": coord_stats["metrics"]["tasks_completed"] / max(coord_stats["metrics"]["tasks_assigned"], 1),
        "error_rate": coord_stats["metrics"]["tasks_failed"] / max(coord_stats["metrics"]["tasks_assigned"], 1)
    }
    
    return metrics
```

### Maintenance Tasks

```python
def daily_maintenance():
    """Perform daily maintenance tasks"""
    coordinator = SupervisorCoordinator("maintenance")
    
    # Clean up old messages and inactive agents
    results = coordinator.cleanup_and_maintenance()
    
    # Archive completed tasks older than 30 days
    # (This would require additional SQL scripts)
    
    # Update agent performance metrics
    # (Custom implementation based on your needs)
    
    return results
```

## Security Considerations

### Authentication
- Use Entra ID authentication for Azure SQL
- Implement certificate-based authentication for agents
- Rotate secrets regularly using Azure Key Vault

### Authorization
- Implement role-based access for different agent types
- Restrict agent communication to authorized channels
- Monitor and audit all agent activities

### Data Protection
- Encrypt sensitive task parameters
- Implement data retention policies
- Use private endpoints for Azure SQL access

## Troubleshooting

### Common Issues

1. **Connection Timeouts**
   - Increase connection timeout in connection string
   - Check firewall rules
   - Verify network connectivity

2. **Agent Registration Failures**
   - Check database permissions
   - Verify agent_registry table exists
   - Review agent capability format

3. **Message Delivery Issues**
   - Check message queue table constraints
   - Verify JSON message format
   - Review database transaction logs

4. **Performance Issues**
   - Monitor database resource utilization
   - Check query execution plans
   - Consider scaling database tier

### Debugging Commands

```bash
# Check database connectivity
python -c "from helpers.agent_communication import MessageQueueManager; print(MessageQueueManager().get_queue_stats())"

# Verify agent registration
python -c "from helpers.agent_communication import AgentRegistry; print(AgentRegistry().get_registry_stats())"

# Test message sending
python -c "
from helpers.agent_communication import AgentMessage, MessageType
from helpers.agent_communication import MessageQueueManager
queue = MessageQueueManager()
msg = AgentMessage('test-001', 'sender', 'receiver', MessageType.HEARTBEAT, {})
print(queue.send_message(msg))
"
```

## Deployment Checklist

- [ ] Azure SQL Database created and configured
- [ ] Database schema deployed (schema.sql)
- [ ] Firewall rules configured
- [ ] Environment variables set
- [ ] Connection string tested
- [ ] Agent registration verified
- [ ] Message queue operational
- [ ] Health checks implemented
- [ ] Monitoring configured
- [ ] Security measures in place
- [ ] Backup strategy established

## Next Steps

1. **Deploy to Development Environment**
   - Test with mock mode first
   - Gradually migrate to SQL mode
   - Verify all functionality

2. **Production Deployment**
   - Use infrastructure as code (Terraform/Bicep)
   - Implement CI/CD pipeline
   - Set up monitoring and alerting

3. **Scale and Optimize**
   - Monitor performance metrics
   - Scale database as needed
   - Optimize agent assignment algorithms

4. **Extend Functionality**
   - Add custom message types
   - Implement specialized agents
   - Create domain-specific workflows

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Azure SQL Database documentation
3. Examine application logs in `agent_communication_demo.log`
4. Test with the provided demo script (`demo.py`)

---

*This deployment guide is part of the Autonomous Agent Communication System (GitHub Issue #92)*
