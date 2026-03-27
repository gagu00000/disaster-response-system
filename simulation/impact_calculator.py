"""
Impact Calculator Module
Computes the impact of resource allocations on zone states and generates performance metrics.
"""
import numpy as np


class ImpactCalculator:
    """
    Calculates the impact of resource allocations and computes
    performance metrics for the simulation.
    """

    @staticmethod
    def compute_response_coverage(zones: list) -> float:
        """
        Compute average response coverage across all zones.
        Coverage = resources_received / initial_demand (capped at 1.0).
        Target: > 0.70
        """
        coverages = []
        for z in zones:
            if z["initial_demand"] > 0:
                coverage = min(1.0, z["cumulative_resources_received"] / (z["initial_demand"] * 1.5))
            else:
                coverage = 1.0
            coverages.append(coverage)
        return round(np.mean(coverages), 4) if coverages else 0.0

    @staticmethod
    def compute_gini_coefficient(allocations: list) -> float:
        """
        Compute Gini coefficient for resource distribution fairness.
        0 = perfect equality, 1 = perfect inequality.
        Target: < 0.30
        """
        if not allocations or all(a == 0 for a in allocations):
            return 0.0
        sorted_alloc = sorted(allocations)
        n = len(sorted_alloc)
        total = sum(sorted_alloc)
        if total == 0:
            return 0.0
        cumulative = np.cumsum(sorted_alloc)
        gini = (2.0 * sum((i + 1) * sorted_alloc[i] for i in range(n))) / (n * total) - (n + 1) / n
        return round(max(0, gini), 4)

    @staticmethod
    def compute_total_cost(allocations: dict, zones: list) -> float:
        """
        Compute total operational cost. Harder-to-access zones cost more.
        Cost per unit = base_cost * (10 / accessibility).
        """
        total_cost = 0.0
        zone_map = {z["name"]: z for z in zones}
        base_cost = 1.0
        for zone_name, amount in allocations.items():
            if zone_name in zone_map:
                accessibility = max(0.5, zone_map[zone_name]["accessibility"])
                cost_multiplier = 10.0 / accessibility
                total_cost += amount * base_cost * cost_multiplier
        return round(total_cost, 2)

    @staticmethod
    def compute_avg_resilience(zones: list) -> float:
        """
        Compute average resilience index across all zones.
        Target: > 0.60
        """
        if not zones:
            return 0.0
        return round(np.mean([z["resilience_index"] for z in zones]), 4)

    @staticmethod
    def compute_avg_severity(zones: list) -> float:
        """
        Compute average current severity across all zones.
        Target end-state: < 3.0
        """
        if not zones:
            return 0.0
        return round(np.mean([z["current_severity"] for z in zones]), 4)

    @staticmethod
    def compute_resource_utilization(total_allocated: float, total_available: float) -> float:
        """
        Resource utilization rate.
        Target: > 0.90
        """
        if total_available <= 0:
            return 0.0
        return round(min(1.0, total_allocated / total_available), 4)

    @staticmethod
    def compute_min_coverage_ratio(zones: list) -> float:
        """
        Minimum coverage ratio across all zones (worst-served zone).
        Target: > 0.40
        """
        ratios = []
        for z in zones:
            if z["initial_demand"] > 0:
                ratio = z["cumulative_resources_received"] / (z["initial_demand"] * 1.5)
            else:
                ratio = 1.0
            ratios.append(ratio)
        return round(min(ratios), 4) if ratios else 0.0

    @staticmethod
    def compute_all_metrics(zones: list, allocations: dict, total_available: float) -> dict:
        """Compute all performance metrics for a time step."""
        zone_alloc_values = list(allocations.values()) if allocations else []
        total_allocated = sum(zone_alloc_values)

        return {
            "response_coverage": ImpactCalculator.compute_response_coverage(zones),
            "gini_coefficient": ImpactCalculator.compute_gini_coefficient(zone_alloc_values),
            "total_cost": ImpactCalculator.compute_total_cost(allocations, zones),
            "avg_resilience": ImpactCalculator.compute_avg_resilience(zones),
            "avg_severity": ImpactCalculator.compute_avg_severity(zones),
            "resource_utilization": ImpactCalculator.compute_resource_utilization(total_allocated, total_available),
            "min_coverage_ratio": ImpactCalculator.compute_min_coverage_ratio(zones),
            "total_allocated": round(total_allocated, 2),
            "total_available": round(total_available, 2)
        }
