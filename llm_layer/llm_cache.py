"""
LLM Cache Module
Caches LLM responses to avoid redundant generation.
Per Section 25.4.
"""
import hashlib
import json
import os


class LLMCache:
    """
    Caches LLM responses keyed by (scenario_id, time_step, allocation_hash).
    Supports explanation, query, and report caching.
    """

    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "llm_cache"
        )
        self.memory_cache = {}
        os.makedirs(self.cache_dir, exist_ok=True)

    def _make_key(self, prefix: str, **kwargs) -> str:
        """Generate a cache key from prefix and kwargs."""
        data_str = json.dumps(kwargs, sort_keys=True, default=str)
        hash_val = hashlib.md5(data_str.encode()).hexdigest()[:12]
        return f"{prefix}_{hash_val}"

    def get_explanation(self, scenario_id: str, time_step: int, allocation: dict) -> str:
        """Retrieve cached explanation."""
        key = self._make_key("explain", scenario=scenario_id, step=time_step,
                              alloc=str(sorted(allocation.items())))
        return self.memory_cache.get(key)

    def set_explanation(self, scenario_id: str, time_step: int, allocation: dict, response: str):
        """Cache an explanation."""
        key = self._make_key("explain", scenario=scenario_id, step=time_step,
                              alloc=str(sorted(allocation.items())))
        self.memory_cache[key] = response

    def get_query(self, question: str) -> str:
        """Retrieve cached query response (exact match)."""
        key = self._make_key("query", q=question.strip().lower())
        return self.memory_cache.get(key)

    def set_query(self, question: str, response: str):
        """Cache a query response."""
        key = self._make_key("query", q=question.strip().lower())
        self.memory_cache[key] = response

    def get_report(self, scenario_id: str, run_hash: str) -> str:
        """Retrieve cached report."""
        key = self._make_key("report", scenario=scenario_id, run=run_hash)
        return self.memory_cache.get(key)

    def set_report(self, scenario_id: str, run_hash: str, report: str):
        """Cache a report."""
        key = self._make_key("report", scenario=scenario_id, run=run_hash)
        self.memory_cache[key] = report

    def clear(self):
        """Clear all cached responses (on new simulation start)."""
        self.memory_cache.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "entries": len(self.memory_cache),
            "types": {
                "explanations": len([k for k in self.memory_cache if k.startswith("explain_")]),
                "queries": len([k for k in self.memory_cache if k.startswith("query_")]),
                "reports": len([k for k in self.memory_cache if k.startswith("report_")])
            }
        }
