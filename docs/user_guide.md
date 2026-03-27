# User Guide — Multi-Agent Disaster Response System

## Getting Started

### 1. Installation
```bash
cd disaster-response-system
pip install -r requirements.txt
```

### 2. Launch the Dashboard
```bash
python -m streamlit run app/dashboard.py
```
The dashboard opens at `http://localhost:8501`.

### 3. (Optional) Enable AI Features
```bash
# Install Ollama from https://ollama.ai
ollama pull mistral
# Restart the dashboard — LLM features auto-detect
```

---

## Using the Dashboard

### Step 1: Select a Scenario
Use the **Scenario Selection** dropdown in the sidebar to choose from:
- **Major Earthquake** (5 zones, 15 steps, 150 resources)
- **Severe Flooding** (6 zones, 18 steps, 180 resources)
- **Urban Industrial Accident** (4 zones, 12 steps, 100 resources)

### Step 2: Start the Simulation
Click **🚀 Start** to initialize. The system creates 4 agents and prepares the simulation.

### Step 3: Run Steps
- **⏭️ Step**: Execute one time step (observe decisions round by round)
- **⏩ Run All**: Execute all remaining steps at once

### Step 4: Explore the Tabs

| Tab | What You'll See |
|-----|----------------|
| **🗺️ Simulation Overview** | Zone status cards, resource pool, dynamic events |
| **🤖 Agent Decisions** | Radar chart of agent weights, proposals table, negotiation log |
| **⚖️ Allocation & Fairness** | Resource distribution bars, Gini coefficient, per-zone breakdown |
| **📈 Analytics & Charts** | Time-series performance, decision heatmap, weight evolution |
| **🧠 AI Explainability** | AI explanation panel, Ask AI, Generate Insights |

### Step 5: AI Explainability (Tab 5)
- **Explain Current Step**: Generates a natural-language explanation
- **Ask AI**: Type questions like "Why did Zone C get fewer resources?"
- **Generate Insights**: After simulation, get a full narrative report

---

## Key Metrics to Watch

| Metric | Target | Meaning |
|--------|--------|---------|
| Response Coverage | > 70% | Average resource coverage across zones |
| Gini Coefficient | < 0.30 | Equity (0 = perfectly equal, 1 = one zone gets everything) |
| Resilience Index | > 0.60 | Long-term recovery potential |
| Resource Utilization | > 90% | Fraction of resources deployed |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "streamlit not found" | Use `python -m streamlit run app/dashboard.py` |
| AI shows "Template Mode" | Install Ollama and run `ollama pull mistral` |
| Fuzzy logic import error | Run `pip install scikit-fuzzy` |
