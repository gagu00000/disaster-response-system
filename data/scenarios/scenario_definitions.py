"""
Scenario definition files for the disaster response simulation.
Each scenario defines zones, severity ranges, populations, dynamic events, and duration.
"""
import json
import os

# --- Scenario 1: Major Earthquake ---
EARTHQUAKE_SCENARIO = {
    "id": "earthquake",
    "name": "Major Earthquake",
    "type": "Earthquake",
    "description": "A magnitude 7.2 earthquake has struck the metropolitan region.",
    "duration": 15,
    "total_resources": 150,
    "zones": [
        {
            "name": "Urban Center",
            "severity": 9.0,
            "population": 200000,
            "accessibility": 3.0,
            "resource_availability": 2.0,
            "vulnerability": 0.7,
            "initial_demand": 50
        },
        {
            "name": "Suburban Ring",
            "severity": 6.5,
            "population": 120000,
            "accessibility": 6.0,
            "resource_availability": 4.0,
            "vulnerability": 0.5,
            "initial_demand": 35
        },
        {
            "name": "Industrial Zone",
            "severity": 7.0,
            "population": 15000,
            "accessibility": 5.0,
            "resource_availability": 3.0,
            "vulnerability": 0.4,
            "initial_demand": 25
        },
        {
            "name": "Rural Outskirts",
            "severity": 4.0,
            "population": 8000,
            "accessibility": 7.0,
            "resource_availability": 5.0,
            "vulnerability": 0.6,
            "initial_demand": 15
        },
        {
            "name": "Coastal Settlement",
            "severity": 5.5,
            "population": 5000,
            "accessibility": 4.0,
            "resource_availability": 6.0,
            "vulnerability": 0.8,
            "initial_demand": 20
        }
    ],
    "dynamic_events": [
        {"time_step": 1, "type": "hospital_reduction", "zone": "Urban Center", "description": "Hospital capacity reduced by 30%", "severity_change": 0.5, "accessibility_change": 0.0},
        {"time_step": 2, "type": "road_closure", "zone": "Suburban Ring", "description": "Major road closure due to debris", "severity_change": 0.0, "accessibility_change": -2.0},
        {"time_step": 3, "type": "aftershock", "zone": "Urban Center", "description": "Aftershock increases severity", "severity_change": 1.0, "accessibility_change": -1.0},
        {"time_step": 7, "type": "aftershock", "zone": "Industrial Zone", "description": "Secondary aftershock hits industrial area", "severity_change": 1.5, "accessibility_change": -0.5}
    ],
    "phases": [
        {"name": "Immediate Response", "start": 0, "end": 3, "description": "Golden hour — save lives"},
        {"name": "Stabilization", "start": 4, "end": 9, "description": "Secure zones and stabilize"},
        {"name": "Recovery", "start": 10, "end": 15, "description": "Begin recovery operations"}
    ]
}

# --- Scenario 2: Severe Flooding ---
FLOODING_SCENARIO = {
    "id": "flooding",
    "name": "Severe Flooding",
    "type": "Flood",
    "description": "Severe monsoon flooding affecting a river basin region.",
    "duration": 18,
    "total_resources": 180,
    "zones": [
        {
            "name": "Riverside District",
            "severity": 8.0,
            "population": 150000,
            "accessibility": 2.5,
            "resource_availability": 2.0,
            "vulnerability": 0.8,
            "initial_demand": 45
        },
        {
            "name": "Low-Lying Residential",
            "severity": 7.5,
            "population": 100000,
            "accessibility": 4.0,
            "resource_availability": 3.0,
            "vulnerability": 0.7,
            "initial_demand": 40
        },
        {
            "name": "Agricultural Belt",
            "severity": 5.0,
            "population": 30000,
            "accessibility": 5.0,
            "resource_availability": 4.0,
            "vulnerability": 0.6,
            "initial_demand": 20
        },
        {
            "name": "Highland Area",
            "severity": 2.5,
            "population": 20000,
            "accessibility": 8.0,
            "resource_availability": 7.0,
            "vulnerability": 0.3,
            "initial_demand": 10
        },
        {
            "name": "Commercial District",
            "severity": 6.0,
            "population": 80000,
            "accessibility": 5.5,
            "resource_availability": 5.0,
            "vulnerability": 0.4,
            "initial_demand": 25
        },
        {
            "name": "Evacuation Center",
            "severity": 3.0,
            "population": 3000,
            "accessibility": 9.0,
            "resource_availability": 8.0,
            "vulnerability": 0.2,
            "initial_demand": 8
        }
    ],
    "dynamic_events": [
        {"time_step": 2, "type": "water_rise", "zone": "Riverside District", "description": "Water level rises 1.5m", "severity_change": 0.5, "accessibility_change": -1.0},
        {"time_step": 3, "type": "route_flooding", "zone": "Low-Lying Residential", "description": "Access routes flooded", "severity_change": 0.5, "accessibility_change": -2.0},
        {"time_step": 4, "type": "water_rise", "zone": "Agricultural Belt", "description": "Floodwaters reach agricultural belt", "severity_change": 1.0, "accessibility_change": -1.0},
        {"time_step": 5, "type": "dam_breach_warning", "zone": "Riverside District", "description": "Dam breach warning issued upstream", "severity_change": 1.5, "accessibility_change": -0.5},
        {"time_step": 6, "type": "water_rise", "zone": "Commercial District", "description": "Flooding reaches commercial areas", "severity_change": 1.0, "accessibility_change": -1.5}
    ],
    "phases": [
        {"name": "Immediate Response", "start": 0, "end": 4, "description": "Evacuate and rescue"},
        {"name": "Stabilization", "start": 5, "end": 11, "description": "Contain and stabilize"},
        {"name": "Recovery", "start": 12, "end": 18, "description": "Drain and rebuild"}
    ]
}

# --- Scenario 3: Urban Industrial Accident ---
INDUSTRIAL_SCENARIO = {
    "id": "industrial",
    "name": "Urban Industrial Accident",
    "type": "Industrial Accident",
    "description": "Chemical plant explosion in an urban industrial zone.",
    "duration": 12,
    "total_resources": 100,
    "zones": [
        {
            "name": "Accident Site",
            "severity": 10.0,
            "population": 2000,
            "accessibility": 1.5,
            "resource_availability": 1.0,
            "vulnerability": 0.9,
            "initial_demand": 35
        },
        {
            "name": "Adjacent Residential",
            "severity": 7.0,
            "population": 80000,
            "accessibility": 5.0,
            "resource_availability": 3.0,
            "vulnerability": 0.7,
            "initial_demand": 30
        },
        {
            "name": "Downwind Exposure",
            "severity": 5.5,
            "population": 50000,
            "accessibility": 6.5,
            "resource_availability": 5.0,
            "vulnerability": 0.6,
            "initial_demand": 20
        },
        {
            "name": "Hospital District",
            "severity": 3.0,
            "population": 30000,
            "accessibility": 8.0,
            "resource_availability": 7.0,
            "vulnerability": 0.3,
            "initial_demand": 10
        }
    ],
    "dynamic_events": [
        {"time_step": 2, "type": "evacuation_order", "zone": "Adjacent Residential", "description": "Evacuation order issued for adjacent residential", "severity_change": 0.5, "accessibility_change": -1.0},
        {"time_step": 3, "type": "plume_shift", "zone": "Downwind Exposure", "description": "Chemical plume shifts direction", "severity_change": 2.0, "accessibility_change": -1.5},
        {"time_step": 5, "type": "secondary_explosion", "zone": "Accident Site", "description": "Risk of secondary explosion", "severity_change": 0.0, "accessibility_change": -2.0}
    ],
    "phases": [
        {"name": "Immediate Response", "start": 0, "end": 3, "description": "Contain and evacuate"},
        {"name": "Stabilization", "start": 4, "end": 8, "description": "Neutralize and secure"},
        {"name": "Recovery", "start": 9, "end": 12, "description": "Decontaminate and restore"}
    ]
}

ALL_SCENARIOS = {
    "earthquake": EARTHQUAKE_SCENARIO,
    "flooding": FLOODING_SCENARIO,
    "industrial": INDUSTRIAL_SCENARIO
}


def get_scenario(scenario_id: str) -> dict:
    """Retrieve a scenario by its ID."""
    if scenario_id not in ALL_SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_id}. Available: {list(ALL_SCENARIOS.keys())}")
    return ALL_SCENARIOS[scenario_id]


def list_scenarios() -> list:
    """Return a list of available scenario summaries."""
    return [
        {"id": s["id"], "name": s["name"], "type": s["type"], "zones": len(s["zones"]), "duration": s["duration"]}
        for s in ALL_SCENARIOS.values()
    ]
