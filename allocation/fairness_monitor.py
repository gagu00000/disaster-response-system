"""
Fairness Monitor Module
Monitors distributional equity using Gini coefficient and triggers reallocation.
Per Section 5.1 Step 4 and Section 12.1 Fairness Metrics.
"""
import numpy as np


class FairnessMonitor:
    """
    Monitors allocation fairness using Gini coefficient and other equity metrics.
    Triggers redistribution when allocations fail fairness thresholds.
    """

    # Fairness thresholds (Section 12.1)
    GINI_THRESHOLD = 0.30          # Gini < 0.30 = fair
    MIN_COVERAGE_THRESHOLD = 0.40  # Every zone should get > 40% of proportional share
    VULNERABILITY_EQUITY_THRESHOLD = 0.25

    @staticmethod
    def compute_gini(allocations: list) -> float:
        """
        Compute Gini coefficient for a list of allocation amounts.
        0 = perfect equality, 1 = perfect inequality.
        """
        if not allocations or all(a == 0 for a in allocations):
            return 0.0

        sorted_alloc = sorted(allocations)
        n = len(sorted_alloc)
        total = sum(sorted_alloc)
        if total == 0:
            return 0.0

        cumulative = 0
        gini_sum = 0
        for i, val in enumerate(sorted_alloc):
            cumulative += val
            gini_sum += (2 * (i + 1) - n - 1) * val

        gini = gini_sum / (n * total)
        return round(max(0, gini), 4)

    @staticmethod
    def compute_need_adjusted_gini(allocations: dict, zones: list) -> float:
        """
        Compute Gini coefficient adjusted for need (severity * population).
        Compares allocation proportions to need proportions.
        """
        zone_map = {z["name"]: z for z in zones}
        needs = []
        allocs = []

        for zone_name, amount in allocations.items():
            if zone_name in zone_map:
                z = zone_map[zone_name]
                need = z["current_severity"] * (z["population"] / 10000)
                needs.append(need)
                allocs.append(amount)

        total_need = sum(needs)
        total_alloc = sum(allocs)

        if total_need == 0 or total_alloc == 0:
            return 0.0

        # Compare allocation ratios to need ratios
        ratios = []
        for need, alloc in zip(needs, allocs):
            need_ratio = need / total_need
            alloc_ratio = alloc / total_alloc
            if need_ratio > 0:
                ratios.append(alloc_ratio / need_ratio)
            else:
                ratios.append(1.0)

        return FairnessMonitor.compute_gini(ratios)

    @staticmethod
    def check_fairness(allocations: dict, zones: list) -> dict:
        """
        Run all fairness checks on an allocation.

        Returns:
            dict with gini, need_adjusted_gini, min_coverage, is_fair, issues
        """
        zone_map = {z["name"]: z for z in zones}
        alloc_values = list(allocations.values())
        total_alloc = sum(alloc_values)

        gini = FairnessMonitor.compute_gini(alloc_values)
        need_gini = FairnessMonitor.compute_need_adjusted_gini(allocations, zones)

        # Check minimum coverage ratio
        min_coverage = 1.0
        coverage_details = {}
        total_pop = sum(z["population"] for z in zones)

        for zone in zones:
            name = zone["name"]
            pop_share = zone["population"] / total_pop if total_pop > 0 else 0
            fair_share = pop_share * total_alloc
            actual = allocations.get(name, 0)
            coverage = actual / fair_share if fair_share > 0 else 1.0
            coverage_details[name] = round(coverage, 4)
            min_coverage = min(min_coverage, coverage)

        # Determine fairness status
        issues = []
        if gini > FairnessMonitor.GINI_THRESHOLD:
            issues.append(f"Gini coefficient ({gini}) exceeds threshold ({FairnessMonitor.GINI_THRESHOLD})")
        if min_coverage < FairnessMonitor.MIN_COVERAGE_THRESHOLD:
            issues.append(f"Minimum coverage ratio ({round(min_coverage, 4)}) below threshold ({FairnessMonitor.MIN_COVERAGE_THRESHOLD})")

        return {
            "gini_coefficient": gini,
            "need_adjusted_gini": need_gini,
            "min_coverage_ratio": round(min_coverage, 4),
            "coverage_details": coverage_details,
            "is_fair": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def redistribute(allocations: dict, zones: list, total_resources: float) -> dict:
        """
        Redistribute resources from over-served to under-served zones.
        Triggered when fairness check fails.
        """
        zone_map = {z["name"]: z for z in zones}
        adjusted = allocations.copy()
        total_alloc = sum(adjusted.values())
        total_pop = sum(z["population"] for z in zones)

        if total_pop == 0 or total_alloc == 0:
            return adjusted

        # Compute fair shares and identify over/under-served
        over_served = []
        under_served = []

        for zone in zones:
            name = zone["name"]
            pop_share = zone["population"] / total_pop
            severity_factor = zone["current_severity"] / 10.0
            need_share = (pop_share + severity_factor) / 2.0  # Blend of pop and severity
            fair_amount = need_share * total_alloc

            actual = adjusted.get(name, 0)
            if actual > fair_amount * 1.5:
                over_served.append((name, actual - fair_amount))
            elif actual < fair_amount * 0.6:
                under_served.append((name, fair_amount - actual))

        # Transfer from over to under
        transfer_pool = sum(excess for _, excess in over_served) * 0.3  # Transfer 30% of excess

        if transfer_pool > 0 and under_served:
            # Reduce over-served
            for name, excess in over_served:
                reduction = excess * 0.3
                adjusted[name] = round(adjusted[name] - reduction, 2)

            # Distribute to under-served proportionally
            total_deficit = sum(deficit for _, deficit in under_served)
            for name, deficit in under_served:
                share = deficit / total_deficit if total_deficit > 0 else 0
                adjusted[name] = round(adjusted.get(name, 0) + transfer_pool * share, 2)

        return adjusted
