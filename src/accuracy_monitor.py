"""Rolling model-accuracy monitoring."""

from collections import defaultdict, deque
from typing import Deque, Dict


class AccuracyMonitor:
    """Track recent success and failure results for each model."""

    def __init__(
        self,
        window_size: int = 100,
        default_accuracy: float = 1.0,
    ) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be greater than zero")

        if not 0.0 <= default_accuracy <= 1.0:
            raise ValueError("default_accuracy must be between 0 and 1")

        self.window_size = window_size
        self.default_accuracy = default_accuracy
        self._results: Dict[str, Deque[bool]] = defaultdict(
            lambda: deque(maxlen=self.window_size)
        )

    def record_result(self, model_name: str, success: bool) -> None:
        """Record the outcome of one model request."""
        if not model_name:
            raise ValueError("model_name must not be empty")

        self._results[model_name].append(bool(success))

    def get_model_accuracy(self, model_name: str) -> float:
        """Return rolling accuracy for a model."""
        results = self._results.get(model_name)

        if not results:
            return self.default_accuracy

        successful = sum(results)
        return round(successful / len(results), 4)

    def get_all_accuracies(self) -> Dict[str, float]:
        """Return rolling accuracy for every observed model."""
        return {
            model_name: self.get_model_accuracy(model_name)
            for model_name in self._results
        }
