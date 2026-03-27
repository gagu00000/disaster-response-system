# Multi-Agent Disaster Response and Resource Allocation System

An AI-powered disaster response simulation that uses **multi-agent negotiation**, **AHP (Analytic Hierarchy Process)**, **Fuzzy Logic**, and **LLM-based explainability** to allocate emergency resources across disaster-affected zones.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT DASHBOARD                       │
│  [Overview] [Agents] [Allocation] [Analytics] [AI Explain]  │
├─────────────────────────────────────────────────────────────┤
│                     CONTROLLER LAYER                         │
│              Orchestration │ Data Routing                    │
├──────────┬──────────┬──────────┬────────────────────────────┤
│ AGENTS   │ DECISION │ ALLOC    │ EXPLAINABILITY             │
│ Emergency│ AHP      │ Resource │ Template Narrator          │
│ Govt     │ Fuzzy    │ Fairness │ Trade-off Reporter         │
│ NGO      │ Criteria │ Constr.  │ Audit Trail                │
│ AI Coord │ Priority │          │                            │
├──────────┴──────────┴──────────┼────────────────────────────┤
│         SIMULATION ENGINE       │     LLM LAYER (Optional)  │
│  Environment │ Events │ Impact  │ Client │ Prompts │ Valid. │
└─────────────────────────────────┴────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- (Optional) [Ollama](https://ollama.ai) for LLM features

### Installation
```bash
cd disaster-response-system
pip install -r requirements.txt
```

### Run the Dashboard
```bash
streamlit run app/dashboard.py
```

### (Optional) Enable LLM Features
```bash
# Install Ollama from https://ollama.ai
ollama pull mistral
# Restart the dashboard — LLM features auto-detect
```

---

## 📋 Features

### 🔬 Multi-Criteria Decision Making
- **AHP Module**: Pairwise comparison matrices, eigenvector computation, consistency ratio validation (CR < 0.10)
- **Fuzzy Logic Module**: 18 inference rules with trapezoidal/triangular membership functions for 4 input variables
- **Integration**: Composite priority scores = AHP weights × Fuzzy criterion scores

### 🤖 Four Specialized Agents
| Agent | Primary Focus | Key Weights |
|-------|--------------|-------------|
| **Emergency Response** | Save lives, fast response | Speed: 50%, Resilience: 30% |
| **Government Agency** | Budget management, balanced coverage | Cost: 35%, Resilience: 25% |
| **NGO** | Equitable distribution, vulnerable populations | Fairness: 45%, Resilience: 30% |
| **AI Coordinator** | Global optimization, dynamic adaptation | Phase-dependent (adapts over time) |

### 🤝 5-Round Negotiation Protocol
1. **Independent Evaluation** — Each agent evaluates zones via AHP + Fuzzy Logic
2. **Proposal Exchange** — All agents submit allocation proposals simultaneously
3. **Divergence Analysis** — AI Coordinator identifies agreed vs. contested zones
4. **Counter-Proposals** — Agents make concessions on contested zones
5. **Weighted Consensus** — Domain-authority-weighted final allocation

### 📊 Performance Metrics
| Metric | Target | Description |
|--------|--------|-------------|
| Response Coverage | > 70% | Average resource coverage across zones |
| Gini Coefficient | < 0.30 | Distributional equity (0=equal, 1=unequal) |
| Resilience Index | > 0.60 | Average zone resilience score |
| Resource Utilization | > 90% | Fraction of resources deployed |

### 🧠 LLM Explainability (Optional)
- **Decision Explanations**: Natural-language explanations referencing specific data
- **Ask AI**: Query the system about allocation decisions
- **Insight Reports**: Post-simulation narrative analysis
- **Validation Layer**: 5 automated checks before display (numerical accuracy, entity validation, temporal consistency, claim grounding, prohibited content)
- **Graceful Degradation**: Falls back to template-based explanations when LLM unavailable

---

## 🌍 Disaster Scenarios

### 1. Major Earthquake
- 5 zones: Urban Center, Suburban Ring, Industrial Zone, Rural Outskirts, Coastal Settlement
- 15 time steps | 150 resource units
- Dynamic events: aftershocks, road closures, hospital damage

### 2. Severe Flooding
- 6 zones: Riverside District, Low-Lying Residential, Agricultural Belt, Highland Area, Commercial District, Evacuation Center
- 18 time steps | 180 resource units
- Dynamic events: water level rises, route flooding, dam breach warnings

### 3. Urban Industrial Accident
- 4 zones: Accident Site, Adjacent Residential, Downwind Exposure, Hospital District
- 12 time steps | 100 resource units
- Dynamic events: evacuation orders, chemical plume shifts, secondary explosion risk

---

## 📁 Project Structure

```
disaster-response-system/
├── app/
│   ├── controller.py          # Central orchestration
│   ├── dashboard.py           # Streamlit dashboard (5 tabs)
│   └── main.py                # Entry point
├── agents/
│   ├── base_agent.py          # Abstract agent interface
│   ├── emergency_agent.py     # Emergency Response Agent
│   ├── government_agent.py    # Government Agency Agent
│   ├── ngo_agent.py           # NGO Agent
│   ├── ai_coordinator_agent.py # AI Coordinator Agent
│   └── negotiation_engine.py  # 5-round negotiation protocol
├── decision_engine/
│   ├── ahp_module.py          # Analytic Hierarchy Process
│   ├── fuzzy_module.py        # Fuzzy Logic inference (18 rules)
│   ├── criteria_manager.py    # Agent weight profiles
│   └── priority_aggregator.py # AHP + Fuzzy integration
├── simulation/
│   ├── disaster_environment.py # Zone & world state management
│   ├── event_system.py        # Dynamic event scheduling
│   ├── impact_calculator.py   # Performance metric computation
│   └── simulation_engine.py   # Main time-step loop
├── allocation/
│   ├── resource_allocator.py  # Full allocation pipeline
│   ├── fairness_monitor.py    # Gini coefficient monitoring
│   └── constraint_handler.py  # Capacity/floor/budget constraints
├── explainability/
│   ├── decision_narrator.py   # Template-based explanations
│   ├── tradeoff_reporter.py   # Trade-off analysis
│   └── audit_trail.py         # Decision logging
├── visualization/
│   ├── charts.py              # 7 Plotly chart types
│   └── metrics_display.py     # KPI cards & scorecards
├── llm_layer/
│   ├── llm_client.py          # Ollama API client
│   ├── prompt_engine.py       # 4 prompt templates
│   ├── validation_layer.py    # 5 post-generation checks
│   ├── response_formatter.py  # Output formatting
│   ├── query_handler.py       # User question handling
│   ├── insight_generator.py   # Post-simulation reports
│   └── llm_cache.py           # Response caching
├── data/
│   ├── scenarios/             # 3 disaster scenario definitions
│   ├── configurations/        # System config
│   ├── logs/                  # Audit trail logs
│   └── llm_cache/             # Cached LLM responses
├── tests/
│   └── test_integration.py    # Integration test suite
└── requirements.txt
```

---

## 🧪 Running Tests

```bash
python tests/test_integration.py
```

This runs a comprehensive integration test covering:
- All 3 scenario loading and validation
- AHP consistency checking
- Fuzzy logic scoring accuracy
- Full allocation pipeline with negotiation
- Template explanation generation
- Validation layer checks
- End-to-end simulation for all scenarios

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Decision Making | NumPy/SciPy (AHP), scikit-fuzzy (Fuzzy Logic) |
| Visualization | Plotly |
| LLM Integration | Ollama (local, privacy-preserving) |
| Language | Python 3.10+ |

---

## 📖 Key Design Principles

1. **Algorithmic Integrity**: The LLM is a **translator and narrator**, never a decision-maker
2. **Data-Grounded**: Every LLM output is validated against source data before display
3. **Graceful Degradation**: System fully functional without LLM via template fallbacks
4. **Transparency**: Complete audit trail of all decisions and negotiations
5. **Fairness**: Gini coefficient monitoring with automatic redistribution
