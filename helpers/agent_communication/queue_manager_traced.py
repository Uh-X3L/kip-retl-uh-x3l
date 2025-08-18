"""
Message Queue Manager
=====================

Manages agent message passing via Redis Streams for high-performance, scalable messaging.
Provides a simple interface for sending, receiving, and processing messages between agents.
"""

import os
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta

# SNOOP TRACING ADDED - Added by snoop integration script
import snoop

# Snoop decorator for functions
trace_func = snoop.snoop

# Snoop decorator for classes  
@trace_func
def trace_class(cls):
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_') and hasattr(attr, '__module__'):
            setattr(cls, attr_name, trace_func(attr))
    return cls


try:
    import redis
except ImportError:
    redis = None
from message_protocol import AgentMessage, MessageType, MessagePriority

# Import optional file logging
try:
    from file_logger import get_file_logger, log_message_sent, log_message_processed
except ImportError:
    # File logging is optional
    @trace_func
    def get_file_logger():
        return None
    @trace_func
    def log_message_sent(*args, **kwargs):
        pass
    @trace_func
    def log_message_processed(*args, **kwargs):
        pass


@trace_class
class MessageQueueManager:
    """Manages agent message queue using Redis Streams for high-performance messaging"""
    
    def __init__(self, redis_url: Optional[str] = None, use_mock: bool = False):
        """
        Initialize the message queue manager.
        
        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379)
            use_mock: If True, use in-memory mock instead of Redis
        """
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.use_mock = use_mock
        
        # Stream names for different types of data
        self.message_stream = "agent_messages"
        self.heartbeat_stream = "agent_heartbeats"
        
        if self.use_mock:
            self.mock_messages = []
            self.mock_agents = {}
            self.mock_last_ids = {}
            logging.info("MessageQueueManager initialized in mock mode")
        else:
            try:
                self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
                self._test_connection()
                logging.info(f"MessageQueueManager initialized with Redis at {self.redis_url}")
            except Exception as e:
                logging.error(f"Failed to connect to Redis: {e}")
                logging.warning("Falling back to mock mode")
                self.use_mock = True
                self.mock_messages = []
                self.mock_agents = {}
                self.mock_last_ids = {}
    
    def _test_connection(self) -> bool:
        """Test the Redis connection"""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logging.error(f"Redis connection test failed: {e}")
            raise
    
    @trace_func
    def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message to the queue.
        
        Args:
            message: AgentMessage to send
            
        Returns:
            bool: True if message was sent successfully
        """
        try:
            if self.use_mock:
                return self._send_message_mock(message)
            else:
                return self._send_message_redis(message)
        except Exception as e:
            logging.error(f"Failed to send message {message.message_id}: {e}")
            return False
    
    def _send_message_mock(self, message: AgentMessage) -> bool:
        """Send message in mock mode"""
        # Add to mock storage with timestamp-based ID
        mock_id = f"{int(datetime.now().timestamp() * 1000)}-0"
        mock_message = {
            "id": mock_id,
            "data": message,
            "timestamp": datetime.now(timezone.utc)
        }
        self.mock_messages.append(mock_message)
        
        # Log the message
        recipient = message.to_agent or "ALL"
        logging.info(f"-> [MOCK] Message sent: {message.from_agent} -> {recipient}")
        logging.info(f"   Type: {message.message_type.value}, Priority: {message.priority.value}")
        logging.info(f"   Content: {str(message.content)[:100]}...")
        
        # Optional file logging
        log_message_sent(
            message.message_id, 
            message.from_agent, 
            message.to_agent or "ALL", 
            message.message_type.value
        )
        
        return True
    
    def _send_message_redis(self, message: AgentMessage) -> bool:
        """Send message to Redis Streams"""
        # Prepare message data for Redis (all values must be strings)
        stream_data = {
            "message_id": message.message_id,
            "from_agent": message.from_agent,
            "to_agent": message.to_agent or "",
            "message_type": message.message_type.value,
            "content": json.dumps(message.content),
            "parent_message_id": message.parent_message_id or "",
            "priority": str(message.priority.value),
            "status": message.status,
            "retry_count": str(message.retry_count),
            "max_retries": str(message.max_retries),
            "created_at": message.created_at or datetime.now(timezone.utc).isoformat(),
            "expires_at": message.expires_at or ""
        }
        
        # Add to Redis stream
        stream_id = self.redis_client.xadd(self.message_stream, stream_data)
        
        logging.info(f"-> [REDIS] Message sent: {message.message_id} (stream_id: {stream_id})")
        
        # Optional file logging
        log_message_sent(
            message.message_id, 
            message.from_agent, 
            message.to_agent or "ALL", 
            message.message_type.value
        )
        
        return True
    
    @trace_func
    def get_messages(self, agent_id: str, limit: int = 10, message_types: Optional[List[MessageType]] = None, 
                    last_id: str = "0-0", block_ms: int = 1000) -> List[AgentMessage]:
        """
        Get pending messages for an agent.
        
        Args:
            agent_id: ID of the agent requesting messages
            limit: Maximum number of messages to return
            message_types: Optional filter for specific message types
            last_id: Last message ID seen (for continuous reading)
            block_ms: Milliseconds to block waiting for new messages
            
        Returns:
            List of AgentMessage objects
        """
        try:
            if self.use_mock:
                return self._get_messages_mock(agent_id, limit, message_types, last_id)
            else:
                return self._get_messages_redis(agent_id, limit, message_types, last_id, block_ms)
        except Exception as e:
            logging.error(f"Failed to get messages for {agent_id}: {e}")
            return []
    
    def _get_messages_mock(self, agent_id: str, limit: int, message_types: Optional[List[MessageType]], 
                          last_id: str) -> List[AgentMessage]:
        """Get messages in mock mode"""
        # Get last processed ID for this agent
        agent_last_id = self.mock_last_ids.get(agent_id, "0-0")
        
        # Filter messages for this agent
        filtered_messages = []
        
        for mock_msg in self.mock_messages:
            message = mock_msg["data"]
            
            # Skip if we've already seen this message
            if mock_msg["id"] <= agent_last_id:
                continue
                
            # Check if message is for this agent (direct or broadcast)
            if (message.to_agent == agent_id or message.to_agent is None) and message.status == "pending":
                # Check message type filter
                if message_types is None or message.message_type in message_types:
                    # Check if not expired
                    if not message.is_expired():
                        filtered_messages.append(message)
        
        # Sort by priority and creation time
        filtered_messages.sort(key=lambda x: (x.priority.value, x.created_at))
        
        # Apply limit
        result = filtered_messages[:limit]
        
        # Update last seen ID for this agent
        if result:
            # Find the highest ID we're returning
            for mock_msg in reversed(self.mock_messages):
                if mock_msg["data"] in result:
                    self.mock_last_ids[agent_id] = mock_msg["id"]
                    break
        
        logging.info(f"<- [MOCK] Retrieved {len(result)} messages for {agent_id}")
        return result
    
    def _get_messages_redis(self, agent_id: str, limit: int, message_types: Optional[List[MessageType]], 
                           last_id: str, block_ms: int) -> List[AgentMessage]:
        """Get messages from Redis Streams"""
        # Read from Redis stream
        try:
            response = self.redis_client.xread(
                {self.message_stream: last_id}, 
                count=limit, 
                block=block_ms
            )
        except redis.ResponseError:
            # If stream doesn't exist yet, return empty
            return []
        
        if not response:
            return []
        
        messages = []
        for stream_name, entries in response:
            for msg_id, msg_data in entries:
                try:
                    # Parse message data back to AgentMessage
                    content = json.loads(msg_data.get("content", "{}"))
                    
                    # Check if message is for this agent (direct or broadcast)
                    to_agent = msg_data.get("to_agent")
                    if to_agent and to_agent != agent_id:
                        continue  # Skip messages not for this agent
                    
                    # Check message type filter
                    message_type = MessageType(msg_data.get("message_type"))
                    if message_types and message_type not in message_types:
                        continue
                    
                    # Check if message has expired
                    expires_at = msg_data.get("expires_at")
                    if expires_at and expires_at != "":
                        expire_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        if datetime.now(timezone.utc) > expire_time:
                            continue
                    
                    # Create AgentMessage object
                    message = AgentMessage(
                        message_id=msg_data.get("message_id"),
                        from_agent=msg_data.get("from_agent"),
                        to_agent=to_agent if to_agent else None,
                        message_type=message_type,
                        content=content,
                        parent_message_id=msg_data.get("parent_message_id") if msg_data.get("parent_message_id") else None,
                        priority=MessagePriority(int(msg_data.get("priority", MessagePriority.MEDIUM.value))),
                        status=msg_data.get("status", "pending"),
                        retry_count=int(msg_data.get("retry_count", 0)),
                        max_retries=int(msg_data.get("max_retries", 3)),
                        created_at=msg_data.get("created_at"),
                        expires_at=expires_at if expires_at else None
                    )
                    
                    # Add Redis stream ID for tracking
                    message.stream_id = msg_id
                    messages.append(message)
                    
                except Exception as e:
                    logging.error(f"Failed to parse message {msg_id}: {e}")
                    continue
        
        logging.info(f"<- [REDIS] Retrieved {len(messages)} messages for {agent_id}")
        return messages
    
    @trace_func
    def mark_processed(self, message_id: str, agent_id: str, status: str = "processed", 
                      error_message: Optional[str] = None) -> bool:
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
            if self.use_mock:
                return self._mark_processed_mock(message_id, agent_id, status, error_message)
            else:
                return self._mark_processed_redis(message_id, agent_id, status, error_message)
        except Exception as e:
            logging.error(f"Failed to mark message {message_id} as processed: {e}")
            return False
    
    def _mark_processed_mock(self, message_id: str, agent_id: str, status: str, error_message: Optional[str]) -> bool:
        """Mark message as processed in mock mode"""
        for mock_msg in self.mock_messages:
            message = mock_msg["data"]
            if message.message_id == message_id:
                message.status = status
                message.processed_at = datetime.now(timezone.utc).isoformat()
                if error_message:
                    message.content['error_message'] = error_message
                
                logging.info(f"OK [MOCK] Marked message {message_id} as {status}")
                return True
        
        logging.warning(f"Message {message_id} not found for processing")
        return False
    
    def _mark_processed_redis(self, message_id: str, agent_id: str, status: str, error_message: Optional[str]) -> bool:
        """Mark message as processed in Redis"""
        # In Redis Streams, we can't modify existing messages
        # Instead, we add a status update message to track processing
        status_data = {
            "type": "message_status",
            "original_message_id": message_id,
            "agent_id": agent_id,
            "status": status,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "error_message": error_message or ""
        }
        
        try:
            # Add status update to a separate stream
            status_stream = f"{self.message_stream}_status"
            self.redis_client.xadd(status_stream, status_data)
            
            # For efficiency, we could also delete the original message if fully processed
            # But keeping it for audit trail for now
            
            logging.info(f"OK [REDIS] Marked message {message_id} as {status}")
            
            # Optional file logging
            processing_time = 0  # Could calculate actual processing time if tracked
            log_message_processed(message_id, "", agent_id, "", processing_time)
            
            return True
        except Exception as e:
            logging.error(f"Failed to mark message as processed: {e}")
            return False
    
    @trace_func
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an agent"""
        if self.use_mock:
            return self.mock_agents.get(agent_id)
        else:
            # Read latest heartbeat from heartbeat stream
            try:
                response = self.redis_client.xrevrange(self.heartbeat_stream, count=1)
                if response:
                    stream_id, data = response[0]
                    if data.get("agent_id") == agent_id:
                        return {
                            "agent_id": data.get("agent_id"),
                            "status": data.get("status"),
                            "last_heartbeat": data.get("timestamp"),
                            "current_tasks": int(data.get("current_tasks", 0))
                        }
                return None
            except Exception as e:
                logging.error(f"Failed to get agent status: {e}")
                return None
    
    @trace_func
    def update_agent_heartbeat(self, agent_id: str, status_info: Dict[str, Any]) -> bool:
        """Update agent heartbeat and status"""
        try:
            if self.use_mock:
                self.mock_agents[agent_id] = {
                    **status_info,
                    'last_heartbeat': datetime.now(timezone.utc).isoformat()
                }
                logging.info(f"HEARTBEAT [MOCK] Updated heartbeat for {agent_id}")
                return True
            else:
                # Add heartbeat to Redis stream
                heartbeat_data = {
                    "agent_id": agent_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **{k: str(v) for k, v in status_info.items()}
                }
                
                self.redis_client.xadd(self.heartbeat_stream, heartbeat_data)
                
                # Trim heartbeat stream to keep only recent entries (last 1000)
                self.redis_client.xtrim(self.heartbeat_stream, maxlen=1000, approximate=True)
                
                logging.info(f"HEARTBEAT [REDIS] Updated heartbeat for {agent_id}")
                return True
        except Exception as e:
            logging.error(f"Failed to update heartbeat for {agent_id}: {e}")
            return False
    
    @trace_func
    def cleanup_expired_messages(self) -> int:
        """Clean up expired and old processed messages"""
        try:
            if self.use_mock:
                initial_count = len(self.mock_messages)
                now = datetime.now(timezone.utc)
                
                # Remove expired and old processed messages
                self.mock_messages = [
                    mock_msg for mock_msg in self.mock_messages
                    if not (mock_msg["data"].is_expired() or 
                           (mock_msg["data"].status == "processed" and 
                            (now - mock_msg["timestamp"]).days > 7))
                ]
                
                cleaned = initial_count - len(self.mock_messages)
                logging.info(f"CLEANUP [MOCK] Cleaned up {cleaned} expired/processed messages")
                return cleaned
            else:
                # Trim Redis streams to prevent infinite growth
                # Keep last 10,000 messages (approximately)
                trimmed = 0
                
                try:
                    # Trim main message stream
                    old_len = self.redis_client.xlen(self.message_stream)
                    self.redis_client.xtrim(self.message_stream, maxlen=10000, approximate=True)
                    new_len = self.redis_client.xlen(self.message_stream)
                    trimmed += (old_len - new_len)
                    
                    # Trim status stream
                    status_stream = f"{self.message_stream}_status"
                    old_len = self.redis_client.xlen(status_stream)
                    self.redis_client.xtrim(status_stream, maxlen=5000, approximate=True)
                    new_len = self.redis_client.xlen(status_stream)
                    trimmed += (old_len - new_len)
                    
                except redis.ResponseError:
                    # Streams might not exist yet
                    pass
                
                logging.info(f"CLEANUP [REDIS] Cleaned up {trimmed} old messages")
                return trimmed
        except Exception as e:
            logging.error(f"Failed to cleanup messages: {e}")
            return 0
    
    @trace_func
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the message queue"""
        if self.use_mock:
            pending = len([mock_msg for mock_msg in self.mock_messages if mock_msg["data"].status == "pending"])
            processed = len([mock_msg for mock_msg in self.mock_messages if mock_msg["data"].status == "processed"])
            failed = len([mock_msg for mock_msg in self.mock_messages if mock_msg["data"].status == "failed"])
            
            return {
                "mode": "mock",
                "total_messages": len(self.mock_messages),
                "pending": pending,
                "processed": processed,
                "failed": failed,
                "active_agents": len(self.mock_agents)
            }
        else:
            try:
                # Get Redis stream info
                stream_info = self.redis_client.xinfo_stream(self.message_stream)
                heartbeat_info = self.redis_client.xinfo_stream(self.heartbeat_stream)
                
                # Safely get groups count
                groups = stream_info.get("groups", [])
                groups_count = len(groups) if isinstance(groups, list) else groups if isinstance(groups, int) else 0
                
                return {
                    "mode": "redis",
                    "redis_url": self.redis_url,
                    "message_stream_length": stream_info.get("length", 0),
                    "heartbeat_stream_length": heartbeat_info.get("length", 0),
                    "first_message_id": stream_info.get("first-entry", [None])[0],
                    "last_message_id": stream_info.get("last-entry", [None])[0],
                    "consumer_groups": groups_count,
                }
            except redis.ResponseError:
                # Streams might not exist yet
                return {
                    "mode": "redis",
                    "redis_url": self.redis_url,
                    "message_stream_length": 0,
                    "heartbeat_stream_length": 0,
                    "status": "streams_not_created_yet"
                }
            except Exception as e:
                return {
                    "mode": "redis",
                    "error": str(e),
                    "status": "error_getting_stats"
                }
    
    @trace_func
    def get_last_message_id(self, agent_id: str) -> str:
        """Get the last message ID processed by an agent (for continuous reading)"""
        if self.use_mock:
            return self.mock_last_ids.get(agent_id, "0-0")
        else:
            # In production, you might want to store this in Redis
            # For now, return the latest ID in the stream
            try:
                info = self.redis_client.xinfo_stream(self.message_stream)
                last_entry = info.get("last-entry")
                if last_entry:
                    return last_entry[0]  # Return the ID part
                return "0-0"
            except redis.ResponseError:
                return "0-0"
    
    @trace_func
    def is_connected(self) -> bool:
        """Check if the queue manager is connected and operational"""
        if self.use_mock:
            return True
        else:
            try:
                self.redis_client.ping()
                return True
            except:
                return False


# Convenience functions for common operations
@trace_func
def create_simple_queue_manager(redis_url: Optional[str] = None) -> MessageQueueManager:
    """Create a message queue manager with automatic configuration"""
    return MessageQueueManager(redis_url=redis_url)


@trace_func
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


@trace_func
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
