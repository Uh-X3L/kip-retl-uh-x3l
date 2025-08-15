"""
Agent Registry - Centralized management and reuse system for Azure AI agents
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent
from .web_research_analyst import WebResearchAnalyst
from .project_planner import ProjectPlanner
from .devops_agent import DevOpsAgent
from .worker_agent import WorkerAgent
from .testing_agent import TestingAgent
from .documentation_agent import DocumentationAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Centralized registry for managing and reusing Azure AI agents.
    Provides intelligent agent selection, lifecycle management, and performance tracking.
    """
    
    def __init__(self, project_client):
        """Initialize the agent registry."""
        self.project_client = project_client
        self.registry_path = "helpers/config/agent_registry.json"
        self.config_path = "helpers/config/agent_config.json"
        self._load_configuration()
    
    def _load_configuration(self):
        """Load registry configuration."""
        default_config = {
            "agent_cleanup_days": 7,
            "max_agents_per_type": 3,
            "reuse_threshold_hours": 1,
            "performance_tracking": True,
            "auto_cleanup": True
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self._save_configuration()
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}")
            self.config = default_config
    
    def _save_configuration(self):
        """Save registry configuration."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save configuration: {e}")
    
    def get_agent(self, agent_type: str, **kwargs) -> BaseAgent:
        """
        Get or create an agent of the specified type with intelligent reuse.
        
        Args:
            agent_type: Type of agent needed
            **kwargs: Additional parameters for agent creation
        
        Returns:
            Agent instance (reused or newly created)
        """
        agent_classes = {
            "web_research_analyst": WebResearchAnalyst,
            "project_planner": ProjectPlanner,
            "devops_agent": DevOpsAgent,
            "researcher": WebResearchAnalyst,
            "planner": ProjectPlanner,
            "devops_specialist": DevOpsAgent
        }
        
        agent_class = agent_classes.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Create agent with reuse capabilities
        agent = agent_class(project_client=self.project_client, **kwargs)
        
        # Update registry statistics
        self._update_usage_stats(agent_type, agent.is_reused)
        
        return agent
    
    def _update_usage_stats(self, agent_type: str, was_reused: bool):
        """Update agent usage statistics."""
        try:
            stats = self._load_stats()
            
            if agent_type not in stats:
                stats[agent_type] = {
                    "total_requests": 0,
                    "reuse_count": 0,
                    "creation_count": 0,
                    "last_used": None
                }
            
            stats[agent_type]["total_requests"] += 1
            stats[agent_type]["last_used"] = datetime.now().isoformat()
            
            if was_reused:
                stats[agent_type]["reuse_count"] += 1
            else:
                stats[agent_type]["creation_count"] += 1
            
            self._save_stats(stats)
            
        except Exception as e:
            logger.warning(f"Failed to update usage stats: {e}")
    
    def _load_stats(self) -> Dict:
        """Load usage statistics."""
        stats_path = "helpers/config/agent_stats.json"
        try:
            if os.path.exists(stats_path):
                with open(stats_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except:
            return {}
    
    def _save_stats(self, stats: Dict):
        """Save usage statistics."""
        stats_path = "helpers/config/agent_stats.json"
        try:
            os.makedirs(os.path.dirname(stats_path), exist_ok=True)
            with open(stats_path, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save stats: {e}")
    
    def list_active_agents(self) -> List[Dict]:
        """List all active agents in the registry."""
        try:
            if not os.path.exists(self.registry_path):
                return []
                
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
                
            active_agents = [
                agent for agent in registry.get('agents', [])
                if agent.get('status') == 'active'
            ]
            
            return active_agents
            
        except Exception as e:
            logger.warning(f"Failed to list active agents: {e}")
            return []
    
    def get_agent_statistics(self) -> Dict:
        """Get comprehensive agent statistics."""
        try:
            stats = self._load_stats()
            registry_stats = self._get_registry_stats()
            
            # Calculate reuse efficiency
            total_requests = sum(stat.get("total_requests", 0) for stat in stats.values())
            total_reuses = sum(stat.get("reuse_count", 0) for stat in stats.values())
            reuse_efficiency = (total_reuses / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "usage_stats": stats,
                "registry_stats": registry_stats,
                "reuse_efficiency": round(reuse_efficiency, 2),
                "total_requests": total_requests,
                "total_reuses": total_reuses,
                "active_agents_count": len(self.list_active_agents())
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def _get_registry_stats(self) -> Dict:
        """Get registry-level statistics."""
        try:
            active_agents = self.list_active_agents()
            
            # Group by agent type
            type_counts = {}
            for agent in active_agents:
                agent_type = agent.get('agent_type', 'unknown')
                type_counts[agent_type] = type_counts.get(agent_type, 0) + 1
            
            # Calculate age distribution
            now = datetime.now()
            age_distribution = {"< 1 hour": 0, "1-24 hours": 0, "1-7 days": 0, "> 7 days": 0}
            
            for agent in active_agents:
                try:
                    created_at = datetime.fromisoformat(agent.get('created_at', now.isoformat()))
                    age = now - created_at
                    
                    if age < timedelta(hours=1):
                        age_distribution["< 1 hour"] += 1
                    elif age < timedelta(days=1):
                        age_distribution["1-24 hours"] += 1
                    elif age < timedelta(days=7):
                        age_distribution["1-7 days"] += 1
                    else:
                        age_distribution["> 7 days"] += 1
                except:
                    pass
            
            return {
                "total_active_agents": len(active_agents),
                "agents_by_type": type_counts,
                "age_distribution": age_distribution
            }
            
        except Exception as e:
            logger.warning(f"Failed to get registry stats: {e}")
            return {}
    
    def cleanup_inactive_agents(self, dry_run: bool = False) -> Dict:
        """
        Clean up inactive agents based on configuration.
        
        Args:
            dry_run: If True, only report what would be cleaned up
        
        Returns:
            Cleanup report
        """
        try:
            if not os.path.exists(self.registry_path):
                return {"message": "No registry file found", "cleaned_count": 0}
                
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
            
            cleanup_threshold = datetime.now() - timedelta(days=self.config.get('agent_cleanup_days', 7))
            
            agents_to_cleanup = []
            cleaned_count = 0
            
            for agent in registry.get('agents', []):
                try:
                    last_used = datetime.fromisoformat(agent.get('last_used', agent.get('created_at')))
                    
                    if last_used < cleanup_threshold:
                        agents_to_cleanup.append({
                            "agent_id": agent.get('agent_id'),
                            "name": agent.get('name'),
                            "last_used": agent.get('last_used'),
                            "age_days": (datetime.now() - last_used).days
                        })
                        
                        if not dry_run:
                            try:
                                # Try to delete the agent from Azure
                                self.project_client.agents.delete_agent(agent.get('agent_id'))
                                agent['status'] = 'deleted'
                                cleaned_count += 1
                                logger.info(f"🗑️ Cleaned up agent: {agent.get('name')} (ID: {agent.get('agent_id')})")
                            except Exception as delete_error:
                                logger.warning(f"Failed to delete agent {agent.get('agent_id')}: {delete_error}")
                                agent['status'] = 'cleanup_failed'
                                
                except Exception as date_error:
                    logger.warning(f"Error processing agent date: {date_error}")
            
            if not dry_run and cleaned_count > 0:
                # Save updated registry
                with open(self.registry_path, 'w') as f:
                    json.dump(registry, f, indent=2)
            
            return {
                "cleanup_threshold": cleanup_threshold.isoformat(),
                "agents_identified": len(agents_to_cleanup),
                "cleaned_count": cleaned_count if not dry_run else 0,
                "dry_run": dry_run,
                "agents_to_cleanup": agents_to_cleanup
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup agents: {e}")
            return {"error": str(e), "cleaned_count": 0}
    
    def optimize_registry(self) -> Dict:
        """Optimize the agent registry for better performance."""
        try:
            optimization_report = {
                "initial_agents": 0,
                "removed_duplicates": 0,
                "marked_inactive": 0,
                "verified_active": 0
            }
            
            if not os.path.exists(self.registry_path):
                return {"message": "No registry file found"}
            
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
            
            agents = registry.get('agents', [])
            optimization_report["initial_agents"] = len(agents)
            
            # Remove duplicates and verify agent existence
            seen_agents = set()
            optimized_agents = []
            
            for agent in agents:
                agent_id = agent.get('agent_id')
                
                # Skip if duplicate
                if agent_id in seen_agents:
                    optimization_report["removed_duplicates"] += 1
                    continue
                
                seen_agents.add(agent_id)
                
                # Verify agent still exists in Azure
                try:
                    self.project_client.agents.get_agent(agent_id)
                    agent['status'] = 'active'
                    optimization_report["verified_active"] += 1
                    optimized_agents.append(agent)
                except:
                    agent['status'] = 'inactive'
                    optimization_report["marked_inactive"] += 1
                    optimized_agents.append(agent)
            
            # Save optimized registry
            registry['agents'] = optimized_agents
            registry['last_optimized'] = datetime.now().isoformat()
            
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            
            logger.info(f"🔧 Optimized agent registry: {optimization_report}")
            return optimization_report
            
        except Exception as e:
            logger.error(f"Failed to optimize registry: {e}")
            return {"error": str(e)}
    
    def generate_usage_report(self) -> str:
        """Generate a comprehensive usage report."""
        try:
            stats = self.get_agent_statistics()
            
            report = "# Agent Registry Usage Report\n\n"
            report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Summary
            report += "## Summary\n"
            report += f"- **Reuse Efficiency:** {stats.get('reuse_efficiency', 0)}%\n"
            report += f"- **Total Requests:** {stats.get('total_requests', 0)}\n"
            report += f"- **Total Reuses:** {stats.get('total_reuses', 0)}\n"
            report += f"- **Active Agents:** {stats.get('active_agents_count', 0)}\n\n"
            
            # Agent Types
            usage_stats = stats.get('usage_stats', {})
            if usage_stats:
                report += "## Agent Type Usage\n"
                for agent_type, type_stats in usage_stats.items():
                    reuse_rate = (type_stats.get('reuse_count', 0) / type_stats.get('total_requests', 1)) * 100
                    report += f"- **{agent_type.title()}:**\n"
                    report += f"  - Requests: {type_stats.get('total_requests', 0)}\n"
                    report += f"  - Reuse Rate: {reuse_rate:.1f}%\n"
                    report += f"  - Last Used: {type_stats.get('last_used', 'N/A')}\n"
                report += "\n"
            
            # Registry Statistics
            registry_stats = stats.get('registry_stats', {})
            if registry_stats:
                report += "## Registry Statistics\n"
                report += f"- **Total Active Agents:** {registry_stats.get('total_active_agents', 0)}\n"
                
                agents_by_type = registry_stats.get('agents_by_type', {})
                if agents_by_type:
                    report += "- **Agents by Type:**\n"
                    for agent_type, count in agents_by_type.items():
                        report += f"  - {agent_type}: {count}\n"
                
                age_dist = registry_stats.get('age_distribution', {})
                if age_dist:
                    report += "- **Age Distribution:**\n"
                    for age_range, count in age_dist.items():
                        report += f"  - {age_range}: {count}\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate usage report: {e}")
            return f"Error generating report: {str(e)}"
