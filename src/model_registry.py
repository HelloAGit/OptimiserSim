"""Model pool registry and management."""

from typing import Dict, List, Optional


class ModelRegistry:
    """Maintains list of available model endpoints and their configurations."""
    
    def __init__(self, models_config: List[Dict]):
        self.models = models_config
        self.model_index = {m["name"]: m for m in models_config}
    
    def get_all_models(self) -> List[Dict]:
        """Return all registered models sorted by priority."""
        return sorted(self.models, key=lambda m: m["priority"])
    
    def get_model_by_name(self, name: str) -> Optional[Dict]:
        """Get model configuration by friendly name."""
        return self.model_index.get(name)
    
    def get_model_by_endpoint(self, endpoint: str) -> Optional[Dict]:
        """Get model configuration by API endpoint."""
        for model in self.models:
            if model["endpoint"] == endpoint:
                return model
        return None
    
    def update_pricing(self, model_name: str, new_price: float):
        """Update pricing for a model (for dynamic price updates)."""
        if model_name in self.model_index:
            self.model_index[model_name]["price_per_million_input"] = new_price
            self.model_index[model_name]["price_per_million_output"] = new_price
