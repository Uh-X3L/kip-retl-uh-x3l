#!/usr/bin/env python3
"""
Simple Agent Communication Demo
===============================

Basic Redis-based agent messaging demo.
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.agent_communication.message_protocol import AgentMessage, MessageType, MessagePriority
from helpers.agent_communication.queue_manager import MessageQueueManager

def main():
    print("=== Agent Communication Demo ===")
    
    # Initialize (try Redis first, fall back to mock if unavailable)
    try:
        queue = MessageQueueManager(use_mock=False)
        print("✓ Connected to Redis!")
    except Exception as e:
        print(f"⚠ Redis unavailable ({e}), using mock mode")
        queue = MessageQueueManager(use_mock=True)
    
    print("1. Sending messages between agents...")
    
    # Agent A sends task to Agent B
    task_msg = AgentMessage(
        message_id=f"task_{int(time.time())}",
        from_agent="agent_a",
        to_agent="agent_b",
        message_type=MessageType.TASK_REQUEST,
        content={"task": "process_data", "file": "data.csv"},
        priority=MessagePriority.HIGH
    )
    
    success = queue.send_message(task_msg)
    print(f"   Task sent: {success}")
    
    # Agent B sends status update
    status_msg = AgentMessage(
        message_id=f"status_{int(time.time())}",
        from_agent="agent_b", 
        to_agent="agent_a",
        message_type=MessageType.STATUS_UPDATE,
        content={"status": "processing", "progress": 0.5}
    )
    
    success = queue.send_message(status_msg)
    print(f"   Status sent: {success}")
    
    print("\n2. Agent B receiving messages...")
    messages = queue.get_messages("agent_b", limit=5)
    
    for msg in messages:
        print(f"   From: {msg.from_agent}")
        print(f"   Type: {msg.message_type.value}")
        print(f"   Content: {msg.content}")
        
        # Mark as processed
        queue.mark_processed(msg.message_id, "agent_b")
        print(f"   Marked processed: {msg.message_id}")
    
    print("\n=== Demo Complete ===")
    if not queue.use_mock:
        print("✓ Successfully used Redis Streams for messaging!")
        print("Check Redis: docker exec redis-agent-comm redis-cli XLEN agent_messages")
    else:
        print("Used mock mode - start Redis to use real streams:")
        print("docker run -d --name redis-agent-comm -p 6379:6379 redis:7-alpine")

if __name__ == "__main__":
    main()
