-- Agent Communication System Database Schema
-- ============================================
--
-- This schema supports autonomous agent communication using Azure SQL Server
-- with Entra ID authentication. Designed for minimal complexity while supporting
-- asynchronous message passing and task coordination.

-- Drop existing tables if they exist (for development)
-- Uncomment these lines when recreating schema
-- DROP TABLE IF EXISTS task_coordination;
-- DROP TABLE IF EXISTS agent_messages;
-- DROP TABLE IF EXISTS agent_registry;

-- =============================================================================
-- Agent Registry Table
-- =============================================================================
-- Tracks all agents in the system, their capabilities, and current status

CREATE TABLE agent_registry (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    agent_id NVARCHAR(100) UNIQUE NOT NULL,
    agent_role NVARCHAR(50) NOT NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'offline',  -- active, idle, busy, offline, error
    last_heartbeat DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    capabilities NVARCHAR(MAX) NULL,  -- JSON array of capabilities
    current_task_id NVARCHAR(100) NULL,
    load_factor DECIMAL(3,2) NULL DEFAULT 0.0,  -- 0.0 to 1.0
    max_concurrent_tasks INT NOT NULL DEFAULT 1,
    metadata NVARCHAR(MAX) NULL,  -- JSON for additional agent-specific data
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    -- Indexes for performance
    INDEX IX_agent_registry_agent_id (agent_id),
    INDEX IX_agent_registry_role (agent_role),
    INDEX IX_agent_registry_status (status),
    INDEX IX_agent_registry_heartbeat (last_heartbeat),
    INDEX IX_agent_registry_load (load_factor)
);

-- =============================================================================
-- Agent Messages Table
-- =============================================================================
-- Core message queue for agent-to-agent communication

CREATE TABLE agent_messages (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    message_id NVARCHAR(100) UNIQUE NOT NULL,
    from_agent NVARCHAR(100) NOT NULL,
    to_agent NVARCHAR(100) NULL,  -- NULL for broadcast messages
    message_type NVARCHAR(50) NOT NULL,
    content NVARCHAR(MAX) NOT NULL,  -- JSON content
    parent_message_id NVARCHAR(100) NULL,
    priority INT NOT NULL DEFAULT 3,  -- 1=critical, 5=background
    status NVARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, processing, processed, failed, expired
    retry_count INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 3,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    processed_at DATETIME2 NULL,
    expires_at DATETIME2 NULL,
    error_message NVARCHAR(MAX) NULL,
    
    -- Foreign key constraints
    FOREIGN KEY (from_agent) REFERENCES agent_registry(agent_id),
    
    -- Indexes for performance
    INDEX IX_agent_messages_message_id (message_id),
    INDEX IX_agent_messages_from_agent (from_agent),
    INDEX IX_agent_messages_to_agent (to_agent),
    INDEX IX_agent_messages_status (status),
    INDEX IX_agent_messages_priority_created (priority, created_at),
    INDEX IX_agent_messages_parent (parent_message_id),
    INDEX IX_agent_messages_type (message_type),
    INDEX IX_agent_messages_expires (expires_at)
);

-- =============================================================================
-- Task Coordination Table
-- =============================================================================
-- Tracks task assignments, dependencies, and execution status

CREATE TABLE task_coordination (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    task_id NVARCHAR(100) UNIQUE NOT NULL,
    parent_task_id NVARCHAR(100) NULL,
    assigned_agent NVARCHAR(100) NOT NULL,
    supervisor_agent NVARCHAR(100) NOT NULL,
    task_type NVARCHAR(50) NOT NULL,
    task_name NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX) NULL,
    priority INT NOT NULL DEFAULT 5,  -- 1=highest, 10=lowest
    status NVARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, assigned, in_progress, completed, failed, cancelled
    progress DECIMAL(3,2) NOT NULL DEFAULT 0.0,  -- 0.0 to 1.0
    task_data NVARCHAR(MAX) NOT NULL,  -- JSON task details and parameters
    result_data NVARCHAR(MAX) NULL,  -- JSON result data
    error_message NVARCHAR(MAX) NULL,
    estimated_hours DECIMAL(5,2) NULL,
    actual_hours DECIMAL(5,2) NULL,
    deadline DATETIME2 NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    assigned_at DATETIME2 NULL,
    started_at DATETIME2 NULL,
    completed_at DATETIME2 NULL,
    
    -- Foreign key constraints
    FOREIGN KEY (assigned_agent) REFERENCES agent_registry(agent_id),
    FOREIGN KEY (supervisor_agent) REFERENCES agent_registry(agent_id),
    FOREIGN KEY (parent_task_id) REFERENCES task_coordination(task_id),
    
    -- Indexes for performance
    INDEX IX_task_coordination_task_id (task_id),
    INDEX IX_task_coordination_assigned (assigned_agent),
    INDEX IX_task_coordination_supervisor (supervisor_agent),
    INDEX IX_task_coordination_status (status),
    INDEX IX_task_coordination_priority_created (priority, created_at),
    INDEX IX_task_coordination_parent (parent_task_id),
    INDEX IX_task_coordination_deadline (deadline),
    INDEX IX_task_coordination_type (task_type)
);

-- =============================================================================
-- Agent Performance Metrics (Optional)
-- =============================================================================
-- Tracks agent performance for optimization and load balancing

CREATE TABLE agent_metrics (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    agent_id NVARCHAR(100) NOT NULL,
    metric_type NVARCHAR(50) NOT NULL,  -- task_completion_time, error_rate, throughput, etc.
    metric_value DECIMAL(10,4) NOT NULL,
    measurement_period NVARCHAR(20) NOT NULL,  -- hourly, daily, weekly
    recorded_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    metadata NVARCHAR(MAX) NULL,  -- JSON for additional metric data
    
    -- Foreign key constraints
    FOREIGN KEY (agent_id) REFERENCES agent_registry(agent_id),
    
    -- Indexes for performance
    INDEX IX_agent_metrics_agent_type (agent_id, metric_type),
    INDEX IX_agent_metrics_recorded (recorded_at),
    INDEX IX_agent_metrics_period (measurement_period, recorded_at)
);

-- =============================================================================
-- Views for Common Queries
-- =============================================================================

-- Active agents with their current workload
CREATE VIEW vw_active_agents AS
SELECT 
    ar.agent_id,
    ar.agent_role,
    ar.status,
    ar.load_factor,
    ar.max_concurrent_tasks,
    ar.last_heartbeat,
    COUNT(tc.task_id) as current_tasks,
    CASE 
        WHEN ar.max_concurrent_tasks > 0 
        THEN CAST(COUNT(tc.task_id) AS DECIMAL(3,2)) / ar.max_concurrent_tasks 
        ELSE 0.0 
    END as actual_load
FROM agent_registry ar
LEFT JOIN task_coordination tc ON ar.agent_id = tc.assigned_agent 
    AND tc.status IN ('assigned', 'in_progress')
WHERE ar.status IN ('active', 'idle', 'busy')
    AND ar.last_heartbeat > DATEADD(MINUTE, -5, GETUTCDATE())
GROUP BY ar.agent_id, ar.agent_role, ar.status, ar.load_factor, 
         ar.max_concurrent_tasks, ar.last_heartbeat;

-- Pending messages by priority
CREATE VIEW vw_pending_messages AS
SELECT 
    am.message_id,
    am.from_agent,
    am.to_agent,
    am.message_type,
    am.priority,
    am.created_at,
    am.retry_count,
    am.expires_at,
    CASE 
        WHEN am.expires_at IS NOT NULL AND am.expires_at < GETUTCDATE() 
        THEN 1 
        ELSE 0 
    END as is_expired
FROM agent_messages am
WHERE am.status = 'pending'
    AND (am.expires_at IS NULL OR am.expires_at > GETUTCDATE())
    AND am.retry_count < am.max_retries;

-- Task queue by priority and assignment
CREATE VIEW vw_task_queue AS
SELECT 
    tc.task_id,
    tc.task_name,
    tc.task_type,
    tc.assigned_agent,
    tc.supervisor_agent,
    tc.priority,
    tc.status,
    tc.progress,
    tc.created_at,
    tc.deadline,
    CASE 
        WHEN tc.deadline IS NOT NULL AND tc.deadline < GETUTCDATE() 
        THEN 1 
        ELSE 0 
    END as is_overdue,
    DATEDIFF(HOUR, tc.created_at, GETUTCDATE()) as age_hours
FROM task_coordination tc
WHERE tc.status IN ('pending', 'assigned', 'in_progress')
ORDER BY tc.priority, tc.created_at;

-- =============================================================================
-- Stored Procedures for Common Operations
-- =============================================================================

-- Register or update an agent
CREATE OR ALTER PROCEDURE sp_upsert_agent
    @agent_id NVARCHAR(100),
    @agent_role NVARCHAR(50),
    @capabilities NVARCHAR(MAX) = NULL,
    @max_concurrent_tasks INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    MERGE agent_registry AS target
    USING (SELECT @agent_id as agent_id, @agent_role as agent_role, 
                  @capabilities as capabilities, @max_concurrent_tasks as max_concurrent_tasks) AS source
    ON target.agent_id = source.agent_id
    WHEN MATCHED THEN
        UPDATE SET 
            agent_role = source.agent_role,
            capabilities = source.capabilities,
            max_concurrent_tasks = source.max_concurrent_tasks,
            last_heartbeat = GETUTCDATE(),
            updated_at = GETUTCDATE(),
            status = 'active'
    WHEN NOT MATCHED THEN
        INSERT (agent_id, agent_role, capabilities, max_concurrent_tasks, status)
        VALUES (source.agent_id, source.agent_role, source.capabilities, 
                source.max_concurrent_tasks, 'active');
END;

-- Get next message for an agent
CREATE OR ALTER PROCEDURE sp_get_next_message
    @agent_id NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Get highest priority pending message for this agent or broadcast
    SELECT TOP 1 *
    FROM agent_messages
    WHERE (to_agent = @agent_id OR to_agent IS NULL)
        AND status = 'pending'
        AND (expires_at IS NULL OR expires_at > GETUTCDATE())
        AND retry_count < max_retries
    ORDER BY priority, created_at;
END;

-- Mark message as processed
CREATE OR ALTER PROCEDURE sp_mark_message_processed
    @message_id NVARCHAR(100),
    @processing_agent NVARCHAR(100),
    @status NVARCHAR(20) = 'processed',
    @error_message NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE agent_messages
    SET status = @status,
        processed_at = GETUTCDATE(),
        error_message = @error_message
    WHERE message_id = @message_id
        AND (to_agent = @processing_agent OR to_agent IS NULL);
        
    SELECT @@ROWCOUNT as rows_affected;
END;

-- =============================================================================
-- Indexes for Performance Optimization
-- =============================================================================

-- Composite indexes for common query patterns
CREATE INDEX IX_messages_agent_status_priority 
ON agent_messages (to_agent, status, priority, created_at);

CREATE INDEX IX_tasks_agent_status_priority 
ON task_coordination (assigned_agent, status, priority, created_at);

CREATE INDEX IX_registry_role_status_heartbeat 
ON agent_registry (agent_role, status, last_heartbeat);

-- =============================================================================
-- Data Cleanup and Maintenance
-- =============================================================================

-- Cleanup old processed messages (run periodically)
-- DELETE FROM agent_messages 
-- WHERE status IN ('processed', 'expired') 
--   AND processed_at < DATEADD(DAY, -7, GETUTCDATE());

-- Cleanup old completed tasks (run periodically)  
-- DELETE FROM task_coordination 
-- WHERE status IN ('completed', 'cancelled') 
--   AND completed_at < DATEADD(DAY, -30, GETUTCDATE());

-- Mark offline agents as inactive
-- UPDATE agent_registry 
-- SET status = 'offline' 
-- WHERE status != 'offline' 
--   AND last_heartbeat < DATEADD(MINUTE, -10, GETUTCDATE());

PRINT 'Agent Communication System schema created successfully!';
