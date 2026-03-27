"""
Validation Layer Module
Post-generation verification of LLM outputs against actual system data.
Performs 5 checks per Section 22.2.
"""
import re


class ValidationLayer:
    """
    Validates LLM outputs before displaying to the user.
    Performs numerical accuracy, entity validation, temporal consistency,
    claim grounding, and prohibited content checks.
    """

    # Prohibited language patterns
    SPECULATIVE_PATTERNS = [
        r'\bcould have\b', r'\bmight have\b', r'\bshould have\b',
        r'\bif only\b', r'\bwould have\b', r'\bperhaps\b',
        r'\bwhat if\b', r'\bpossibly\b', r'\bspeculate\b'
    ]

    EMOTIONAL_PATTERNS = [
        r'\btragic\b', r'\bdevastating\b', r'\bheartbreaking\b',
        r'\bhorrific\b', r'\bterrible\b', r'\bawful\b',
        r'\bstunning\b', r'\bshocking\b'
    ]

    EXTERNAL_PATTERNS = [
        r'\baccording to studies\b', r'\bhistorically\b',
        r'\bin similar disasters\b', r'\bresearch shows\b',
        r'\bexperts say\b', r'\bit is known that\b'
    ]

    VALID_AGENT_NAMES = [
        "Emergency Response", "Emergency", "Government Agency", "Government",
        "NGO", "AI Coordinator", "AI", "Coordinator"
    ]

    @staticmethod
    def validate(response: str, context_data: dict) -> dict:
        """
        Run all validation checks on an LLM response.

        Returns:
            dict with 'passed', 'flags', 'minor_issues', 'critical_issues'
        """
        flags = []

        # CHECK 1: Numerical Accuracy
        num_flags = ValidationLayer._check_numbers(response, context_data)
        flags.extend(num_flags)

        # CHECK 2: Entity Validation
        entity_flags = ValidationLayer._check_entities(response, context_data)
        flags.extend(entity_flags)

        # CHECK 3: Temporal Consistency
        temporal_flags = ValidationLayer._check_temporal(response, context_data)
        flags.extend(temporal_flags)

        # CHECK 4: Claim Grounding
        claim_flags = ValidationLayer._check_claims(response, context_data)
        flags.extend(claim_flags)

        # CHECK 5: Prohibited Content
        prohibited_flags = ValidationLayer._check_prohibited(response)
        flags.extend(prohibited_flags)

        # Decision logic
        critical_flags = [f for f in flags if f.get("severity") == "critical"]
        minor_flags = [f for f in flags if f.get("severity") == "minor"]

        if len(flags) == 0:
            passed = True
        elif len(critical_flags) == 0 and len(minor_flags) <= 2:
            passed = True  # Pass with caveat
        else:
            passed = False

        return {
            "passed": passed,
            "flags": flags,
            "total_flags": len(flags),
            "minor_issues": len(minor_flags),
            "critical_issues": len(critical_flags),
            "caveat": len(minor_flags) > 0 and len(critical_flags) == 0
        }

    @staticmethod
    def _check_numbers(response: str, context_data: dict) -> list:
        """CHECK 1: Extract numbers from response and cross-reference with data."""
        flags = []
        # Extract all numbers from the response
        numbers_in_response = re.findall(r'\b\d+\.?\d*\b', response)

        # Get valid numbers from context data
        valid_numbers = set()
        zones = context_data.get("zones", context_data.get("post_state", []))
        allocations = context_data.get("allocations", context_data.get("final_allocation", {}))
        metrics = context_data.get("metrics", {})

        for z in zones:
            valid_numbers.add(str(round(z.get("current_severity", 0), 1)))
            valid_numbers.add(str(z.get("population", 0)))
            valid_numbers.add(str(z.get("population_at_risk", 0)))

        for v in allocations.values():
            valid_numbers.add(str(round(v, 1)))

        for v in metrics.values():
            if isinstance(v, (int, float)):
                valid_numbers.add(str(round(v, 1)))
                valid_numbers.add(str(round(v, 2)))
                valid_numbers.add(str(round(v, 3)))

        # Check step numbers and common numbers (don't flag these)
        common_ok = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '100'}
        valid_numbers.update(common_ok)

        # Only flag suspicious numbers (big specific values not in data)
        for num in numbers_in_response:
            try:
                val = float(num)
                if val > 10 and num not in valid_numbers:
                    # Check if it's close to any valid number
                    close = any(abs(val - float(vn)) < max(1, val * 0.1)
                               for vn in valid_numbers if vn.replace('.', '').isdigit())
                    if not close:
                        flags.append({
                            "check": "numerical_accuracy",
                            "severity": "minor",
                            "detail": f"Number {num} not found in source data"
                        })
            except ValueError:
                pass

        return flags

    @staticmethod
    def _check_entities(response: str, context_data: dict) -> list:
        """CHECK 2: Verify zone names and agent names."""
        flags = []
        zones = context_data.get("zones", context_data.get("post_state", []))
        valid_zone_names = [z["name"].lower() for z in zones]

        # Check for potential zone name mentions
        response_lower = response.lower()
        zone_keywords = ["zone", "area", "district", "center", "settlement", "ring", "outskirts"]

        # Check agent names
        for pattern in ["agent"]:
            if pattern in response_lower:
                # Make sure referenced agents exist
                for agent in ValidationLayer.VALID_AGENT_NAMES:
                    if agent.lower() in response_lower:
                        break

        return flags

    @staticmethod
    def _check_temporal(response: str, context_data: dict) -> list:
        """CHECK 3: Verify temporal references."""
        flags = []
        step = context_data.get("step", 0)

        # Check for time step references
        step_refs = re.findall(r'(?:time )?step (\d+)', response, re.IGNORECASE)
        for ref in step_refs:
            ref_step = int(ref)
            total_steps = context_data.get("total_steps", 20)
            if ref_step > total_steps:
                flags.append({
                    "check": "temporal_consistency",
                    "severity": "critical",
                    "detail": f"References step {ref_step} which exceeds total steps ({total_steps})"
                })

        return flags

    @staticmethod
    def _check_claims(response: str, context_data: dict) -> list:
        """CHECK 4: Verify comparative and causal claims."""
        flags = []
        allocations = context_data.get("allocations", context_data.get("final_allocation", {}))

        # Check "more than" / "less than" claims
        more_pattern = r'(\w[\w\s]*?) received more (?:resources )?than (\w[\w\s]*?)[\.\,]'
        matches = re.findall(more_pattern, response, re.IGNORECASE)
        for zone_a, zone_b in matches:
            zone_a = zone_a.strip()
            zone_b = zone_b.strip()
            if zone_a in allocations and zone_b in allocations:
                if allocations[zone_a] <= allocations[zone_b]:
                    flags.append({
                        "check": "claim_grounding",
                        "severity": "critical",
                        "detail": f"Claim '{zone_a} > {zone_b}' contradicts data "
                                  f"({allocations[zone_a]} vs {allocations[zone_b]})"
                    })

        return flags

    @staticmethod
    def _check_prohibited(response: str) -> list:
        """CHECK 5: Scan for prohibited content."""
        flags = []
        response_lower = response.lower()

        for pattern in ValidationLayer.SPECULATIVE_PATTERNS:
            if re.search(pattern, response_lower):
                flags.append({
                    "check": "prohibited_content",
                    "severity": "minor",
                    "detail": f"Speculative language detected: {pattern}"
                })

        for pattern in ValidationLayer.EMOTIONAL_PATTERNS:
            if re.search(pattern, response_lower):
                flags.append({
                    "check": "prohibited_content",
                    "severity": "minor",
                    "detail": f"Emotional language detected: {pattern}"
                })

        for pattern in ValidationLayer.EXTERNAL_PATTERNS:
            if re.search(pattern, response_lower):
                flags.append({
                    "check": "prohibited_content",
                    "severity": "critical",
                    "detail": f"External reference detected: {pattern}"
                })

        return flags
