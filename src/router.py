"""Main routing engine for Model Router/Cost Optimizer."""

import os
import yaml
import asyncio
from typing import Dict, List, Optional
from loguru import logger
from datetime import datetime

from .analyzer import QueryAnalyzer
from .model_registry import ModelRegistry
from .accuracy_monitor import AccuracyMonitor
from .cost_tracker import CostTracker


class ModelRouter:
    """Core routing engine that selects optimal model for each query."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.analyzer = QueryAnalyzer()
        self.model_registry = ModelRegistry(self.config["models"])
        self.accuracy_monitor = AccuracyMonitor(
            window_size=self.config["monitoring"]["accuracy_window_size"]
        )
        self.cost_tracker = CostTracker()
        
        logger.info("ModelRouter initialized successfully")
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def route_query(
        self, 
        query: str, 
        accuracy_threshold: Optional[float] = None
    ) -> Dict:
        """
        Route a query to the optimal model based on cost and accuracy.
        
        Args:
            query: The user's input text
            accuracy_threshold: Minimum accuracy requirement (uses default if None)
            
        Returns:
            Dictionary with selected model, cost estimate, and metadata
        """
        # Step 1: Analyze query complexity
        complexity_score = self.analyzer.analyze(query)
        logger.debug(f"Query complexity score: {complexity_score}")
        
        # Step 2: Determine minimum accuracy threshold
        if accuracy_threshold is None:
            accuracy_threshold = self.config["routing"]["global_min_accuracy"]
        
        # Step 3: Get qualified models above threshold
        candidates = await self._get_qualified_models(
            complexity_score, 
            accuracy_threshold
        )
        
        if not candidates:
            logger.warning("No qualified models found, using fallback")
            candidates = await self._get_fallback_models()
        
        # Step 4: Select cheapest viable option
        selected_model = self._select_cheapest(candidates)
        
        # Step 5: Calculate cost estimate
        estimated_tokens = self._estimate_tokens(query)
        estimated_cost = self._calculate_cost(selected_model, estimated_tokens)
        
        result = {
            "selected_model": selected_model["name"],
            "model_endpoint": selected_model["endpoint"],
            "estimated_tokens_input": estimated_tokens.get("input", 0),
            "estimated_tokens_output": estimated_tokens.get("output", 0),
            "estimated_cost_usd": estimated_cost,
            "accuracy_threshold_used": accuracy_threshold,
            "routing_timestamp": datetime.utcnow().isoformat(),
            "complexity_score": complexity_score
        }
        
        logger.info(f"Routed query to {selected_model['name']} | Cost: ${estimated_cost}")
        return result
    
    async def execute_query_with_model(
        self, 
        query: str, 
        model_name: str,
        temperature: float = 0.7
    ) -> Dict:
        """Execute query against selected model and track results."""
        import aiohttp
        
        model_config = self.model_registry.get_model_by_name(model_name)
        
        headers = {
            "Authorization": f"Bearer {os.getenv(self.config['fireworks']['api_key_env'])}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_config["endpoint"],
            "messages": [{"role": "user", "content": query}],
            "temperature": temperature,
            "max_tokens": 1024
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.config["fireworks"]["base_url"] + "/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                
        # Track accuracy (simple heuristic - would be replaced with actual eval)
        tokens_used = result.get("usage", {})
        input_tokens = tokens_used.get("prompt_tokens", 0)
        output_tokens = tokens_used.get("completion_tokens", 0)
        
        actual_cost = self._calculate_actual_cost(
            model_config, input_tokens, output_tokens
        )
        
        self.cost_tracker.log_usage(
            model=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=actual_cost
        )
        
        return {
            "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
            "tokens_used": input_tokens + output_tokens,
            "actual_cost_usd": actual_cost,
            "model_used": model_name
        }
    
    async def _get_qualified_models(
        self, 
        complexity_score: float, 
        accuracy_threshold: float
    ) -> List[Dict]:
        """Get models that meet accuracy requirements."""
        all_models = self.model_registry.get_all_models()
        qualified = []
        
        for model in all_models:
            model_accuracy = self.accuracy_monitor.get_model_accuracy(
                model["name"]
            )
            
            if model_accuracy >= model["min_accuracy_threshold"]:
                if model["min_accuracy_threshold"] >= accuracy_threshold:
                    qualified.append(model)
        
        # Sort by effective cost
        qualified.sort(key=lambda m: m["price_per_million_input"])
        return qualified
    
    async def _get_fallback_models(self) -> List[Dict]:
        """Return fallback models if no qualified models exist."""
        fallback_name = self.config["routing"]["default_fallback_model"]
        model = self.model_registry.get_model_by_endpoint(fallback_name)
        return [model] if model else []
    
    def _select_cheapest(self, models: List[Dict]) -> Dict:
        """Select the cheapest model from candidates."""
        return models[0] if models else {}
    
    def _estimate_tokens(self, query: str) -> Dict:
        """Estimate input and output token count."""
        # Simple word-based estimation (replace with tokenizer for accuracy)
        words = len(query.split())
        input_tokens = int(words * 1.3)  # ~1.3 tokens per word average
        
        return {
            "input": input_tokens,
            "output": int(input_tokens * self.config["token_estimation"]["output_multiplier"])
        }
    
    def _calculate_cost(self, model: Dict, tokens: Dict) -> float:
        """Calculate estimated cost in USD."""
        input_cost = (tokens["input"] / 1_000_000) * model["price_per_million_input"]
        output_cost = (tokens["output"] / 1_000_000) * model["price_per_million_output"]
        return round(input_cost + output_cost, 6)
    
    def _calculate_actual_cost(self, model: Dict, input_tokens: int, output_tokens: int) -> float:
        """Calculate actual cost from executed request."""
        input_cost = (input_tokens / 1_000_000) * model["price_per_million_input"]
        output_cost = (output_tokens / 1_000_000) * model["price_per_million_output"]
        return round(input_cost + output_cost, 6)
    
    def update_accuracy(self, model_name: str, success: bool):
        """Update accuracy tracking after query execution."""
        self.accuracy_monitor.record_result(model_name, success)
    
    def get_metrics(self) -> Dict:
        """Get current routing metrics."""
        return {
            "total_queries_routed": self.cost_tracker.total_queries,
            "total_cost_saved_vs_baseline": self.cost_tracker.calculate_savings(),
            "avg_cost_per_query": self.cost_tracker.get_average_cost(),
            "model_accuracy_rates": self.accuracy_monitor.get_all_accuracies(),
            "active_models": len(self.model_registry.get_all_models()),
            "routing_distribution": self.cost_tracker.get_routing_distribution()
        }


# Singleton instance
_router_instance = None

def get_router() -> ModelRouter:
    """Get or create singleton router instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter()
    return _router_instance
