"""
Fuzzy Logic Module
Implements fuzzy inference for zone priority scoring using scikit-fuzzy.
Fuzzy variables: Severity, Population Density, Accessibility, Resource Availability.
Output: Priority Score (0-100).
Per Section 4.3 of the implementation plan.
"""
import numpy as np

try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    SKFUZZY_AVAILABLE = True
except ImportError:
    SKFUZZY_AVAILABLE = False


class FuzzyModule:
    """
    Implements fuzzy logic inference for computing zone priority scores.
    Uses trapezoidal and triangular membership functions as specified.
    """

    def __init__(self):
        if SKFUZZY_AVAILABLE:
            self._build_fuzzy_system()
        else:
            self.simulation = None

    def _build_fuzzy_system(self):
        """Build the fuzzy inference system with all variables and rules."""
        # --- Input Variables (0-10 scale) ---
        self.severity = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'severity')
        self.population_density = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'population_density')
        self.accessibility = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'accessibility')
        self.resource_availability = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'resource_availability')

        # --- Output Variable (0-100 scale) ---
        self.priority = ctrl.Consequent(np.arange(0, 100.1, 0.5), 'priority')

        # --- Membership Functions: Severity ---
        self.severity['low'] = fuzz.trapmf(self.severity.universe, [0, 0, 2, 4])
        self.severity['moderate'] = fuzz.trimf(self.severity.universe, [2, 5, 8])
        self.severity['high'] = fuzz.trapmf(self.severity.universe, [6, 8, 10, 10])

        # --- Membership Functions: Population Density ---
        self.population_density['sparse'] = fuzz.trapmf(self.population_density.universe, [0, 0, 2, 4])
        self.population_density['medium'] = fuzz.trimf(self.population_density.universe, [3, 5, 7])
        self.population_density['dense'] = fuzz.trapmf(self.population_density.universe, [6, 8, 10, 10])

        # --- Membership Functions: Accessibility ---
        self.accessibility['difficult'] = fuzz.trapmf(self.accessibility.universe, [0, 0, 2, 4])
        self.accessibility['moderate'] = fuzz.trimf(self.accessibility.universe, [3, 5, 7])
        self.accessibility['easy'] = fuzz.trapmf(self.accessibility.universe, [6, 8, 10, 10])

        # --- Membership Functions: Resource Availability ---
        self.resource_availability['scarce'] = fuzz.trapmf(self.resource_availability.universe, [0, 0, 2, 4])
        self.resource_availability['adequate'] = fuzz.trimf(self.resource_availability.universe, [3, 5, 7])
        self.resource_availability['abundant'] = fuzz.trapmf(self.resource_availability.universe, [6, 8, 10, 10])

        # --- Membership Functions: Priority (Output) ---
        self.priority['very_low'] = fuzz.trapmf(self.priority.universe, [0, 0, 10, 25])
        self.priority['low'] = fuzz.trimf(self.priority.universe, [10, 25, 45])
        self.priority['medium'] = fuzz.trimf(self.priority.universe, [30, 50, 70])
        self.priority['high'] = fuzz.trimf(self.priority.universe, [55, 75, 90])
        self.priority['very_high'] = fuzz.trapmf(self.priority.universe, [75, 90, 100, 100])

        # --- Fuzzy Rules (Section 4.3.2) ---
        rules = []

        # Rule 1: High severity + Dense population + Difficult access → Very High
        rules.append(ctrl.Rule(
            self.severity['high'] & self.population_density['dense'] & self.accessibility['difficult'],
            self.priority['very_high']
        ))
        # Rule 2: High severity + Sparse population + Easy access → Medium
        rules.append(ctrl.Rule(
            self.severity['high'] & self.population_density['sparse'] & self.accessibility['easy'],
            self.priority['medium']
        ))
        # Rule 3: Moderate severity + Dense population + Scarce resources → High
        rules.append(ctrl.Rule(
            self.severity['moderate'] & self.population_density['dense'] & self.resource_availability['scarce'],
            self.priority['high']
        ))
        # Rule 4: Low severity + Sparse population + Abundant resources → Very Low
        rules.append(ctrl.Rule(
            self.severity['low'] & self.population_density['sparse'] & self.resource_availability['abundant'],
            self.priority['very_low']
        ))
        # Rule 5: High severity + Scarce resources → Very High
        rules.append(ctrl.Rule(
            self.severity['high'] & self.resource_availability['scarce'],
            self.priority['very_high']
        ))
        # Rule 6: High severity + Dense population → High
        rules.append(ctrl.Rule(
            self.severity['high'] & self.population_density['dense'],
            self.priority['high']
        ))
        # Rule 7: Moderate severity + Medium population → Medium
        rules.append(ctrl.Rule(
            self.severity['moderate'] & self.population_density['medium'],
            self.priority['medium']
        ))
        # Rule 8: Low severity + Dense population + Scarce resources → Medium
        rules.append(ctrl.Rule(
            self.severity['low'] & self.population_density['dense'] & self.resource_availability['scarce'],
            self.priority['medium']
        ))
        # Rule 9: High severity + Moderate access + Adequate resources → High
        rules.append(ctrl.Rule(
            self.severity['high'] & self.accessibility['moderate'] & self.resource_availability['adequate'],
            self.priority['high']
        ))
        # Rule 10: Moderate severity + Difficult access → High
        rules.append(ctrl.Rule(
            self.severity['moderate'] & self.accessibility['difficult'],
            self.priority['high']
        ))
        # Rule 11: Low severity + Medium population + Adequate resources → Low
        rules.append(ctrl.Rule(
            self.severity['low'] & self.population_density['medium'] & self.resource_availability['adequate'],
            self.priority['low']
        ))
        # Rule 12: High severity + Medium population + Moderate access → High
        rules.append(ctrl.Rule(
            self.severity['high'] & self.population_density['medium'] & self.accessibility['moderate'],
            self.priority['high']
        ))
        # Rule 13: Moderate severity + Sparse population + Easy access → Low
        rules.append(ctrl.Rule(
            self.severity['moderate'] & self.population_density['sparse'] & self.accessibility['easy'],
            self.priority['low']
        ))
        # Rule 14: Low severity + Easy access + Abundant resources → Very Low
        rules.append(ctrl.Rule(
            self.severity['low'] & self.accessibility['easy'] & self.resource_availability['abundant'],
            self.priority['very_low']
        ))
        # Rule 15: Moderate severity + Dense population + Difficult access → Very High
        rules.append(ctrl.Rule(
            self.severity['moderate'] & self.population_density['dense'] & self.accessibility['difficult'],
            self.priority['very_high']
        ))
        # Rule 16: High severity + Easy access → Medium (accessible high-severity)
        rules.append(ctrl.Rule(
            self.severity['high'] & self.accessibility['easy'],
            self.priority['medium']
        ))
        # Rule 17: Moderate severity + Adequate resources → Medium
        rules.append(ctrl.Rule(
            self.severity['moderate'] & self.resource_availability['adequate'],
            self.priority['medium']
        ))
        # Rule 18: Low severity + Difficult access → Medium
        rules.append(ctrl.Rule(
            self.severity['low'] & self.accessibility['difficult'],
            self.priority['medium']
        ))

        self.ctrl_system = ctrl.ControlSystem(rules)
        self.simulation = ctrl.ControlSystemSimulation(self.ctrl_system)

    def compute_priority(self, severity: float, population_density: float,
                          accessibility: float, resource_availability: float) -> float:
        """
        Compute fuzzy priority score for a zone.

        Args:
            severity: 0-10 scale
            population_density: 0-10 scale
            accessibility: 0-10 scale
            resource_availability: 0-10 scale

        Returns:
            Priority score 0-100
        """
        if not SKFUZZY_AVAILABLE or self.simulation is None:
            return self._fallback_priority(severity, population_density, accessibility, resource_availability)

        try:
            # Clamp inputs to valid range
            self.simulation.input['severity'] = max(0.0, min(10.0, severity))
            self.simulation.input['population_density'] = max(0.0, min(10.0, population_density))
            self.simulation.input['accessibility'] = max(0.0, min(10.0, accessibility))
            self.simulation.input['resource_availability'] = max(0.0, min(10.0, resource_availability))

            self.simulation.compute()
            result = self.simulation.output['priority']
            # Reset for next computation
            self.simulation = ctrl.ControlSystemSimulation(self.ctrl_system)
            return round(result, 2)
        except Exception:
            return self._fallback_priority(severity, population_density, accessibility, resource_availability)

    def _fallback_priority(self, severity: float, population_density: float,
                            accessibility: float, resource_availability: float) -> float:
        """
        Fallback priority calculation when skfuzzy is not available.
        Uses a weighted linear combination.
        """
        # Higher severity → higher priority
        # Higher population → higher priority
        # Lower accessibility → higher priority (harder to reach = more urgent)
        # Lower resource availability → higher priority
        score = (
            severity * 4.0 +
            population_density * 2.5 +
            (10 - accessibility) * 2.0 +
            (10 - resource_availability) * 1.5
        )
        return round(min(100, max(0, score)), 2)

    def compute_zone_scores(self, zones: list) -> dict:
        """
        Compute priority scores for all zones.

        Args:
            zones: list of zone state dicts

        Returns:
            dict mapping zone_name → priority_score
        """
        scores = {}
        for zone in zones:
            pop_density = min(10, zone["population"] / 20000)  # Normalize population to 0-10
            score = self.compute_priority(
                severity=zone["current_severity"],
                population_density=pop_density,
                accessibility=zone["accessibility"],
                resource_availability=zone["resource_availability"]
            )
            scores[zone["name"]] = score
        return scores

    def compute_criterion_scores(self, zones: list) -> dict:
        """
        Compute per-criterion fuzzy scores for each zone.
        Returns: {zone_name: {speed: score, fairness: score, cost: score, resilience: score}}
        """
        result = {}
        for zone in zones:
            severity = zone["current_severity"]
            pop_density = min(10, zone["population"] / 20000)
            accessibility = zone["accessibility"]
            resource_avail = zone["resource_availability"]
            vulnerability = zone.get("vulnerability", 0.5)

            # Speed score: based on severity and accessibility (urgent + accessible = fast response needed)
            speed_score = self.compute_priority(severity, pop_density, accessibility, resource_avail)

            # Fairness score: based on vulnerability and unmet demand
            unmet = min(10, zone.get("unmet_demand", 5) / 5.0)
            fairness_score = self.compute_priority(unmet, pop_density * vulnerability * 2, 5.0, resource_avail)

            # Cost score: inverse — lower accessibility = higher cost, so higher priority
            cost_score = self.compute_priority(severity, pop_density, 10 - accessibility, resource_avail)

            # Resilience score: based on long-term recovery potential
            resilience_val = zone.get("resilience_index", 0.5)
            resilience_score = self.compute_priority(severity, pop_density, accessibility, (1 - resilience_val) * 10)

            result[zone["name"]] = {
                "speed": round(speed_score, 2),
                "fairness": round(fairness_score, 2),
                "cost": round(cost_score, 2),
                "resilience": round(resilience_score, 2)
            }
        return result
