"""Query complexity analysis module."""

import re
from typing import Dict
import numpy as np


class QueryAnalyzer:
    """Analyzes incoming queries to determine complexity and required capabilities."""
    
    COMPLEXITY_PATTERNS = {
        'simple': [
            r'\b(hello|hi|thanks|help|what|how)\b',
            r'[?][\s]*$',
            r'\b(yes|no|ok|sure)\b'
        ],
        'medium': [
            r'\b(explain|describe|compare|analyze|summarize)\b',
            r'\b(step|process|procedure|method)\b',
            r'[\d]{3,}'  # Lists, numbered items
        ],
        'complex': [
            r'\b(reason|argument|hypothesis|critique|evaluate)\b',
            r'\b(comprehensive|detailed|in-depth|thorough)\b',
            r'\b(proof|derivation|calculation)\b',
            r'(\w{15,}\s){3,}'  # Long words indicate technical content
        ]
    }
    
    def analyze(self, query: str) -> float:
        """
        Analyze query and return complexity score (0.0 - 1.0).
        
        Higher scores indicate more complex queries requiring better models.
        """
        query_lower = query.lower()
        
        # Score each pattern category
        simple_score = self._count_matches(query_lower, self.COMPLEXITY_PATTERNS['simple'])
        medium_score = self._count_matches(query_lower, self.COMPLEXITY_PATTERNS['medium'])
        complex_score = self._count_matches(query_lower, self.COMPLEXITY_PATTERNS['complex'])
        
        # Normalize scores
        total_patterns = sum([
            len(p) for p in self.COMPLEXITY_PATTERNS.values()
        ])
        
        # Base complexity from query length
        length_factor = min(len(query) / 500, 1.0)  # Cap at 500 chars
        
        # Final weighted score
        complexity = (
            (simple_score / total_patterns) * 0.2 +
            (medium_score / total_patterns) * 0.5 +
            (complex_score / total_patterns) * 0.3 +
            length_factor * 0.3
        )
        
        return round(min(complexity, 1.0), 2)
    
    def _count_matches(self, text: str, patterns: list) -> int:
        """Count how many patterns match the text."""
        count = 0
        for pattern in patterns:
            if re.search(pattern, text):
                count += 1
        return count
    
    def get_required_threshold(self, complexity_score: float) -> float:
        """Map complexity to minimum accuracy threshold."""
        if complexity_score < 0.3:
            return 0.75  # Simple queries, lower threshold
        elif complexity_score < 0.6:
            return 0.85  # Medium complexity
        else:
            return 0.95  # High complexity needs high accuracy
