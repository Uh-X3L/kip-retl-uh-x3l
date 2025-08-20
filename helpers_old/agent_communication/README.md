# Agent Communication System

![Redis](https://img.shields.io/badge/redis-streams-red.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

> **Minimal Redis-based messaging for autonomous agents**

Simple, fast agent communication using Redis Streams with optional file logging.

## Quick Start

```bash
# Start Redis
docker run -d --name redis-agent-queue -p 6379:6379 redis:7-alpine

# Run demo
python demo.py
```

## Architecture

```
Agent A ──┐
          ├──→ Redis Streams ←──┐
Agent B ──┘                    ├── Agent C
                               └── Agent D
```

## Core Components

- **`MessageQueueManager`** - Send/receive messages via Redis Streams
- **`AgentMessage`** - Message protocol (JSON-based)
- **`AgentRegistry`** - In-memory agent discovery
- **File Logging** - Optional audit trails (disabled by default)

## Basic Usage

```python
from queue_manager import MessageQueueManager
from message_protocol import AgentMessage, MessageType

# Initialize
queue = MessageQueueManager()

# Send message
message = AgentMessage(
    from_agent="agent_001",
    to_agent="agent_002", 
    message_type=MessageType.TASK_ASSIGNMENT,
    content={"task": "process_data"}
)
queue.send_message(message)

# Receive messages
messages = queue.get_messages("agent_002")
for msg in messages:
    print(f"From: {msg.from_agent}, Content: {msg.content}")
    queue.mark_processed(msg.message_id, "agent_002")
```

## Optional File Logging

```python
from file_logger import enable_file_logging

# Enable for audit trails (disabled by default)
enable_file_logging("./logs")

# Creates daily JSON files:
# - agent_activity_YYYY-MM-DD.jsonl
# - message_audit_YYYY-MM-DD.jsonl  
# - task_history_YYYY-MM-DD.jsonl
```

## Message Types

- `TASK_ASSIGNMENT` - Assign work to agents
- `TASK_RESPONSE` - Task completion results
- `STATUS_UPDATE` - Agent status changes
- `HEARTBEAT` - Keep-alive signals
- `ERROR_REPORT` - Error notifications

## Requirements

- Python 3.8+
- Redis 7+ (optional - has mock mode)
- `redis` package for Python

That's it! Simple messaging for autonomous agents.
    max_concurrent_tasks=3
)

# Assign a task
task_id = coordinator.assign_task(
    task_type="api_development",
    description="Create user authentication API",
    parameters={"framework": "fastapi", "auth": "jwt"},
    required_capabilities=["python", "api_development"],
    priority=MessagePriority.HIGH
)

print(f"Task assigned: {task_id}")
```

## 📖 Documentation

### Core Components

#### 1. Message Protocol (`message_protocol.py`)
- **`AgentMessage`** - Core message structure with JSON serialization
- **`MessageType`** - Enum defining message categories
- **`TaskRequest`/`TaskResponse`** - Structured task communication
- **Helper Functions** - Message creation utilities

#### 2. Queue Manager (`queue_manager.py`)
- **`MessageQueueManager`** - Message sending, receiving, and processing
- **SQL Backend** - Azure SQL Server integration
- **Mock Backend** - In-memory queue for development
- **Priority Handling** - Message ordering by priority

#### 3. Agent Registry (`agent_registry.py`)
- **`AgentRegistry`** - Agent registration and discovery
- **`AgentInfo`** - Agent metadata and capabilities
- **Capability Matching** - Find agents by required skills
- **Load Balancing** - Intelligent agent selection

#### 4. Supervisor Coordinator (`supervisor_coordinator.py`)
- **`SupervisorCoordinator`** - Main orchestration layer
- **Task Assignment** - Automated delegation to best agents
- **Message Processing** - Handle responses and status updates
- **Coordination Stats** - System monitoring and metrics

### Message Types

| Type | Purpose | Content |
|------|---------|---------|
| `TASK_REQUEST` | Assign work to agents | Task details, parameters, capabilities |
| `TASK_RESPONSE` | Report task completion | Status, results, execution time |
| `STATUS_UPDATE` | Agent state changes | Current status, availability |
| `HEARTBEAT` | Keep-alive signal | Timestamp, health metrics |
| `ERROR_REPORT` | Report failures | Error details, stack trace |
| `COORDINATION` | Multi-agent sync | Coordination instructions |

## 🔧 Configuration

### Environment Variables

```bash
# Database Connection
AZURE_SQL_SERVER=your-server.database.windows.net
AZURE_SQL_DATABASE=agent-communication
AZURE_SQL_USERNAME=sqladmin
AZURE_SQL_PASSWORD=YourPassword123!

# Agent Settings
AGENT_COMMUNICATION_MODE=sql  # 'sql' or 'mock'
AGENT_DEFAULT_TIMEOUT=300     # seconds
AGENT_MAX_RETRIES=3
AGENT_HEARTBEAT_INTERVAL=30   # seconds

# Optional: Azure Key Vault
AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/
AZURE_CLIENT_ID=your-app-id
AZURE_CLIENT_SECRET=your-secret
AZURE_TENANT_ID=your-tenant-id
```

### Connection Strings

#### SQL Server Authentication
```
Driver={ODBC Driver 17 for SQL Server};Server=tcp:server.database.windows.net,1433;Database=agent-communication;Uid=admin;Pwd=password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
```

#### Entra ID Authentication (Recommended)
```
Driver={ODBC Driver 17 for SQL Server};Server=tcp:server.database.windows.net,1433;Database=agent-communication;Authentication=ActiveDirectoryIntegrated;Encrypt=yes;TrustServerCertificate=no;
```

## 🧪 Testing

### Run Unit Tests
```bash
# Run all tests
python -m pytest test_agent_communication.py -v

# Run specific test categories
python -m pytest test_agent_communication.py::TestMessageProtocol -v
python -m pytest test_agent_communication.py::TestSupervisorCoordinator -v
```

### Run Demo
```bash
# Interactive demonstration
python demo.py
```

### Test Coverage
- ✅ Message serialization and deserialization
- ✅ Queue operations (send, receive, process)
- ✅ Agent registration and discovery
- ✅ Task assignment and coordination
- ✅ Error handling and recovery
- ✅ End-to-end workflows

## 📊 Monitoring

### Health Checks
```python
def health_check():
    coordinator = SupervisorCoordinator("health-monitor")
    
    return {
        "database_connected": coordinator.queue_manager.is_connected(),
        "agents_registered": coordinator.agent_registry.get_registry_stats()["total_agents"],
        "queue_operational": len(coordinator.queue_manager.get_queue_stats()) > 0
    }
```

### Performance Metrics
```python
def get_performance_metrics():
    coordinator = SupervisorCoordinator("metrics")
    
    return {
        "message_throughput": coordinator.queue_manager.get_queue_stats()["messages_per_minute"],
        "agent_utilization": coordinator.agent_registry.get_registry_stats()["average_load"],
        "task_completion_rate": coordinator.get_coordination_stats()["completion_rate"]
    }
```

## 🔐 Security

### Authentication
- **Entra ID Integration** - Azure Active Directory authentication
- **Certificate-based Auth** - PKI for agent verification
- **Role-based Access** - Granular permissions per agent type

### Data Protection
- **Encryption at Rest** - Azure SQL transparent data encryption
- **Encryption in Transit** - TLS 1.2+ for all connections
- **Secret Management** - Azure Key Vault integration

### Network Security
- **Private Endpoints** - VNet isolation for Azure SQL
- **Firewall Rules** - Restricted database access
- **Network Security Groups** - Traffic filtering

## 🚀 Deployment

### Development
```bash
# Use mock mode for local development
export AGENT_COMMUNICATION_MODE=mock
python demo.py
```

### Production
1. **Deploy Azure SQL Database**
2. **Apply Database Schema** (`schema.sql`)
3. **Configure Environment Variables**
4. **Setup Monitoring and Alerting**
5. **Deploy Agent Applications**

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 🔧 Integration Examples

### Backend Supervisor Agent
```python
from helpers.agent_communication import SupervisorCoordinator

class BackendSupervisorAgent:
    def __init__(self):
        self.coordinator = SupervisorCoordinator("backend-supervisor-001")
        
        # Register this supervisor
        self.coordinator.agent_registry.register_agent(
            agent_id="backend-supervisor-001",
            agent_role=AgentRole.SUPERVISOR,
            capabilities=["project_management", "coordination"],
            max_concurrent_tasks=20
        )
    
    def create_comprehensive_project(self, project_idea, requirements):
        # Assign development tasks to specialized agents
        tasks = []
        
        # Backend development
        if "api" in requirements:
            task_id = self.coordinator.assign_task(
                task_type="api_development",
                description=f"Develop API for {project_idea}",
                parameters={"requirements": requirements},
                required_capabilities=["python", "api_development"]
            )
            tasks.append(task_id)
        
        # Frontend development
        if "ui" in requirements:
            task_id = self.coordinator.assign_task(
                task_type="ui_development", 
                description=f"Create UI for {project_idea}",
                parameters={"requirements": requirements},
                required_capabilities=["javascript", "react"]
            )
            tasks.append(task_id)
        
        return {"autonomous_tasks": tasks, "coordination_enabled": True}
```

### Specialized Worker Agent
```python
class PythonWorkerAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.registry = AgentRegistry()
        self.queue = MessageQueueManager()
        
        # Register capabilities
        self.registry.register_agent(
            agent_id=agent_id,
            agent_role=AgentRole.WORKER,
            capabilities=["python", "fastapi", "postgresql", "testing"],
            max_concurrent_tasks=3
        )
    
    def start_listening(self):
        """Start processing tasks from the queue"""
        while True:
            messages = self.queue.get_messages(self.agent_id, limit=5)
            
            for message in messages:
                if message.message_type == MessageType.TASK_REQUEST:
                    self.process_task(message)
                    self.queue.mark_processed(message.message_id, self.agent_id)
            
            time.sleep(10)  # Poll every 10 seconds
    
    def process_task(self, message):
        """Process an assigned task"""
        task_data = message.content
        
        try:
            # Execute the task based on type
            result = self.execute_task(task_data)
            
            # Send completion response
            response = AgentMessage(
                message_id=f"response-{message.message_id}",
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                message_type=MessageType.TASK_RESPONSE,
                content={
                    "task_id": task_data.get("task_id"),
                    "status": "completed",
                    "result": result,
                    "completion_percentage": 100
                }
            )
            self.queue.send_message(response)
            
        except Exception as e:
            # Send error response
            error_response = AgentMessage(
                message_id=f"error-{message.message_id}",
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                message_type=MessageType.ERROR_REPORT,
                content={
                    "task_id": task_data.get("task_id"),
                    "error_type": "task_execution_failure",
                    "error_message": str(e)
                }
            )
            self.queue.send_message(error_response)
```

## 📋 API Reference

### Core Classes

#### `AgentMessage`
```python
class AgentMessage:
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: Dict[str, Any]
    priority: MessagePriority = MessagePriority.MEDIUM
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_json(self) -> str
    @classmethod
    def from_json(cls, json_data: str) -> 'AgentMessage'
```

#### `MessageQueueManager`
```python
class MessageQueueManager:
    def __init__(self, connection_string: str = None, use_mock: bool = False)
    def send_message(self, message: AgentMessage) -> bool
    def get_messages(self, agent_id: str, limit: int = 10) -> List[AgentMessage]
    def mark_processed(self, message_id: str, agent_id: str) -> bool
    def get_queue_stats(self) -> Dict[str, Any]
```

## 📁 Optional File Logging

The system includes optional file-based logging for audit trails, performance metrics, and compliance requirements. All data is stored as JSON Lines files organized by date.

### Enable File Logging
```python
from helpers.agent_communication.file_logger import enable_file_logging

# Enable file logging with custom directory
file_logger = enable_file_logging(base_dir="./logs")

# File logging is now active - all agent activities will be logged
```

### File Structure
```
logs/
├── 2024-01-15/
│   ├── agent_activity_2024-01-15.jsonl      # Agent registrations, status changes
│   ├── message_audit_2024-01-15.jsonl       # Message send/receive/process events
│   ├── task_history_2024-01-15.jsonl        # Task assignments and completions
│   ├── performance_2024-01-15.jsonl         # Performance metrics and timings
│   └── errors_2024-01-15.jsonl              # Error tracking and diagnostics
├── 2024-01-16/
│   └── ...
└── 2024-01-17/
    └── ...
```

### Log Entry Examples
```json
// agent_activity_2024-01-15.jsonl
{"agent_id": "agent_001", "event": "registered", "data": {"agent_role": "coordinator", "capabilities": ["planning"]}, "timestamp": "2024-01-15T10:30:00Z"}

// message_audit_2024-01-15.jsonl
{"message_id": "msg_123", "from_agent": "agent_001", "to_agent": "agent_002", "message_type": "task_assignment", "event": "sent", "timestamp": "2024-01-15T10:31:00Z"}

// task_history_2024-01-15.jsonl
{"task_id": "task_456", "agent_id": "agent_002", "event": "completed", "data": {"duration_ms": 1250, "success": true}, "timestamp": "2024-01-15T10:32:15Z"}
```

### File Logging API
```python
from helpers.agent_communication.file_logger import get_file_logger

# Get logger instance
logger = get_file_logger()

# Manual logging (automatic logging is handled by MessageQueueManager)
logger.log_agent_activity("agent_001", "status_change", {"new_status": "busy"})
logger.log_performance_metric("agent_001", "response_time", 125.5, "ms")
logger.log_error("agent_001", "connection_error", "Redis connection failed")

# Get logging statistics
stats = logger.get_log_stats()
print(f"Log files: {stats['log_files']}")

# Clean up old logs (optional)
logger.cleanup_old_logs(days_to_keep=30)
```

### Benefits of File Logging
- **Audit Trails**: Complete record of all agent activities and communications
- **Performance Analysis**: Detailed metrics for system optimization
- **Compliance**: Structured logs for regulatory requirements
- **Debugging**: Historical data for troubleshooting and error analysis
- **Analytics**: JSON Lines format for easy data processing and visualization

**Note**: File logging is optional and disabled by default for performance. Enable only when audit trails or compliance logging is required.

#### `AgentRegistry`
```python
class AgentRegistry:
    def __init__(self, connection_string: str = None, use_mock: bool = False)
    def register_agent(self, agent_id: str, agent_role: AgentRole, 
                      capabilities: List[str], max_concurrent_tasks: int = 1) -> bool
    def find_available_agents(self, required_capabilities: List[str], 
                             max_results: int = 10) -> List[AgentInfo]
    def find_best_agent(self, required_capabilities: List[str]) -> Optional[AgentInfo]
    def update_heartbeat(self, agent_id: str, status: str = 'active', 
                        current_tasks: int = None) -> bool
```

#### `SupervisorCoordinator`
```python
class SupervisorCoordinator:
    def __init__(self, supervisor_id: str, connection_string: str = None, use_mock: bool = False)
    def assign_task(self, task_type: str, description: str, parameters: Dict[str, Any],
                   required_capabilities: List[str], priority: MessagePriority = MessagePriority.MEDIUM) -> Optional[str]
    def process_incoming_messages(self) -> int
    def get_coordination_stats(self) -> Dict[str, Any]
    def broadcast_message(self, message_type: MessageType, content: Dict[str, Any],
                         priority: MessagePriority = MessagePriority.MEDIUM) -> bool
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/autonomous-agent-communication.git
cd autonomous-agent-communication

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest test_agent_communication.py -v

# Run demo
python demo.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for GitHub Issue #92 - Autonomous Agent Communication and Coordination System
- Uses Azure SQL Server for enterprise-grade message persistence
- Designed for integration with existing BackendSupervisorAgent framework
- Inspired by distributed systems and actor model patterns

## 📞 Support

For questions, issues, or feature requests:

1. **Documentation** - Check this README and [DEPLOYMENT.md](DEPLOYMENT.md)
2. **Testing** - Run `python demo.py` for interactive demonstration
3. **Troubleshooting** - Review logs in `agent_communication_demo.log`
4. **Issues** - Open a GitHub issue with detailed reproduction steps

---

**🚀 Ready to enable autonomous agent coordination in your system!**
