"""
File-based Logging for Agent Communication System
================================================

Optional file-based persistence for agent activities, task history,
and performance metrics. All data is stored as JSON Lines files
organized by date for easy parsing and analysis.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path



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


@trace_class
class AgentFileLogger:
    """Handles file-based logging for agent communication system"""
    
    def __init__(self, base_dir: str = "./logs", enable_logging: bool = False):
        """
        Initialize the file logger.
        
        Args:
            base_dir: Base directory for log files
            enable_logging: Whether to enable file logging (disabled by default)
        """
        self.base_dir = Path(base_dir)
        self.enable_logging = enable_logging
        
        if self.enable_logging:
            self._setup_log_directory()
    
    def _setup_log_directory(self):
        """Create log directory structure"""
        log_date = datetime.now().strftime('%Y-%m-%d')
        self.current_log_dir = self.base_dir / log_date
        self.current_log_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_log_file_path(self, log_type: str) -> Path:
        """Get the path for a specific log type"""
        log_date = datetime.now().strftime('%Y-%m-%d')
        return self.current_log_dir / f"{log_type}_{log_date}.jsonl"
    
    def _write_log_entry(self, log_type: str, entry: Dict[str, Any]):
        """Write a log entry to the appropriate file"""
        if not self.enable_logging:
            return
            
        # Ensure timestamp is included
        if 'timestamp' not in entry:
            entry['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        log_file = self._get_log_file_path(log_type)
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            # Don't let logging errors break the system
            print(f"Warning: Failed to write to log file {log_file}: {e}")
    
    @trace_func
    def log_agent_activity(self, agent_id: str, event: str, data: Optional[Dict[str, Any]] = None):
        """Log agent activity events"""
        entry = {
            'agent_id': agent_id,
            'event': event,
            'data': data or {}
        }
        self._write_log_entry('agent_activity', entry)
    
    @trace_func
    def log_message_audit(self, message_id: str, from_agent: str, to_agent: Optional[str], 
                         message_type: str, event: str, data: Optional[Dict[str, Any]] = None):
        """Log message audit trail"""
        entry = {
            'message_id': message_id,
            'from_agent': from_agent,
            'to_agent': to_agent,
            'message_type': message_type,
            'event': event,
            'data': data or {}
        }
        self._write_log_entry('message_audit', entry)
    
    @trace_func
    def log_task_history(self, task_id: str, agent_id: str, event: str, 
                        data: Optional[Dict[str, Any]] = None):
        """Log task execution history"""
        entry = {
            'task_id': task_id,
            'agent_id': agent_id,
            'event': event,
            'data': data or {}
        }
        self._write_log_entry('task_history', entry)
    
    @trace_func
    def log_performance_metric(self, agent_id: str, metric_type: str, value: float,
                             unit: str, metadata: Optional[Dict[str, Any]] = None):
        """Log performance metrics"""
        entry = {
            'agent_id': agent_id,
            'metric_type': metric_type,
            'value': value,
            'unit': unit,
            'metadata': metadata or {}
        }
        self._write_log_entry('performance', entry)
    
    @trace_func
    def log_error(self, source: str, error_type: str, error_message: str,
                  context: Optional[Dict[str, Any]] = None):
        """Log errors and exceptions"""
        entry = {
            'source': source,
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }
        self._write_log_entry('errors', entry)
    
    @trace_func
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about log files"""
        if not self.enable_logging:
            return {'status': 'disabled'}
        
        stats = {
            'enabled': True,
            'base_dir': str(self.base_dir),
            'current_log_dir': str(self.current_log_dir),
            'log_files': {}
        }
        
        log_types = ['agent_activity', 'message_audit', 'task_history', 'performance', 'errors']
        
        for log_type in log_types:
            log_file = self._get_log_file_path(log_type)
            if log_file.exists():
                stats['log_files'][log_type] = {
                    'path': str(log_file),
                    'size_bytes': log_file.stat().st_size,
                    'line_count': self._count_lines(log_file)
                }
            else:
                stats['log_files'][log_type] = {'exists': False}
        
        return stats
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file efficiently"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    @trace_func
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up log files older than specified days"""
        if not self.enable_logging:
            return
        
        cutoff_date = datetime.now().date()
        
        for date_dir in self.base_dir.iterdir():
            if date_dir.is_dir():
                try:
                    dir_date = datetime.strptime(date_dir.name, '%Y-%m-%d').date()
                    if (cutoff_date - dir_date).days > days_to_keep:
                        # Archive or delete old directory
                        print(f"Cleaning up old log directory: {date_dir}")
                        # For now, just print - implement archival logic as needed
                except ValueError:
                    # Skip directories that don't match date format
                    continue


# Global logger instance
_file_logger = None

@trace_func
def get_file_logger(enable_logging: bool = False) -> AgentFileLogger:
    """Get the global file logger instance"""
    global _file_logger
    if _file_logger is None:
        _file_logger = AgentFileLogger(enable_logging=enable_logging)
    return _file_logger

@trace_func
def enable_file_logging(base_dir: str = "./logs"):
    """Enable file logging globally"""
    global _file_logger
    _file_logger = AgentFileLogger(base_dir=base_dir, enable_logging=True)
    return _file_logger

@trace_func
def disable_file_logging():
    """Disable file logging globally"""
    global _file_logger
    if _file_logger:
        _file_logger.enable_logging = False

# Convenience functions for easy logging
@trace_func
def log_agent_registered(agent_id: str, agent_role: str, capabilities: list):
    """Log agent registration"""
    logger = get_file_logger()
    logger.log_agent_activity(agent_id, 'registered', {
        'agent_role': agent_role,
        'capabilities': capabilities
    })

@trace_func
def log_message_sent(message_id: str, from_agent: str, to_agent: str, message_type: str):
    """Log message sent"""
    logger = get_file_logger()
    logger.log_message_audit(message_id, from_agent, to_agent, message_type, 'sent')

@trace_func
def log_message_processed(message_id: str, from_agent: str, to_agent: str, 
                         message_type: str, processing_time_ms: float):
    """Log message processed"""
    logger = get_file_logger()
    logger.log_message_audit(message_id, from_agent, to_agent, message_type, 'processed', {
        'processing_time_ms': processing_time_ms
    })

@trace_func
def log_task_assigned(task_id: str, agent_id: str, task_type: str, priority: int):
    """Log task assignment"""
    logger = get_file_logger()
    logger.log_task_history(task_id, agent_id, 'assigned', {
        'task_type': task_type,
        'priority': priority
    })

@trace_func
def log_task_completed(task_id: str, agent_id: str, duration_ms: float, success: bool):
    """Log task completion"""
    logger = get_file_logger()
    logger.log_task_history(task_id, agent_id, 'completed', {
        'duration_ms': duration_ms,
        'success': success
    })
