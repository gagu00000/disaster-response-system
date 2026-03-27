# Technical Reference — Multi-Agent Disaster Response System

## Architecture

```
Frontend (Streamlit) → Controller → Agents + Decision Engine + Allocation → Explainability → LLM Layer
```

All data flows **unidirectionally** from simulation to display. The LLM is strictly a narrator.

---

## Module Reference

### `simulation/disaster_environment.py`
- **Zone** class: State container for each disaster zone
- **DisasterEnvironment** class: Manages zone collection, resource pool, phase transitions
- Key methods: `initialize()`, `apply_resources()`, `get_all_zone_states()`, `advance_step()`

### `simulation/simulation_engine.py`
- **SimulationEngine** class: Orchestrates the time-step loop
- Key methods: `initialize()`, `apply_dynamic_events()`, `execute_allocation()`, `advance_step()`
- Tracks `metrics_history`, `allocation_history`, `event_log`

### `simulation/event_system.py`
- **EventSystem** class: Schedules and fires dynamic events by step number
- Events modify zone severity, accessibility, or other properties

### `simulation/impact_calculator.py`
- **ImpactCalculator** class: Computes performance metrics
- Methods: `compute_metrics()` → Gini coefficient, response coverage, avg resilience, resource utilization, total cost

---

### `decision_engine/ahp_module.py`
- **AHPModule** class: Implements Saaty's AHP
- Constructs pairwise comparison matrix from weight profiles
- Computes principal eigenvector via power method (100 iterations)
- Validates consistency ratio < 0.10

### `decision_engine/fuzzy_module.py`
- **FuzzyModule** class: scikit-fuzzy based inference
- 4 inputs: severity, population_density, accessibility, resource_availability (0-10)
- 1 output: priority_score (0-100)
- 18 rules covering significant input combinations
- Defuzzification: centroid method

### `decision_engine/criteria_manager.py`
- **CriteriaManager** class: Agent weight profile storage
- Phase-based dynamic adaptation for AI Coordinator agent
- 3 phases: Immediate Response, Stabilization, Recovery

### `decision_engine/priority_aggregator.py`
- **PriorityAggregator** class: Combines AHP weights × Fuzzy scores
- Produces composite priority score per zone per agent

---

### `agents/base_agent.py`
- **BaseAgent** abstract class: Common interface for all agents
- Methods: `evaluate_zones()`, `generate_proposal()`, `make_concession()`
- Each subclass overrides `get_behavioral_adjustment()`

### `agents/emergency_agent.py` / `government_agent.py` / `ngo_agent.py`
- Concrete agent implementations with specific weight profiles
- Behavioral adjustments: severity multiplier, cost penalty, vulnerability boost

### `agents/ai_coordinator_agent.py`
- Dynamic phase-based weight adaptation
- Divergence analysis: identifies agreed vs contested zones
- Weighted consensus computation

### `agents/negotiation_engine.py`
- 5-round protocol: Independent Eval → Proposal Exchange → Divergence Analysis → Counter-Proposals → Weighted Consensus
- Concession rate: 0.3 per round
- Dissent score computation per agent

---

### `allocation/resource_allocator.py`
- Pipeline: Negotiation → Constraints → Fairness Check → Redistribution
- Returns: `final_allocation`, `negotiation_result`, `fairness_after`, `was_redistributed`

### `allocation/fairness_monitor.py`
- Gini coefficient computation (0 = equal, 1 = unequal)
- Threshold: 0.30
- Auto-redistribution: 30% transfer rate from over-served to under-served

### `allocation/constraint_handler.py`
- Floor constraint: 3% minimum per zone
- Capacity constraint: 2× unmet demand maximum
- Budget constraint: total ≤ available

---

### `llm_layer/llm_client.py`
- Ollama API client with model auto-detection
- Fallback models: mistral → llama3.2 → phi3
- Temperature: 0.1, graceful degradation on connection failure

### `llm_layer/prompt_engine.py`
- 4 prompt templates: explanation, query, insight, scenario
- Each includes strict guardrail instructions
- System prompts enforce data-only responses

### `llm_layer/validation_layer.py`
- 5 checks: numerical accuracy, entity validation, temporal consistency, claim grounding, prohibited content
- Pass/fail decision: 0 flags = pass, 1-2 minor = pass with caveat, 3+ or critical = fail → fallback

### `llm_layer/response_formatter.py`
- Adds "🤖 AI-Generated" labels
- Truncation at 2000 characters
- Caveat annotation for approximate responses

---

## Data Structures

### Zone State
```python
{
    "name": str,
    "current_severity": float,  # 0-10
    "population": int,
    "population_at_risk": int,
    "accessibility": float,     # 0-10
    "unmet_demand": float,
    "cumulative_resources_received": float,
    "resilience_index": float   # 0-1
}
```

### Allocation Result
```python
{
    "final_allocation": {"Zone A": 35.0, ...},
    "negotiation_result": {
        "proposals": {"Emergency Response": {...}, ...},
        "divergence": {"contested_zones": [...], "agreed_zones": [...]},
        "dissent_scores": {"Emergency Response": 0.05, ...}
    },
    "fairness_after": {"gini_coefficient": 0.22, "is_fair": True},
    "was_redistributed": False
}
```

---

## Configuration Parameters
All system parameters are in `data/configurations/system_config.json`.
