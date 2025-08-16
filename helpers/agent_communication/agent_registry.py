"""
Agent Registry System
=====================

Manages agent registration, capabilities, and status tracking.
Provides load balancing and agent discovery functionality.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import pyodbc
from .message_protocol import AgentRole


@dataclass
class AgentInfo:
    """Information about a registered agent"""
    agent_id: str
    agent_role: AgentRole
    status: str  # active, idle, busy, offline, error
    capabilities: List[str]
    max_concurrent_tasks: int = 1
    current_tasks: int = 0
    load_factor: float = 0.0  # 0.0 to 1.0
    last_heartbeat: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now(timezone.utc).isoformat()
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks"""
        return (
            self.status in ['active', 'idle'] and
            self.current_tasks < self.max_concurrent_tasks and
            not self.is_stale()
        )
    
    def is_stale(self, max_age_minutes: int = 5) -> bool:
        """Check if agent heartbeat is stale"""
        if not self.last_heartbeat:
            return True
        
        last_beat = datetime.fromisoformat(self.last_heartbeat.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) - last_beat > timedelta(minutes=max_age_minutes)
    
    def calculate_load(self) -> float:
        """Calculate actual load factor"""
        if self.max_concurrent_tasks == 0:
            return 1.0 if self.current_tasks > 0 else 0.0
        return min(1.0, self.current_tasks / self.max_concurrent_tasks)


class AgentRegistry:
    """Manages agent registration and discovery"""
    
    def __init__(self, connection_string: Optional[str] = None, mock_mode: bool = None):
        """
        Initialize the agent registry.
        
        Args:
            connection_string: Azure SQL connection string
            mock_mode: If True, use in-memory storage instead of database
        """
        self.connection_string = connection_string or os.getenv('AZURE_SQL_CONNECTION_STRING')
        
        # Auto-detect mock mode if not specified
        if mock_mode is None:
            self.mock_mode = not bool(self.connection_string)
        else:
            self.mock_mode = mock_mode
        
        if self.mock_mode:
            self.mock_agents: Dict[str, AgentInfo] = {}
            logging.info("AgentRegistry initialized in mock mode")
        else:
            self._test_connection()
            logging.info("AgentRegistry initialized with Azure SQL")
    
    def _test_connection(self) -> bool:
        """Test the database connection"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True
        except Exception as e:
            logging.error(f"Database connection test failed: {e}")
            self.mock_mode = True
            self.mock_agents = {}
            logging.warning("Falling back to mock mode due to connection failure")
            return False
    
    def register_agent(
        self,
        agent_id: str,
        agent_role: AgentRole,
        capabilities: List[str],
        max_concurrent_tasks: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register or update an agent in the registry.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_role: Role of the agent (supervisor, worker, etc.)
            capabilities: List of capabilities this agent supports
            max_concurrent_tasks: Maximum tasks this agent can handle concurrently
            metadata: Additional agent-specific metadata
            
        Returns:
            bool: True if registration was successful
        """
        try:
            agent_info = AgentInfo(
                agent_id=agent_id,
                agent_role=agent_role,
                status='active',
                capabilities=capabilities,
                max_concurrent_tasks=max_concurrent_tasks,
                metadata=metadata or {}
            )
            
            if self.mock_mode:
                return self._register_agent_mock(agent_info)
            else:
                return self._register_agent_sql(agent_info)
                
        except Exception as e:
            logging.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    def _register_agent_mock(self, agent_info: AgentInfo) -> bool:
        """Register agent in mock mode"""
        self.mock_agents[agent_info.agent_id] = agent_info
        logging.info(f"🤖 [MOCK] Registered agent: {agent_info.agent_id} ({agent_info.agent_role.value})")
        logging.info(f"   Capabilities: {', '.join(agent_info.capabilities)}")
        return True
    
    def _register_agent_sql(self, agent_info: AgentInfo) -> bool:
        """Register agent in Azure SQL"""
        query = """
        EXEC sp_upsert_agent 
            @agent_id = ?, 
            @agent_role = ?, 
            @capabilities = ?, 
            @max_concurrent_tasks = ?
        """
        
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                agent_info.agent_id,
                agent_info.agent_role.value,
                json.dumps(agent_info.capabilities),
                agent_info.max_concurrent_tasks
            ))
            conn.commit()
        
        logging.info(f"🤖 [SQL] Registered agent: {agent_info.agent_id}")
        return True
    
    def update_heartbeat(
        self,
        agent_id: str,
        status: str = 'active',
        current_tasks: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update agent heartbeat and status.
        
        Args:
            agent_id: ID of the agent
            status: Current status of the agent
            current_tasks: Number of tasks currently being processed
            metadata: Additional status information
            
        Returns:
            bool: True if update was successful
        """
        try:
            if self.mock_mode:
                return self._update_heartbeat_mock(agent_id, status, current_tasks, metadata)
            else:
                return self._update_heartbeat_sql(agent_id, status, current_tasks, metadata)
        except Exception as e:
            logging.error(f"Failed to update heartbeat for {agent_id}: {e}")
            return False
    
    def _update_heartbeat_mock(self, agent_id: str, status: str, current_tasks: int, metadata: Optional[Dict[str, Any]]) -> bool:
        """Update heartbeat in mock mode"""
        if agent_id in self.mock_agents:
            agent = self.mock_agents[agent_id]
            agent.status = status
            agent.current_tasks = current_tasks
            agent.load_factor = agent.calculate_load()
            agent.last_heartbeat = datetime.now(timezone.utc).isoformat()
            if metadata:
                agent.metadata.update(metadata)
            
            logging.debug(f"💓 [MOCK] Heartbeat updated for {agent_id}: {status}, {current_tasks} tasks")
            return True
        else:
            logging.warning(f"Agent {agent_id} not found for heartbeat update")
            return False
    
    def _update_heartbeat_sql(self, agent_id: str, status: str, current_tasks: int, metadata: Optional[Dict[str, Any]]) -> bool:
        """Update heartbeat in Azure SQL"""
        load_factor = 0.0
        
        # Calculate load factor (need to get max_concurrent_tasks from DB)
        query_load = "SELECT max_concurrent_tasks FROM agent_registry WHERE agent_id = ?"
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query_load, (agent_id,))
            row = cursor.fetchone()
            if row and row[0] > 0:
                load_factor = min(1.0, current_tasks / row[0])
        
        # Update the agent record
        query_update = """
        UPDATE agent_registry 
        SET status = ?, 
            current_task_id = ?, 
            load_factor = ?, 
            last_heartbeat = GETUTCDATE(),
            updated_at = GETUTCDATE(),
            metadata = ?
        WHERE agent_id = ?
        """
        
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query_update, (
                status,
                str(current_tasks),
                load_factor,
                json.dumps(metadata) if metadata else None,
                agent_id
            ))
            rows_affected = cursor.rowcount
            conn.commit()
        
        if rows_affected > 0:
            logging.debug(f"💓 [SQL] Heartbeat updated for {agent_id}")
            return True
        else:
            logging.warning(f"Agent {agent_id} not found for heartbeat update")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get information about a specific agent"""
        try:
            if self.mock_mode:
                return self.mock_agents.get(agent_id)
            else:
                return self._get_agent_sql(agent_id)
        except Exception as e:
            logging.error(f"Failed to get agent {agent_id}: {e}")
            return None
    
    def _get_agent_sql(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent from Azure SQL"""
        query = """
        SELECT agent_id, agent_role, status, capabilities, max_concurrent_tasks,
               load_factor, last_heartbeat, metadata
        FROM agent_registry 
        WHERE agent_id = ?
        """
        
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (agent_id,))
            row = cursor.fetchone()
            
            if row:
                capabilities = json.loads(row.capabilities) if row.capabilities else []
                metadata = json.loads(row.metadata) if row.metadata else {}
                
                return AgentInfo(
                    agent_id=row.agent_id,
                    agent_role=AgentRole(row.agent_role),
                    status=row.status,
                    capabilities=capabilities,
                    max_concurrent_tasks=row.max_concurrent_tasks,
                    load_factor=float(row.load_factor) if row.load_factor else 0.0,
                    last_heartbeat=row.last_heartbeat.isoformat() if row.last_heartbeat else None,
                    metadata=metadata
                )
        
        return None
    
    def find_available_agents(
        self,
        required_capabilities: Optional[List[str]] = None,
        agent_role: Optional[AgentRole] = None,
        max_results: int = 10
    ) -> List[AgentInfo]:
        """
        Find available agents matching the specified criteria.
        
        Args:
            required_capabilities: List of required capabilities
            agent_role: Required agent role
            max_results: Maximum number of agents to return
            
        Returns:
            List of available AgentInfo objects, sorted by load factor
        """
        try:
            if self.mock_mode:
                return self._find_available_agents_mock(required_capabilities, agent_role, max_results)
            else:
                return self._find_available_agents_sql(required_capabilities, agent_role, max_results)
        except Exception as e:
            logging.error(f"Failed to find available agents: {e}")
            return []
    
    def _find_available_agents_mock(
        self,
        required_capabilities: Optional[List[str]],
        agent_role: Optional[AgentRole],
        max_results: int
    ) -> List[AgentInfo]:
        """Find available agents in mock mode"""
        available_agents = []
        
        for agent in self.mock_agents.values():
            # Check if agent is available
            if not agent.is_available():
                continue
            
            # Check role filter
            if agent_role and agent.agent_role != agent_role:
                continue
            
            # Check capabilities filter
            if required_capabilities:
                if not all(cap in agent.capabilities for cap in required_capabilities):
                    continue
            
            available_agents.append(agent)
        
        # Sort by load factor (prefer less loaded agents)
        available_agents.sort(key=lambda a: a.calculate_load())
        
        result = available_agents[:max_results]
        logging.info(f"🔍 [MOCK] Found {len(result)} available agents")
        return result
    
    def _find_available_agents_sql(
        self,
        required_capabilities: Optional[List[str]],
        agent_role: Optional[AgentRole],
        max_results: int
    ) -> List[AgentInfo]:
        """Find available agents in Azure SQL"""
        # Use the view for active agents with current workload
        query = f"""
        SELECT TOP ({max_results})
            agent_id, agent_role, status, load_factor, max_concurrent_tasks,
            current_tasks, last_heartbeat
        FROM vw_active_agents
        WHERE 1=1
        """
        
        params = []
        
        if agent_role:
            query += " AND agent_role = ?"
            params.append(agent_role.value)
        
        # For capabilities, we'd need to query the full table to check JSON
        if required_capabilities:
            query = query.replace("FROM vw_active_agents", "FROM agent_registry")
            # This is a simplified check - in production, use JSON functions
            for cap in required_capabilities:
                query += " AND capabilities LIKE ?"
                params.append(f'%"{cap}"%')
        
        query += " ORDER BY load_factor"
        
        agents = []
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                agent_info = AgentInfo(
                    agent_id=row.agent_id,
                    agent_role=AgentRole(row.agent_role),
                    status=row.status,
                    capabilities=[],  # Would need separate query for full capabilities
                    max_concurrent_tasks=row.max_concurrent_tasks,
                    current_tasks=getattr(row, 'current_tasks', 0),
                    load_factor=float(row.load_factor) if row.load_factor else 0.0,
                    last_heartbeat=row.last_heartbeat.isoformat() if row.last_heartbeat else None
                )
                agents.append(agent_info)
        
        logging.info(f"🔍 [SQL] Found {len(agents)} available agents")
        return agents
    
    def get_all_agents(self, include_offline: bool = False) -> List[AgentInfo]:
        """Get all registered agents"""
        try:
            if self.mock_mode:
                agents = list(self.mock_agents.values())
                if not include_offline:
                    agents = [a for a in agents if not a.is_stale()]
                return agents
            else:
                # TODO: Implement SQL query for all agents
                return []
        except Exception as e:
            logging.error(f"Failed to get all agents: {e}")
            return []
    
    def cleanup_stale_agents(self, max_age_minutes: int = 10) -> int:
        """Mark stale agents as offline"""
        try:
            if self.mock_mode:
                stale_count = 0
                for agent in self.mock_agents.values():
                    if agent.is_stale(max_age_minutes):
                        agent.status = 'offline'
                        stale_count += 1
                
                logging.info(f"🧹 [MOCK] Marked {stale_count} stale agents as offline")
                return stale_count
            else:
                # TODO: Implement SQL cleanup for stale agents
                logging.info("🧹 [SQL] Would cleanup stale agents")
                return 0
        except Exception as e:
            logging.error(f"Failed to cleanup stale agents: {e}")
            return 0
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent registry"""
        if self.mock_mode:
            agents = list(self.mock_agents.values())
            stats = {
                "total_agents": len(agents),
                "by_role": {},
                "by_status": {},
                "average_load": 0.0
            }
            
            if agents:
                # Group by role
                for agent in agents:
                    role = agent.agent_role.value
                    stats["by_role"][role] = stats["by_role"].get(role, 0) + 1
                
                # Group by status
                for agent in agents:
                    status = agent.status
                    stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                # Calculate average load
                total_load = sum(agent.calculate_load() for agent in agents)
                stats["average_load"] = total_load / len(agents)
            
            return stats
        else:
            # TODO: Implement SQL stats query
            return {"mode": "sql", "stats": "not_implemented"}


# Convenience functions
def create_simple_registry() -> AgentRegistry:
    """Create an agent registry with automatic configuration"""
    return AgentRegistry()


def register_supervisor_agent(registry: AgentRegistry, agent_id: str) -> bool:
    """Register a supervisor agent with standard capabilities"""
    return registry.register_agent(
        agent_id=agent_id,
        agent_role=AgentRole.SUPERVISOR,
        capabilities=[
            "task_coordination",
            "agent_management", 
            "project_planning",
            "github_integration"
        ],
        max_concurrent_tasks=5
    )


def register_worker_agent(registry: AgentRegistry, agent_id: str, specialization: str) -> bool:
    """Register a worker agent with specific capabilities"""
    capabilities_map = {
        "backend": ["python", "api_development", "database", "testing"],
        "frontend": ["javascript", "react", "html", "css", "testing"],
        "devops": ["terraform", "azure", "ci_cd", "docker", "monitoring"],
        "testing": ["unit_testing", "integration_testing", "test_automation"],
        "documentation": ["technical_writing", "markdown", "api_docs"]
    }
    
    capabilities = capabilities_map.get(specialization, ["general_programming"])
    
    return registry.register_agent(
        agent_id=agent_id,
        agent_role=AgentRole.WORKER,
        capabilities=capabilities,
        max_concurrent_tasks=2,
        metadata={"specialization": specialization}
    )
