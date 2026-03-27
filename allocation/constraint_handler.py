"""
Constraint Handler Module
Enforces capacity, floor, and budget constraints on resource allocations.
Per Section 5.1 Step 3.
"""


class ConstraintHandler:
    """
    Enforces allocation constraints:
    - Capacity constraints: no zone receives more than it can absorb
    - Floor constraints: every zone with severity > 0 gets a minimum allocation
    - Budget constraints: total allocation cannot exceed supply
    """

    @staticmethod
    def apply_constraints(allocations: dict, zones: list, total_available: float,
                           min_share: float = 0.03, max_share: float = 0.45) -> dict:
        """
        Apply all allocation constraints.

        Args:
            allocations: proposed allocation {zone_name: amount}
            zones: list of zone state dicts
            total_available: total resources available
            min_share: minimum share per zone (fraction of total)
            max_share: maximum share per zone (fraction of total)

        Returns:
            Constrained allocation dict
        """
        constrained = allocations.copy()
        zone_map = {z["name"]: z for z in zones}

        min_amount = total_available * min_share
        max_amount = total_available * max_share

        for zone_name in constrained:
            if zone_name in zone_map:
                zone = zone_map[zone_name]

                # Floor constraint: zones with severity > 0 get minimum allocation
                if zone["current_severity"] > 0:
                    constrained[zone_name] = max(constrained[zone_name], min_amount)

                # Capacity constraint: cap at maximum
                constrained[zone_name] = min(constrained[zone_name], max_amount)

                # Absorption constraint: zone can't absorb more than 2x its demand
                max_absorb = zone.get("unmet_demand", 20) * 2.0
                if max_absorb > 0:
                    constrained[zone_name] = min(constrained[zone_name], max_absorb)

        # Budget constraint: total can't exceed available
        total = sum(constrained.values())
        if total > total_available:
            scale = total_available / total
            constrained = {k: round(v * scale, 2) for k, v in constrained.items()}
        else:
            constrained = {k: round(v, 2) for k, v in constrained.items()}

        return constrained

    @staticmethod
    def validate_allocation(allocations: dict, zones: list, total_available: float) -> dict:
        """
        Validate an allocation and return issues if any.

        Returns:
            dict with is_valid, issues list, total_allocated, remaining
        """
        issues = []
        total = sum(allocations.values())

        if total > total_available * 1.01:  # 1% tolerance
            issues.append(f"Total allocation ({total:.2f}) exceeds available resources ({total_available:.2f})")

        zone_names = {z["name"] for z in zones}
        for zone_name in allocations:
            if zone_name not in zone_names:
                issues.append(f"Unknown zone in allocation: {zone_name}")

        for zone_name, amount in allocations.items():
            if amount < 0:
                issues.append(f"Negative allocation for {zone_name}: {amount}")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "total_allocated": round(total, 2),
            "remaining": round(total_available - total, 2)
        }
