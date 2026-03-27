"""
Metrics Display Module
Generates KPI cards and summary displays for the dashboard footer.
"""


class MetricsDisplay:
    """Generates formatted metrics for dashboard display."""

    @staticmethod
    def get_kpi_cards(metrics: dict) -> list:
        """
        Generate KPI card data for the dashboard footer.
        Returns list of dicts with label, value, target, status.
        """
        cards = []

        # Response Coverage
        coverage = metrics.get("response_coverage", 0)
        cards.append({
            "label": "Avg Response Coverage",
            "value": f"{coverage:.1%}",
            "target": "> 70%",
            "status": "good" if coverage > 0.70 else "warning" if coverage > 0.50 else "bad",
            "icon": "🚀"
        })

        # Gini Coefficient
        gini = metrics.get("gini_coefficient", 0)
        cards.append({
            "label": "Gini Coefficient",
            "value": f"{gini:.3f}",
            "target": "< 0.30",
            "status": "good" if gini < 0.30 else "warning" if gini < 0.40 else "bad",
            "icon": "⚖️"
        })

        # Total Cost
        cost = metrics.get("total_cost", 0)
        cards.append({
            "label": "Total Cost",
            "value": f"{cost:.1f}",
            "target": "Minimize",
            "status": "good" if cost < 500 else "warning" if cost < 1000 else "bad",
            "icon": "💰"
        })

        # Resilience Index
        resilience = metrics.get("avg_resilience", 0)
        cards.append({
            "label": "Resilience Index",
            "value": f"{resilience:.3f}",
            "target": "> 0.60",
            "status": "good" if resilience > 0.60 else "warning" if resilience > 0.40 else "bad",
            "icon": "🛡️"
        })

        # Average Severity
        severity = metrics.get("avg_severity", 0)
        cards.append({
            "label": "Avg Severity",
            "value": f"{severity:.2f}/10",
            "target": "< 3.0 (end)",
            "status": "good" if severity < 3.0 else "warning" if severity < 5.0 else "bad",
            "icon": "🔥"
        })

        # Resource Utilization
        util = metrics.get("resource_utilization", 0)
        cards.append({
            "label": "Resource Utilization",
            "value": f"{util:.1%}",
            "target": "> 90%",
            "status": "good" if util > 0.90 else "warning" if util > 0.70 else "bad",
            "icon": "📦"
        })

        return cards

    @staticmethod
    def get_performance_scorecard(metrics_history: list) -> dict:
        """Generate a traffic-light performance scorecard."""
        if not metrics_history:
            return {"scores": [], "overall": "N/A"}

        # Average across all steps
        avg_metrics = {}
        keys = ["response_coverage", "gini_coefficient", "total_cost", "avg_resilience", "avg_severity"]
        for key in keys:
            values = [m.get(key, 0) for m in metrics_history]
            avg_metrics[key] = sum(values) / len(values)

        scores = []
        scores.append({
            "metric": "Response Coverage",
            "value": avg_metrics["response_coverage"],
            "target": 0.70,
            "status": "🟢" if avg_metrics["response_coverage"] > 0.70 else "🟡" if avg_metrics["response_coverage"] > 0.50 else "🔴"
        })
        scores.append({
            "metric": "Fairness (Gini)",
            "value": avg_metrics["gini_coefficient"],
            "target": 0.30,
            "status": "🟢" if avg_metrics["gini_coefficient"] < 0.30 else "🟡" if avg_metrics["gini_coefficient"] < 0.40 else "🔴"
        })
        scores.append({
            "metric": "Avg Severity Reduction",
            "value": avg_metrics["avg_severity"],
            "target": 3.0,
            "status": "🟢" if avg_metrics["avg_severity"] < 3.0 else "🟡" if avg_metrics["avg_severity"] < 5.0 else "🔴"
        })
        scores.append({
            "metric": "Resilience",
            "value": avg_metrics["avg_resilience"],
            "target": 0.60,
            "status": "🟢" if avg_metrics["avg_resilience"] > 0.60 else "🟡" if avg_metrics["avg_resilience"] > 0.40 else "🔴"
        })

        greens = sum(1 for s in scores if s["status"] == "🟢")
        overall = "Excellent" if greens == 4 else "Good" if greens >= 3 else "Fair" if greens >= 2 else "Needs Improvement"

        return {"scores": scores, "overall": overall}
