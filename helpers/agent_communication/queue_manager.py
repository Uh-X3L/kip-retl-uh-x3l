"""
Message Queue Manager
=====================

Manages agent message passing via Azure SQL Server with Entra ID authentication.
Provides a simple interface for sending, receiving, and processing messages between agents.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
import pyodbc
from .message_protocol import AgentMessage, MessageType, MessagePriority, AgentRole


class MessageQueueManager:
    """Manages agent message queue using Azure SQL Server"""
    
    def __init__(self, connection_string: Optional[str] = None, mock_mode: bool = None):
        """
        Initialize the message queue manager.
        
        Args:
            connection_string: Azure SQL connection string with Entra ID auth
            mock_mode: If True, use in-memory mock instead of real database
        """
        self.connection_string = connection_string or os.getenv('AZURE_SQL_CONNECTION_STRING')
        
        # Auto-detect mock mode if not specified
        if mock_mode is None:
            self.mock_mode = not bool(self.connection_string)
        else:
            self.mock_mode = mock_mode
            
        if self.mock_mode:
            self.mock_messages = []
            self.mock_agents = {}
            logging.info("MessageQueueManager initialized in mock mode")
        else:
            self._test_connection()
            logging.info("MessageQueueManager initialized with Azure SQL")
    
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
            # Fall back to mock mode if connection fails
            self.mock_mode = True
            self.mock_messages = []
            self.mock_agents = {}
            logging.warning("Falling back to mock mode due to connection failure")
            return False
    
    def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message to the queue.
        
        Args:
            message: AgentMessage to send
            
        Returns:
            bool: True if message was sent successfully
        """
        try:
            if self.mock_mode:
                return self._send_message_mock(message)
            else:
                return self._send_message_sql(message)
        except Exception as e:
            logging.error(f"Failed to send message {message.message_id}: {e}")
            return False
    
    def _send_message_mock(self, message: AgentMessage) -> bool:
        """Send message in mock mode"""
        # Add to mock storage
        self.mock_messages.append(message)
        
        # Log the message
        recipient = message.to_agent or "ALL"
        logging.info(f"📤 [MOCK] Message sent: {message.from_agent} → {recipient}")
        logging.info(f"   Type: {message.message_type.value}, Priority: {message.priority.value}")
        logging.info(f"   Content: {str(message.content)[:100]}...")
        
        return True
    
    def _send_message_sql(self, message: AgentMessage) -> bool:
        """Send message to Azure SQL"""
        query = """
        INSERT INTO agent_messages (
            message_id, from_agent, to_agent, message_type, content,
            parent_message_id, priority, status, retry_count, max_retries,
            created_at, expires_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                message.message_id,
                message.from_agent,
                message.to_agent,
                message.message_type.value,
                message.to_json(),
                message.parent_message_id,
                message.priority.value,
                message.status,
                message.retry_count,
                message.max_retries,
                message.created_at,
                message.expires_at
            ))
            conn.commit()
            
        logging.info(f"📤 [SQL] Message sent: {message.message_id}")
        return True
    
    def get_messages(self, agent_id: str, limit: int = 10, message_types: Optional[List[MessageType]] = None) -> List[AgentMessage]:
        """
        Get pending messages for an agent.
        
        Args:
            agent_id: ID of the agent requesting messages
            limit: Maximum number of messages to return
            message_types: Optional filter for specific message types
            
        Returns:
            List of AgentMessage objects
        """
        try:
            if self.mock_mode:
                return self._get_messages_mock(agent_id, limit, message_types)
            else:
                return self._get_messages_sql(agent_id, limit, message_types)
        except Exception as e:
            logging.error(f"Failed to get messages for {agent_id}: {e}")
            return []
    
    def _get_messages_mock(self, agent_id: str, limit: int, message_types: Optional[List[MessageType]]) -> List[AgentMessage]:
        """Get messages in mock mode"""
        # Filter messages for this agent
        filtered_messages = []
        
        for msg in self.mock_messages:
            # Check if message is for this agent (direct or broadcast)
            if (msg.to_agent == agent_id or msg.to_agent is None) and msg.status == "pending":
                # Check message type filter
                if message_types is None or msg.message_type in message_types:
                    # Check if not expired
                    if not msg.is_expired():
                        filtered_messages.append(msg)
        
        # Sort by priority and creation time
        filtered_messages.sort(key=lambda x: (x.priority.value, x.created_at))
        
        # Apply limit
        result = filtered_messages[:limit]
        
        logging.info(f"📥 [MOCK] Retrieved {len(result)} messages for {agent_id}")
        return result
    
    def _get_messages_sql(self, agent_id: str, limit: int, message_types: Optional[List[MessageType]]) -> List[AgentMessage]:
        """Get messages from Azure SQL"""
        query = """
        SELECT TOP (?) 
            message_id, from_agent, to_agent, message_type, content,
            parent_message_id, priority, status, retry_count, max_retries,
            created_at, processed_at, expires_at
        FROM agent_messages
        WHERE (to_agent = ? OR to_agent IS NULL)
            AND status = 'pending'
            AND (expires_at IS NULL OR expires_at > GETUTCDATE())
            AND retry_count < max_retries
        """
        
        params = [limit, agent_id]
        
        # Add message type filter if specified
        if message_types:
            type_values = [mt.value for mt in message_types]
            placeholders = ','.join(['?' for _ in type_values])
            query += f" AND message_type IN ({placeholders})"
            params.extend(type_values)
        
        query += " ORDER BY priority, created_at"
        
        messages = []
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                # Parse the JSON content back to create AgentMessage
                content_data = json.loads(row.content)
                message = AgentMessage(
                    message_id=row.message_id,
                    from_agent=row.from_agent,
                    to_agent=row.to_agent,
                    message_type=MessageType(row.message_type),
                    content=content_data.get('content', {}),
                    parent_message_id=row.parent_message_id,
                    priority=MessagePriority(row.priority),
                    created_at=row.created_at.isoformat() if row.created_at else None,
                    processed_at=row.processed_at.isoformat() if row.processed_at else None,
                    status=row.status,
                    retry_count=row.retry_count,
                    max_retries=row.max_retries,
                    expires_at=row.expires_at.isoformat() if row.expires_at else None
                )
                messages.append(message)
        
        logging.info(f"📥 [SQL] Retrieved {len(messages)} messages for {agent_id}")
        return messages
    
    def mark_processed(self, message_id: str, agent_id: str, status: str = "processed", error_message: Optional[str] = None) -> bool:
        """
        Mark a message as processed.
        
        Args:
            message_id: ID of the message to mark
            agent_id: ID of the agent that processed the message
            status: New status (processed, failed, etc.)
            error_message: Optional error message if processing failed
            
        Returns:
            bool: True if message was marked successfully
        """
        try:
            if self.mock_mode:
                return self._mark_processed_mock(message_id, agent_id, status, error_message)
            else:
                return self._mark_processed_sql(message_id, agent_id, status, error_message)
        except Exception as e:
            logging.error(f"Failed to mark message {message_id} as processed: {e}")
            return False
    
    def _mark_processed_mock(self, message_id: str, agent_id: str, status: str, error_message: Optional[str]) -> bool:
        """Mark message as processed in mock mode"""
        for msg in self.mock_messages:
            if msg.message_id == message_id:
                msg.status = status
                msg.processed_at = datetime.now(timezone.utc).isoformat()
                if error_message:
                    msg.content['error_message'] = error_message
                
                logging.info(f"✅ [MOCK] Marked message {message_id} as {status}")
                return True
        
        logging.warning(f"Message {message_id} not found for processing")
        return False
    
    def _mark_processed_sql(self, message_id: str, agent_id: str, status: str, error_message: Optional[str]) -> bool:
        """Mark message as processed in Azure SQL"""
        query = """
        UPDATE agent_messages
        SET status = ?, processed_at = GETUTCDATE(), error_message = ?
        WHERE message_id = ?
            AND (to_agent = ? OR to_agent IS NULL)
        """
        
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (status, error_message, message_id, agent_id))
            rows_affected = cursor.rowcount
            conn.commit()
        
        if rows_affected > 0:
            logging.info(f"✅ [SQL] Marked message {message_id} as {status}")
            return True
        else:
            logging.warning(f"Message {message_id} not found or not accessible to {agent_id}")
            return False
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an agent"""
        if self.mock_mode:
            return self.mock_agents.get(agent_id)
        else:
            # TODO: Implement SQL query for agent status
            return None
    
    def update_agent_heartbeat(self, agent_id: str, status_info: Dict[str, Any]) -> bool:
        """Update agent heartbeat and status"""
        try:
            if self.mock_mode:
                self.mock_agents[agent_id] = {
                    **status_info,
                    'last_heartbeat': datetime.now(timezone.utc).isoformat()
                }
                logging.info(f"💓 [MOCK] Updated heartbeat for {agent_id}")
                return True
            else:
                # TODO: Implement SQL update for agent heartbeat
                logging.info(f"💓 [SQL] Would update heartbeat for {agent_id}")
                return True
        except Exception as e:
            logging.error(f"Failed to update heartbeat for {agent_id}: {e}")
            return False
    
    def cleanup_expired_messages(self) -> int:
        """Clean up expired and old processed messages"""
        try:
            if self.mock_mode:
                initial_count = len(self.mock_messages)
                self.mock_messages = [
                    msg for msg in self.mock_messages
                    if not msg.is_expired() and msg.status != "processed"
                ]
                cleaned = initial_count - len(self.mock_messages)
                logging.info(f"🧹 [MOCK] Cleaned up {cleaned} expired/processed messages")
                return cleaned
            else:
                # TODO: Implement SQL cleanup query
                logging.info("🧹 [SQL] Would clean up expired messages")
                return 0
        except Exception as e:
            logging.error(f"Failed to cleanup messages: {e}")
            return 0
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the message queue"""
        if self.mock_mode:
            pending = len([m for m in self.mock_messages if m.status == "pending"])
            processed = len([m for m in self.mock_messages if m.status == "processed"])
            failed = len([m for m in self.mock_messages if m.status == "failed"])
            
            return {
                "total_messages": len(self.mock_messages),
                "pending": pending,
                "processed": processed,
                "failed": failed,
                "active_agents": len(self.mock_agents)
            }
        else:
            # TODO: Implement SQL stats query
            return {"mode": "sql", "stats": "not_implemented"}


# Convenience functions for common operations
def create_simple_queue_manager() -> MessageQueueManager:
    """Create a message queue manager with automatic configuration"""
    return MessageQueueManager()


def send_task_to_agent(
    queue: MessageQueueManager,
    from_agent: str,
    to_agent: str,
    task_type: str,
    task_data: Dict[str, Any],
    priority: MessagePriority = MessagePriority.MEDIUM
) -> bool:
    """Send a task request to a specific agent"""
    from .message_protocol import create_task_request_message, TaskRequest
    
    task_request = TaskRequest(
        task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{to_agent}",
        task_type=task_type,
        description=task_data.get('description', f'{task_type} task'),
        parameters=task_data
    )
    
    message = create_task_request_message(from_agent, to_agent, task_request, priority)
    return queue.send_message(message)


def broadcast_to_all_agents(
    queue: MessageQueueManager,
    from_agent: str,
    content: Dict[str, Any],
    message_type: MessageType = MessageType.BROADCAST
) -> bool:
    """Send a broadcast message to all agents"""
    from .message_protocol import create_broadcast_message
    
    message = create_broadcast_message(from_agent, content, message_type)
    return queue.send_message(message)
