"""
Streamlit Dashboard Module
Complete interactive web dashboard with 5 tabs per Section 8.1.
Tab 1: Simulation Overview
Tab 2: Agent Decisions
Tab 3: Allocation & Fairness
Tab 4: Analytics & Charts
Tab 5: AI Explainability (LLM)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from app.controller import Controller
from visualization.charts import Charts
from visualization.metrics_display import MetricsDisplay
from data.scenarios.scenario_definitions import list_scenarios, get_scenario


def init_session_state():
    """Initialize Streamlit session state."""
    if "controller" not in st.session_state:
        st.session_state.controller = Controller()
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    if "step_results" not in st.session_state:
        st.session_state.step_results = []
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    if "simulation_complete" not in st.session_state:
        st.session_state.simulation_complete = False
    if "scenario_narration" not in st.session_state:
        st.session_state.scenario_narration = ""
    if "llm_explanations" not in st.session_state:
        st.session_state.llm_explanations = {}
    if "ask_ai_history" not in st.session_state:
        st.session_state.ask_ai_history = []
    if "insight_report" not in st.session_state:
        st.session_state.insight_report = ""


def render_header():
    """Render the dashboard header."""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 20px; border-radius: 10px; margin-bottom: 20px;
        text-align: center;
    }
    .main-header h1 { color: #4ECDC4; margin: 0; font-size: 28px; }
    .main-header p { color: #aaa; margin: 5px 0 0; font-size: 14px; }
    .zone-card {
        background: #1a1a2e; padding: 15px; border-radius: 8px;
        border-left: 4px solid #4ECDC4; margin-bottom: 10px;
    }
    .metric-good { color: #4ECDC4; }
    .metric-warning { color: #FFEAA7; }
    .metric-bad { color: #FF6B6B; }
    .ai-panel {
        background: #1a1a2e; padding: 15px; border-radius: 8px;
        border: 1px solid #45B7D1; margin: 10px 0;
    }
    .ai-label { color: #45B7D1; font-size: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 5, 2])
    with col2:
        st.markdown("## 🚨 Multi-Agent Disaster Response System")
        st.markdown("*AI-Powered Resource Allocation with AHP, Fuzzy Logic & LLM Explainability*")


def render_sidebar():
    """Render the sidebar with scenario selection and controls."""
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")
        st.divider()

        # Scenario Selection
        st.markdown("#### 📋 Scenario Selection")
        scenarios = list_scenarios()
        scenario_names = {s["name"]: s["id"] for s in scenarios}
        selected_name = st.selectbox("Choose Disaster Scenario", list(scenario_names.keys()))
        selected_id = scenario_names[selected_name]

        # Show scenario details
        scenario = get_scenario(selected_id)
        st.markdown(f"**Type:** {scenario['type']}")
        st.markdown(f"**Zones:** {len(scenario['zones'])}")
        st.markdown(f"**Duration:** {scenario['duration']} steps")
        st.markdown(f"**Resources:** {scenario['total_resources']} units")

        st.divider()

        # Simulation Controls
        st.markdown("#### ▶️ Simulation Controls")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Start", use_container_width=True):
                controller = st.session_state.controller
                controller.initialize_simulation(selected_id)
                st.session_state.initialized = True
                st.session_state.simulation_complete = False
                st.session_state.step_results = []
                st.session_state.current_step = 0
                st.session_state.scenario_narration = controller.get_scenario_narration()
                st.session_state.llm_explanations = {}
                st.session_state.ask_ai_history = []
                st.session_state.insight_report = ""
                st.rerun()

        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.initialized = False
                st.session_state.step_results = []
                st.session_state.simulation_complete = False
                st.session_state.current_step = 0
                st.rerun()

        if st.session_state.initialized and not st.session_state.simulation_complete:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏭️ Step", use_container_width=True):
                    result = st.session_state.controller.run_step()
                    if "error" not in result:
                        st.session_state.step_results.append(result)
                        st.session_state.current_step += 1
                        if st.session_state.controller.sim_engine.is_complete:
                            st.session_state.simulation_complete = True
                    st.rerun()
            with col2:
                if st.button("⏩ Run All", use_container_width=True):
                    results = st.session_state.controller.run_all_steps()
                    st.session_state.step_results.extend(results)
                    st.session_state.current_step += len(results)
                    st.session_state.simulation_complete = True
                    st.rerun()

        st.divider()

        # Status
        st.markdown("#### 📊 Status")
        if st.session_state.initialized:
            state = st.session_state.controller.get_current_state()
            st.markdown(f"**Step:** {state.get('step', 0)} / {state.get('total_steps', 0)}")
            st.markdown(f"**Phase:** {state.get('phase', 'N/A')}")
            llm_status = "🟢 Active" if state.get("llm_available") else "🟡 Template Mode"
            st.markdown(f"**🤖 AI:** {llm_status}")
            if st.session_state.simulation_complete:
                st.success("✅ Simulation Complete")
        else:
            st.info("Select a scenario and click Start")


def render_tab_overview():
    """Tab 1: Simulation Overview — zone status cards and resource pool."""
    if not st.session_state.initialized:
        st.info("👈 Select a scenario and click **Start** to begin.")
        return

    # Scenario narration
    if st.session_state.scenario_narration:
        st.markdown("##### 🤖 AI Scenario Briefing")
        st.markdown(f"<div class='ai-panel'><span class='ai-label'>🤖 AI-Generated (based on system data)</span><br><br>{st.session_state.scenario_narration}</div>", unsafe_allow_html=True)

    state = st.session_state.controller.get_current_state()
    zones = state.get("zones", [])

    # Resource pool
    remaining = state.get("remaining_resources", 0)
    total = state["environment"]["total_resources"]
    st.progress(remaining / total if total > 0 else 0, text=f"Resources: {remaining:.0f} / {total} units available")

    # Zone status cards
    st.markdown("##### 🗺️ Zone Status")
    cols = st.columns(min(3, len(zones)))
    for i, zone in enumerate(zones):
        with cols[i % len(cols)]:
            severity_color = "#FF6B6B" if zone["current_severity"] >= 7 else "#FFEAA7" if zone["current_severity"] >= 4 else "#4ECDC4"
            st.markdown(f"""
            <div class='zone-card'>
                <h4 style='color:{severity_color};margin:0'>{zone['name']}</h4>
                <p style='margin:3px 0;color:#ccc'>Severity: <b style='color:{severity_color}'>{zone['current_severity']:.1f}</b>/10</p>
                <p style='margin:3px 0;color:#ccc'>Population: {zone['population']:,}</p>
                <p style='margin:3px 0;color:#ccc'>At Risk: {zone['population_at_risk']:,}</p>
                <p style='margin:3px 0;color:#ccc'>Accessibility: {zone['accessibility']:.1f}/10</p>
                <p style='margin:3px 0;color:#ccc'>Unmet Demand: {zone['unmet_demand']:.1f}</p>
                <p style='margin:3px 0;color:#ccc'>Resilience: {zone['resilience_index']:.3f}</p>
            </div>
            """, unsafe_allow_html=True)

    # Recent events
    if st.session_state.step_results:
        latest = st.session_state.step_results[-1]
        events = latest.get("events", [])
        if events:
            st.markdown("##### ⚡ Recent Events")
            for e in events:
                st.warning(f"**{e['type'].replace('_', ' ').title()}** — {e['zone']}: {e['description']}")


def render_tab_agents():
    """Tab 2: Agent Decisions — proposals, negotiation logs, consensus."""
    if not st.session_state.step_results:
        st.info("Run at least one simulation step to see agent decisions.")
        return

    latest = st.session_state.step_results[-1]
    nr = latest.get("allocation_result", {}).get("negotiation_result", {})

    # Agent weight comparison
    st.markdown("##### 🕸️ Agent Criteria Weights")
    agent_states = nr.get("agent_states", {})
    agent_weights = {at: s.get("weights", {}) for at, s in agent_states.items()}
    if agent_weights:
        fig = Charts.agent_priority_radar(agent_weights)
        st.plotly_chart(fig, use_container_width=True)

    # Per-agent proposals
    st.markdown("##### 📝 Agent Proposals")
    proposals = nr.get("proposals", {})
    if proposals:
        df = pd.DataFrame(proposals).T
        df.index.name = "Agent"
        st.dataframe(df.style.format("{:.1f}").background_gradient(cmap="YlOrRd", axis=1), use_container_width=True)

    # Negotiation rounds
    st.markdown("##### 🤝 Negotiation Log")
    record = nr.get("negotiation_record", {})
    rounds = record.get("rounds", [])
    for r in rounds:
        with st.expander(f"Round {r['round']}: {r['name']}", expanded=(r['round'] >= 4)):
            st.markdown(f"*{r.get('description', '')}*")
            if "contested_zones" in r:
                if r["contested_zones"]:
                    st.warning(f"Contested: {', '.join(r['contested_zones'])}")
                else:
                    st.success("All zones agreed upon")
            if "final_allocation" in r:
                st.json(r["final_allocation"])
            if "dissent_scores" in r:
                for agent, score in r["dissent_scores"].items():
                    bar_color = "🔴" if score > 0.3 else "🟡" if score > 0.1 else "🟢"
                    st.markdown(f"{bar_color} **{agent}**: Dissent = {score:.3f}")

    # Consensus vs proposals chart
    st.markdown("##### 📊 Proposals vs Consensus")
    consensus = latest.get("final_allocation", {})
    fig = Charts.negotiation_divergence(proposals, consensus)
    st.plotly_chart(fig, use_container_width=True)


def render_tab_allocation():
    """Tab 3: Allocation & Fairness — distribution charts, Gini tracking."""
    if not st.session_state.step_results:
        st.info("Run at least one simulation step to see allocation data.")
        return

    latest = st.session_state.step_results[-1]
    allocations = latest.get("final_allocation", {})
    zones = latest.get("post_state", [])
    fairness = latest.get("allocation_result", {}).get("fairness_after", {})

    # Allocation bar chart
    st.markdown("##### 📊 Resource Distribution")
    fig = Charts.resource_allocation_bar(allocations, f"Step {latest['step']} Allocation")
    st.plotly_chart(fig, use_container_width=True)

    # Fairness metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        gini = fairness.get("gini_coefficient", 0)
        color = "metric-good" if gini < 0.3 else "metric-warning" if gini < 0.4 else "metric-bad"
        st.metric("Gini Coefficient", f"{gini:.3f}", delta=f"{'✓' if gini < 0.3 else '⚠'} Target: < 0.30")
    with col2:
        min_cov = fairness.get("min_coverage_ratio", 0)
        st.metric("Min Coverage Ratio", f"{min_cov:.3f}", delta=f"{'✓' if min_cov > 0.4 else '⚠'} Target: > 0.40")
    with col3:
        was_redis = latest.get("allocation_result", {}).get("was_redistributed", False)
        st.metric("Redistributed?", "Yes" if was_redis else "No")

    # Fairness distribution
    st.markdown("##### ⚖️ Fairness Distribution")
    fig = Charts.fairness_distribution(zones, allocations)
    st.plotly_chart(fig, use_container_width=True)

    # Per-zone allocation breakdown
    st.markdown("##### 📋 Per-Zone Breakdown")
    breakdown = []
    for zone in zones:
        name = zone["name"]
        breakdown.append({
            "Zone": name,
            "Allocated": allocations.get(name, 0),
            "Severity": zone["current_severity"],
            "Population": zone["population"],
            "Unmet Demand": zone["unmet_demand"],
            "Resilience": zone["resilience_index"]
        })
    st.dataframe(pd.DataFrame(breakdown).set_index("Zone").style.format({
        "Allocated": "{:.1f}", "Severity": "{:.1f}", "Unmet Demand": "{:.1f}", "Resilience": "{:.3f}"
    }).background_gradient(subset=["Allocated"], cmap="YlOrRd"), use_container_width=True)


def render_tab_analytics():
    """Tab 4: Analytics & Charts — time-series, heatmap, weight evolution."""
    if not st.session_state.step_results:
        st.info("Run the simulation to see analytics.")
        return

    controller = st.session_state.controller
    summary = controller.get_simulation_summary()
    metrics_history = summary.get("metrics_history", [])

    # Time-series performance
    st.markdown("##### 📈 Performance Over Time")
    fig = Charts.time_series_metrics(metrics_history)
    st.plotly_chart(fig, use_container_width=True)

    # Decision heatmap
    st.markdown("##### 🗺️ Decision Heatmap")
    allocation_history = summary.get("allocation_history", [])
    zone_names = summary.get("scenario", {}).get("zone_count", 0)
    env = controller.sim_engine.environment if controller.sim_engine else None
    z_names = env.zone_names if env else []
    fig = Charts.decision_heatmap(allocation_history, z_names)
    st.plotly_chart(fig, use_container_width=True)

    # AI Coordinator weight evolution
    st.markdown("##### 🔄 AI Coordinator Weight Evolution")
    ai_weights = summary.get("ai_weight_history", [])
    if ai_weights:
        fig = Charts.criteria_weight_evolution(ai_weights)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run multiple steps to see weight evolution.")

    # Performance scorecard
    if st.session_state.simulation_complete:
        st.markdown("##### 🏆 Performance Scorecard")
        scorecard = MetricsDisplay.get_performance_scorecard(metrics_history)
        cols = st.columns(len(scorecard["scores"]))
        for i, score in enumerate(scorecard["scores"]):
            with cols[i]:
                st.markdown(f"**{score['status']} {score['metric']}**")
                st.markdown(f"Value: `{score['value']:.3f}`")
                st.markdown(f"Target: `{score['target']}`")
        st.markdown(f"### Overall: **{scorecard['overall']}**")


def render_tab_ai():
    """Tab 5: AI Explainability — explanation panel, Ask AI, Generate Insights."""
    controller = st.session_state.controller

    # --- AI Explanation Panel ---
    st.markdown("##### 🤖 AI Explanation Panel")
    st.markdown("<span class='ai-label'>AI-Generated Explanation (based on system data)</span>", unsafe_allow_html=True)

    if st.session_state.step_results:
        latest = st.session_state.step_results[-1]
        step_idx = latest["step"]

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Explain Current Step"):
                explanation = controller.get_llm_explanation(latest)
                st.session_state.llm_explanations[step_idx] = explanation
        with col2:
            if len(st.session_state.step_results) > 1:
                if st.button("⏮️ Explain Previous Step"):
                    prev = st.session_state.step_results[-2]
                    explanation = controller.get_llm_explanation(prev)
                    st.session_state.llm_explanations[prev["step"]] = explanation

        # Display explanations
        if step_idx in st.session_state.llm_explanations:
            st.markdown(f"<div class='ai-panel'>{st.session_state.llm_explanations[step_idx]}</div>", unsafe_allow_html=True)
        elif latest.get("template_explanation"):
            st.markdown(f"<div class='ai-panel'>{latest['template_explanation']}</div>", unsafe_allow_html=True)

        # Trade-off analysis
        tradeoffs = latest.get("tradeoffs", {}).get("tradeoffs", [])
        if tradeoffs:
            st.markdown("##### 🔄 Trade-off Analysis")
            for t in tradeoffs:
                severity_icon = "🔴" if t["severity"] == "high" else "🟡" if t["severity"] == "moderate" else "🟢"
                st.markdown(f"{severity_icon} **{t['type']}**: {t['description']}")
    else:
        st.info("Run a simulation step to generate explanations.")

    st.divider()

    # --- Ask AI ---
    st.markdown("##### 💬 Ask AI")
    st.markdown("*Ask questions about the simulation (answers based on system data only)*")

    user_question = st.text_input("Your question:", placeholder="Why did Zone C receive fewer resources?")
    if st.button("🔍 Ask") and user_question:
        response = controller.get_llm_query_response(user_question)
        st.session_state.ask_ai_history.append({"question": user_question, "answer": response})

    for qa in reversed(st.session_state.ask_ai_history):
        st.markdown(f"**Q:** {qa['question']}")
        st.markdown(f"<div class='ai-panel'><span class='ai-label'>🤖 AI Response</span><br>{qa['answer']}</div>", unsafe_allow_html=True)

    st.divider()

    # --- Generate Insights ---
    st.markdown("##### 📊 Generate Insights")
    if st.session_state.simulation_complete:
        if st.button("📋 Generate Full Simulation Report"):
            report = controller.get_llm_insights()
            st.session_state.insight_report = report

        if st.session_state.insight_report:
            st.markdown("<div class='ai-panel'><span class='ai-label'>🤖 AI-Generated Report</span><br><br>", unsafe_allow_html=True)
            st.markdown(st.session_state.insight_report)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Complete the simulation to generate insights.")


def render_footer():
    """Render the dashboard footer with KPI summary."""
    if not st.session_state.step_results:
        return

    latest = st.session_state.step_results[-1]
    metrics = latest.get("metrics", {})
    kpi_cards = MetricsDisplay.get_kpi_cards(metrics)

    st.divider()
    cols = st.columns(len(kpi_cards))
    for i, card in enumerate(kpi_cards):
        with cols[i]:
            color = {"good": "#4ECDC4", "warning": "#FFEAA7", "bad": "#FF6B6B"}.get(card["status"], "#ccc")
            st.markdown(f"""
            <div style='text-align:center;padding:10px;background:#1a1a2e;border-radius:8px;border-top:3px solid {color}'>
                <p style='margin:0;font-size:20px'>{card['icon']}</p>
                <p style='margin:2px 0;color:#888;font-size:11px'>{card['label']}</p>
                <p style='margin:2px 0;color:{color};font-size:18px;font-weight:bold'>{card['value']}</p>
                <p style='margin:0;color:#666;font-size:10px'>Target: {card['target']}</p>
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main dashboard entry point."""
    st.set_page_config(
        page_title="Disaster Response MAS",
        page_icon="🚨",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()
    render_header()
    render_sidebar()

    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Simulation Overview",
        "🤖 Agent Decisions",
        "⚖️ Allocation & Fairness",
        "📈 Analytics & Charts",
        "🧠 AI Explainability"
    ])

    with tab1:
        render_tab_overview()
    with tab2:
        render_tab_agents()
    with tab3:
        render_tab_allocation()
    with tab4:
        render_tab_analytics()
    with tab5:
        render_tab_ai()

    render_footer()


if __name__ == "__main__":
    main()
