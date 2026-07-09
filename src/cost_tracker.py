"""Cost tracking and analytics."""

from collections import defaultdict
from typing import Dict
from datetime import datetime


class CostTracker:
    """Logs and analyzes token usage and costs."""
    
    def __init__(self):
        self.usage_logs: list = []
        self.routing_counts: Dict[str, int] = defaultdict(int)
        self.total_queries = 0
    
    def log_usage(
        self, 
        model: str, 
        input_tokens: int, 
        output_tokens: int, 
        cost: float
    ):
        """Log a single query's token usage and cost."""
        self.usage_logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": cost
        })
        
        self.routing_counts[model] += 1
        self.total_queries += 1
    
    def calculate_savings(self, baseline_model: str = "llama-v3p1-70b-instruct") -> float:
        """Calculate total savings vs using baseline model for all queries."""
        if not self.usage_logs:
            return 0.0
        
        baseline_rate = 0.90  # $/million tokens for 70B model
        total_tokens = sum(log["total_tokens"] for log in self.usage_logs)
        baseline_cost = (total_tokens / 1_000_000) * baseline_rate
        
        actual_cost = sum(log["cost_usd"] for log in self.usage_logs)
        return round(baseline_cost - actual_cost, 4)
    
    def get_average_cost(self) -> float:
        """Get average cost per query."""
        if not self.usage_logs:
            return 0.0
        total_cost = sum(log["cost_usd"] for log in self.usage_logs)
        return round(total_cost / len(self.usage_logs), 6)
    
    def get_routing_distribution(self) -> Dict[str, float]:
        """Get percentage of queries routed to each model."""
        if self.total_queries == 0:
            return {}
        
        return {
            model: round(count / self.total_queries * 100, 2)
            for model, count in self.routing_counts.items()
        }
    
    def get_recent_usage(self, limit: int = 10) -> list:
        """Get recent usage logs."""
        return self.usage_logs[-limit:]
