"""
Streamlit Dashboard — Dark Operations Center Theme
Premium UI with 6 tabs, live stats bar, agent cards, AHP/Fuzzy panels.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from app.controller import Controller
from visualization.charts import Charts
from visualization.metrics_display import MetricsDisplay
from data.scenarios.scenario_definitions import list_scenarios, get_scenario

# ─── COLOR PALETTE ───
C = {
    "bg": "#0a0a0f", "panel": "#111119", "panel_border": "#1e1e2e",
    "accent": "#00d4aa", "warn": "#ff6b35", "danger": "#ff3b30",
    "ai": "#a855f7", "blue": "#007aff", "text": "#e0e0e0", "dim": "#666",
    "emergency": "#ff3b30", "ngo": "#34c759", "gov": "#007aff", "ai_agent": "#a855f7",
}

def get_css():
    return f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
*, .stApp, .stMarkdown, .stTabs, p, span, label, h1, h2, h3, h4, h5, h6 {{ font-family: 'Inter', sans-serif !important; }}
.stApp {{ background: {C['bg']} !important; color: {C['text']}; }}
header[data-testid="stHeader"] {{ background: {C['bg']} !important; }}
section[data-testid="stSidebar"] {{ background: #0d0d14 !important; border-right: 1px solid {C['panel_border']}; }}
section[data-testid="stSidebar"] * {{ color: {C['text']} !important; }}
.stTabs [data-baseweb="tab-list"] {{ background: {C['panel']}; border-radius: 8px; padding: 4px; gap: 0; border: 1px solid {C['panel_border']}; }}
.stTabs [data-baseweb="tab"] {{ background: transparent; color: {C['dim']} !important; border-radius: 6px; padding: 8px 16px; font-size: 13px; font-weight: 500; }}
.stTabs [aria-selected="true"] {{ background: {C['accent']}22 !important; color: {C['accent']} !important; border-bottom: 2px solid {C['accent']}; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 16px; }}
div[data-testid="stMetric"] {{ background: {C['panel']}; border: 1px solid {C['panel_border']}; border-radius: 8px; padding: 12px; }}
div[data-testid="stMetric"] label {{ color: {C['dim']} !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: {C['accent']} !important; font-weight: 700; }}
.stDataFrame {{ border: 1px solid {C['panel_border']}; border-radius: 8px; }}
.stProgress > div > div {{ background: {C['accent']} !important; }}
.stButton > button {{ background: {C['panel']} !important; color: {C['accent']} !important; border: 1px solid {C['accent']}44 !important; border-radius: 6px !important; font-weight: 500; transition: all 0.2s; }}
.stButton > button:hover {{ background: {C['accent']}22 !important; border-color: {C['accent']} !important; }}
.stSelectbox > div > div {{ background: {C['panel']} !important; border-color: {C['panel_border']} !important; color: {C['text']} !important; }}
.stTextInput > div > div > input {{ background: {C['panel']} !important; border-color: {C['panel_border']} !important; color: {C['text']} !important; }}
.stats-bar {{ display:flex; gap:16px; background:{C['panel']}; border:1px solid {C['panel_border']}; border-radius:10px; padding:10px 20px; margin-bottom:16px; align-items:center; }}
.stat-item {{ text-align:center; flex:1; }}
.stat-label {{ font-size:10px; color:{C['dim']}; text-transform:uppercase; letter-spacing:1.5px; font-weight:600; }}
.stat-value {{ font-size:20px; font-weight:700; color:{C['text']}; margin-top:2px; }}
.stat-value.teal {{ color:{C['accent']}; }}
.stat-value.red {{ color:{C['danger']}; }}
.stat-value.orange {{ color:{C['warn']}; }}
.stat-value.purple {{ color:{C['ai']}; }}
.stat-divider {{ width:1px; height:36px; background:{C['panel_border']}; }}
.panel {{ background:{C['panel']}; border:1px solid {C['panel_border']}; border-radius:10px; padding:16px; margin-bottom:12px; }}
.panel-title {{ font-size:12px; color:{C['dim']}; text-transform:uppercase; letter-spacing:1.5px; font-weight:600; margin-bottom:12px; }}
.agent-card {{ background:{C['panel']}; border:1px solid {C['panel_border']}; border-radius:10px; padding:14px; margin-bottom:10px; display:flex; align-items:center; gap:12px; transition: border-color 0.2s; }}
.agent-card:hover {{ border-color: #333; }}
.agent-badge {{ width:10px; height:10px; border-radius:50%; flex-shrink:0; }}
.agent-name {{ font-size:14px; font-weight:600; color:{C['text']}; }}
.agent-role {{ font-size:11px; color:{C['dim']}; }}
.agent-status {{ font-size:11px; padding:2px 10px; border-radius:12px; font-weight:500; margin-left:auto; }}
.zone-card {{ background:{C['panel']}; border:1px solid {C['panel_border']}; border-radius:10px; padding:14px; margin-bottom:10px; position:relative; overflow:hidden; }}
.zone-card::before {{ content:''; position:absolute; top:0; left:0; width:4px; height:100%; }}
.zone-critical::before {{ background:{C['danger']}; }}
.zone-severe::before {{ background:{C['warn']}; }}
.zone-moderate::before {{ background:{C['accent']}; }}
.zone-name {{ font-size:14px; font-weight:600; margin-bottom:6px; }}
.zone-detail {{ font-size:12px; color:{C['dim']}; margin:3px 0; }}
.zone-sev-badge {{ font-size:10px; padding:2px 8px; border-radius:10px; font-weight:600; display:inline-block; }}
.badge-critical {{ background:{C['danger']}22; color:{C['danger']}; }}
.badge-severe {{ background:{C['warn']}22; color:{C['warn']}; }}
.badge-moderate {{ background:{C['accent']}22; color:{C['accent']}; }}
.ahp-bar-wrap {{ margin:6px 0; }}
.ahp-bar-label {{ display:flex; justify-content:space-between; font-size:12px; margin-bottom:3px; }}
.ahp-bar-label span:first-child {{ color:{C['dim']}; }}
.ahp-bar-label span:last-child {{ color:{C['text']}; font-weight:600; }}
.ahp-bar {{ height:6px; background:#1a1a2e; border-radius:3px; overflow:hidden; }}
.ahp-bar-fill {{ height:100%; border-radius:3px; transition:width 0.5s; }}
.fuzzy-row {{ display:flex; align-items:center; gap:8px; margin:6px 0; padding:8px 10px; background:{C['bg']}; border-radius:6px; }}
.fuzzy-zone {{ width:70px; font-size:12px; font-weight:500; flex-shrink:0; }}
.fuzzy-bar-bg {{ flex:1; height:6px; background:#1a1a2e; border-radius:3px; position:relative; }}
.fuzzy-bar-fill {{ height:100%; border-radius:3px; }}
.fuzzy-label {{ font-size:10px; font-weight:600; width:60px; text-align:right; flex-shrink:0; }}
.ai-panel {{ background:{C['bg']}; border:1px solid {C['ai']}33; border-radius:10px; padding:14px; margin:8px 0; }}
.ai-tag {{ font-size:10px; color:{C['ai']}; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }}
.live-dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; background:{C['accent']}; margin-right:6px; animation:pulse 1.5s infinite; }}
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}
.kpi-card {{ background:{C['panel']}; border:1px solid {C['panel_border']}; border-radius:10px; padding:12px; text-align:center; }}
.kpi-card .kpi-icon {{ font-size:20px; }}
.kpi-card .kpi-label {{ font-size:10px; color:{C['dim']}; text-transform:uppercase; letter-spacing:1px; margin:4px 0 2px; }}
.kpi-card .kpi-val {{ font-size:18px; font-weight:700; }}
.kpi-card .kpi-target {{ font-size:10px; color:{C['dim']}; }}
.neg-round {{ background:{C['bg']}; border:1px solid {C['panel_border']}; border-radius:8px; padding:10px 14px; margin:6px 0; }}
.neg-round-title {{ font-size:12px; font-weight:600; color:{C['accent']}; }}
.neg-round-desc {{ font-size:11px; color:{C['dim']}; }}
</style>"""


def init_session_state():
    defaults = {
        "controller": Controller(), "initialized": False, "step_results": [],
        "current_step": 0, "simulation_complete": False, "scenario_narration": "",
        "llm_explanations": {}, "ask_ai_history": [], "insight_report": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_live_stats():
    if not st.session_state.initialized:
        return {"step": "00", "total": "00", "critical": 0, "pending": 0, "cost": 0, "status": "STANDBY", "phase": "—"}
    state = st.session_state.controller.get_current_state()
    zones = state.get("zones", [])
    critical = sum(1 for z in zones if z["current_severity"] >= 7)
    pending = sum(1 for z in zones if z["unmet_demand"] > 5)
    cost = sum(r.get("metrics", {}).get("total_cost", 0) for r in st.session_state.step_results)
    status = "COMPLETE" if st.session_state.simulation_complete else "LIVE" if st.session_state.step_results else "READY"
    return {"step": f"{state.get('step',0):02d}", "total": f"{state.get('total_steps',0):02d}",
            "critical": critical, "pending": pending, "cost": int(cost),
            "status": status, "phase": state.get("phase", "—")}


def render_stats_bar():
    s = get_live_stats()
    dot = "<span class='live-dot'></span>" if s["status"] == "LIVE" else ""
    status_color = "teal" if s["status"] == "LIVE" else "orange" if s["status"] == "READY" else "purple" if s["status"] == "COMPLETE" else ""
    st.markdown(f"""<div class="stats-bar">
        <div style="font-size:16px;font-weight:700;color:{C['accent']};letter-spacing:1px;margin-right:8px;">⚡ ESARS</div>
        <div class="stat-divider"></div>
        <div class="stat-item"><div class="stat-label">Steps</div><div class="stat-value teal">{s['step']}:{s['total']}</div></div>
        <div class="stat-divider"></div>
        <div class="stat-item"><div class="stat-label">Critical</div><div class="stat-value red">{s['critical']}</div></div>
        <div class="stat-divider"></div>
        <div class="stat-item"><div class="stat-label">Pending</div><div class="stat-value orange">{s['pending']}</div></div>
        <div class="stat-divider"></div>
        <div class="stat-item"><div class="stat-label">Cost</div><div class="stat-value">${s['cost']:,}</div></div>
        <div class="stat-divider"></div>
        <div class="stat-item"><div class="stat-label">Phase</div><div class="stat-value" style="font-size:13px">{s['phase']}</div></div>
        <div class="stat-divider"></div>
        <div class="stat-item"><div class="stat-label">Status</div><div class="stat-value {status_color}">{dot}{s['status']}</div></div>
    </div>""", unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown(f"<div style='text-align:center;padding:10px 0'><span style='font-size:22px;font-weight:700;color:{C['accent']};letter-spacing:2px'>⚡ ESARS</span><br><span style='font-size:10px;color:{C['dim']};letter-spacing:1px'>MULTI-AGENT DISASTER RESPONSE</span></div>", unsafe_allow_html=True)
        st.divider()
        scenarios = list_scenarios()
        scenario_map = {s["name"]: s["id"] for s in scenarios}
        selected = st.selectbox("Scenario", list(scenario_map.keys()), label_visibility="collapsed")
        sid = scenario_map[selected]
        sc = get_scenario(sid)
        st.markdown(f"""<div class="panel" style="padding:10px">
            <div style="font-size:11px;color:{C['dim']};margin-bottom:6px">SCENARIO DETAILS</div>
            <div style="font-size:12px;margin:3px 0"><span style="color:{C['dim']}">Type:</span> <b>{sc['type'].title()}</b></div>
            <div style="font-size:12px;margin:3px 0"><span style="color:{C['dim']}">Zones:</span> <b>{len(sc['zones'])}</b></div>
            <div style="font-size:12px;margin:3px 0"><span style="color:{C['dim']}">Steps:</span> <b>{sc['duration']}</b></div>
            <div style="font-size:12px;margin:3px 0"><span style="color:{C['dim']}">Resources:</span> <b>{sc['total_resources']} units</b></div>
        </div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            start = st.button("▶ START", use_container_width=True)
        with c2:
            reset = st.button("⟲ RESET", use_container_width=True)
        if start:
            ctrl = st.session_state.controller
            ctrl.initialize_simulation(sid)
            st.session_state.update({"initialized": True, "simulation_complete": False, "step_results": [], "current_step": 0,
                                     "scenario_narration": ctrl.get_scenario_narration(), "llm_explanations": {}, "ask_ai_history": [], "insight_report": ""})
            st.rerun()
        if reset:
            st.session_state.update({"initialized": False, "step_results": [], "simulation_complete": False, "current_step": 0})
            st.rerun()
        if st.session_state.initialized and not st.session_state.simulation_complete:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⏭ STEP", use_container_width=True):
                    r = st.session_state.controller.run_step()
                    if "error" not in r:
                        st.session_state.step_results.append(r)
                        st.session_state.current_step += 1
                        if st.session_state.controller.sim_engine.is_complete:
                            st.session_state.simulation_complete = True
                    st.rerun()
            with c2:
                if st.button("⏩ ALL", use_container_width=True):
                    results = st.session_state.controller.run_all_steps()
                    st.session_state.step_results.extend(results)
                    st.session_state.current_step += len(results)
                    st.session_state.simulation_complete = True
                    st.rerun()
        if st.session_state.simulation_complete:
            st.markdown(f"<div style='text-align:center;padding:8px;background:{C['accent']}15;border:1px solid {C['accent']}33;border-radius:8px;color:{C['accent']};font-size:12px;font-weight:600;margin-top:8px'>✓ SIMULATION COMPLETE</div>", unsafe_allow_html=True)
        llm_status = "ACTIVE" if st.session_state.initialized and st.session_state.controller.get_current_state().get("llm_available") else "TEMPLATE"
        llm_color = C['accent'] if llm_status == "ACTIVE" else C['warn']
        st.markdown(f"<div style='text-align:center;margin-top:12px;font-size:10px;color:{llm_color}'>🤖 AI: {llm_status}</div>", unsafe_allow_html=True)
    return sid


def sev_class(s):
    return ("critical" if s >= 7 else "severe" if s >= 4 else "moderate")

def sev_label(s):
    c = sev_class(s)
    return f"<span class='zone-sev-badge badge-{c}'>{c.upper()}</span>"


def render_tab_overview():
    if not st.session_state.initialized:
        st.markdown(f"<div class='panel' style='text-align:center;padding:40px'><span style='font-size:14px;color:{C['dim']}'>Select a scenario and click <b style=\"color:{C['accent']}\">▶ START</b> to begin</span></div>", unsafe_allow_html=True)
        return
    if st.session_state.scenario_narration:
        st.markdown(f"""<div class="ai-panel"><div class="ai-tag">🤖 AI Scenario Briefing</div><div style="font-size:13px;color:{C['text']};line-height:1.6">{st.session_state.scenario_narration}</div></div>""", unsafe_allow_html=True)
    state = st.session_state.controller.get_current_state()
    zones = state.get("zones", [])
    remaining = state.get("remaining_resources", 0)
    total = state["environment"]["total_resources"]
    pct = remaining / total if total > 0 else 0
    bar_color = C['accent'] if pct > 0.4 else C['warn'] if pct > 0.15 else C['danger']
    st.markdown(f"""<div class="panel"><div class="panel-title">Resource Pool</div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px"><span style="color:{C['dim']}">Available</span><span style="font-weight:600">{remaining:.0f} / {total}</span></div>
        <div style="height:8px;background:#1a1a2e;border-radius:4px;overflow:hidden"><div style="width:{pct*100}%;height:100%;background:{bar_color};border-radius:4px;transition:width 0.5s"></div></div></div>""", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>Disaster Zones</div>", unsafe_allow_html=True)
    cols = st.columns(min(3, len(zones)))
    for i, z in enumerate(zones):
        sc = sev_class(z["current_severity"])
        with cols[i % len(cols)]:
            st.markdown(f"""<div class="zone-card zone-{sc}">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                    <span class="zone-name">{z['name']}</span>{sev_label(z['current_severity'])}
                </div>
                <div class="zone-detail">Severity: <b style="color:{'#ff3b30' if sc=='critical' else '#ff6b35' if sc=='severe' else C['accent']}">{z['current_severity']:.1f}</b>/10</div>
                <div class="zone-detail">Population: <b>{z['population']:,}</b></div>
                <div class="zone-detail">Accessibility: <b>{z['accessibility']:.1f}</b>/10</div>
                <div class="zone-detail">Unmet Demand: <b>{z['unmet_demand']:.1f}</b></div>
                <div class="zone-detail">Resilience: <b>{z['resilience_index']:.3f}</b></div>
            </div>""", unsafe_allow_html=True)
    if st.session_state.step_results:
        latest = st.session_state.step_results[-1]
        events = latest.get("events", [])
        if events:
            st.markdown("<div class='panel-title'>⚡ Dynamic Events</div>", unsafe_allow_html=True)
            for e in events:
                st.markdown(f"<div class='neg-round'><span class='neg-round-title'>⚠ {e['type'].replace('_',' ').title()}</span> — <span class='neg-round-desc'>{e['zone']}: {e['description']}</span></div>", unsafe_allow_html=True)


def render_tab_agents():
    if not st.session_state.step_results:
        st.markdown(f"<div class='panel' style='text-align:center;padding:30px;color:{C['dim']}'>Run a simulation step to see agent data</div>", unsafe_allow_html=True)
        return
    latest = st.session_state.step_results[-1]
    nr = latest.get("allocation_result", {}).get("negotiation_result", {})
    agent_info = [
        ("Emergency Response", C['emergency'], "Prioritizes speed & severity"),
        ("Government Agency", C['gov'], "Balances cost & coverage"),
        ("NGO", C['ngo'], "Advocates fairness & equity"),
        ("AI Coordinator", C['ai_agent'], "Data-driven optimization"),
    ]
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<div class='panel-title'>Agent Status</div>", unsafe_allow_html=True)
        proposals = nr.get("proposals", {})
        for name, color, role in agent_info:
            has_data = name in proposals
            status_bg = f"{color}22"
            st.markdown(f"""<div class="agent-card" style="border-left:3px solid {color}">
                <div><div class="agent-name">{name}</div><div class="agent-role">{role}</div></div>
                <div class="agent-status" style="background:{status_bg};color:{color}">{'Active' if has_data else 'Idle'}</div>
            </div>""", unsafe_allow_html=True)
        dissent = nr.get("negotiation_record", {}).get("rounds", [])
        if dissent:
            last_round = [r for r in dissent if "dissent_scores" in r]
            if last_round:
                st.markdown("<div class='panel-title' style='margin-top:16px'>Dissent Scores</div>", unsafe_allow_html=True)
                for agent, score in last_round[-1]["dissent_scores"].items():
                    color = C['danger'] if score > 0.3 else C['warn'] if score > 0.1 else C['accent']
                    st.markdown(f"""<div class="ahp-bar-wrap"><div class="ahp-bar-label"><span>{agent}</span><span style="color:{color}">{score:.3f}</span></div>
                        <div class="ahp-bar"><div class="ahp-bar-fill" style="width:{min(score*200,100)}%;background:{color}"></div></div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='panel-title'>Agent Proposals</div>", unsafe_allow_html=True)
        if proposals:
            df = pd.DataFrame(proposals).T
            df.index.name = "Agent"
            st.dataframe(df.style.format("{:.1f}").background_gradient(cmap="YlOrRd", axis=1), use_container_width=True)
        st.markdown("<div class='panel-title' style='margin-top:16px'>Proposals vs Consensus</div>", unsafe_allow_html=True)
        consensus = latest.get("final_allocation", {})
        fig = Charts.negotiation_divergence(proposals, consensus)
        st.plotly_chart(fig, use_container_width=True, key="neg_div")
    st.markdown("<div class='panel-title'>Negotiation Rounds</div>", unsafe_allow_html=True)
    record = nr.get("negotiation_record", {})
    for r in record.get("rounds", []):
        with st.expander(f"Round {r['round']}: {r['name']}", expanded=(r['round'] >= 4)):
            st.markdown(f"<span style='color:{C['dim']};font-size:12px'>{r.get('description','')}</span>", unsafe_allow_html=True)
            if "contested_zones" in r and r["contested_zones"]:
                st.warning(f"Contested: {', '.join(r['contested_zones'])}")
            if "final_allocation" in r:
                st.json(r["final_allocation"])


def render_tab_decision():
    if not st.session_state.step_results:
        st.markdown(f"<div class='panel' style='text-align:center;padding:30px;color:{C['dim']}'>Run a simulation step to see decision engine</div>", unsafe_allow_html=True)
        return
    latest = st.session_state.step_results[-1]
    nr = latest.get("allocation_result", {}).get("negotiation_result", {})
    agent_states = nr.get("agent_states", {})
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='panel'><div class='panel-title'>AHP Criteria Weights</div>", unsafe_allow_html=True)
        agent_weights = {at: s.get("weights", {}) for at, s in agent_states.items()}
        colors_map = {"Emergency Response": C['emergency'], "Government Agency": C['gov'], "NGO": C['ngo'], "AI Coordinator": C['ai_agent']}
        if agent_weights:
            first_agent = list(agent_weights.keys())[0]
            weights = agent_weights[first_agent]
            color = colors_map.get(first_agent, C['accent'])
            for criterion, val in weights.items():
                pct = val * 100
                st.markdown(f"""<div class="ahp-bar-wrap"><div class="ahp-bar-label"><span>{criterion.title()}</span><span>{pct:.0f}%</span></div>
                    <div class="ahp-bar"><div class="ahp-bar-fill" style="width:{pct*2}%;background:{color}"></div></div></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='panel'><div class='panel-title'>Radar Comparison</div>", unsafe_allow_html=True)
        if agent_weights:
            fig = Charts.agent_priority_radar(agent_weights)
            st.plotly_chart(fig, use_container_width=True, key="radar_de")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='panel'><div class='panel-title'>Fuzzy Urgency Assessment</div>", unsafe_allow_html=True)
        zones = latest.get("post_state", [])
        for z in zones:
            s = z["current_severity"]
            sc = sev_class(s)
            bar_color = C['danger'] if sc == "critical" else C['warn'] if sc == "severe" else C['accent']
            label_color = bar_color
            st.markdown(f"""<div class="fuzzy-row">
                <span class="fuzzy-zone">{z['name'][:12]}</span>
                <div class="fuzzy-bar-bg"><div class="fuzzy-bar-fill" style="width:{s*10}%;background:{bar_color}"></div></div>
                <span class="fuzzy-label" style="color:{label_color}">{sc.title()} {s:.1f}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='panel'><div class='panel-title'>Priority Matrix</div>", unsafe_allow_html=True)
        proposals = nr.get("proposals", {})
        if proposals:
            df = pd.DataFrame(proposals).T
            st.dataframe(df.style.format("{:.1f}").background_gradient(cmap="RdYlGn", axis=1), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_tab_allocation():
    if not st.session_state.step_results:
        st.markdown(f"<div class='panel' style='text-align:center;padding:30px;color:{C['dim']}'>Run a simulation step to see allocation data</div>", unsafe_allow_html=True)
        return
    latest = st.session_state.step_results[-1]
    alloc = latest.get("final_allocation", {})
    zones = latest.get("post_state", [])
    fairness = latest.get("allocation_result", {}).get("fairness_after", {})
    c1, c2, c3 = st.columns(3)
    gini = fairness.get("gini_coefficient", 0)
    min_cov = fairness.get("min_coverage_ratio", 0)
    was_redis = latest.get("allocation_result", {}).get("was_redistributed", False)
    with c1: st.metric("Gini Coefficient", f"{gini:.3f}", delta=f"{'✓ Fair' if gini < 0.3 else '⚠ Unequal'}")
    with c2: st.metric("Min Coverage", f"{min_cov:.3f}", delta=f"{'✓ OK' if min_cov > 0.4 else '⚠ Low'}")
    with c3: st.metric("Redistributed", "Yes ⟲" if was_redis else "No")
    col1, col2 = st.columns(2)
    with col1:
        fig = Charts.resource_allocation_bar(alloc, f"Step {latest['step']} Allocation")
        st.plotly_chart(fig, use_container_width=True, key="alloc_bar")
    with col2:
        fig = Charts.fairness_distribution(zones, alloc)
        st.plotly_chart(fig, use_container_width=True, key="fair_dist")
    st.markdown("<div class='panel-title'>Zone Breakdown</div>", unsafe_allow_html=True)
    rows = []
    for z in zones:
        rows.append({"Zone": z["name"], "Allocated": alloc.get(z["name"], 0), "Severity": z["current_severity"],
                      "Population": z["population"], "Unmet Demand": z["unmet_demand"], "Resilience": z["resilience_index"]})
    st.dataframe(pd.DataFrame(rows).set_index("Zone").style.format(
        {"Allocated": "{:.1f}", "Severity": "{:.1f}", "Unmet Demand": "{:.1f}", "Resilience": "{:.3f}"}
    ).background_gradient(subset=["Allocated"], cmap="YlOrRd"), use_container_width=True)


def render_tab_analytics():
    if not st.session_state.step_results:
        st.markdown(f"<div class='panel' style='text-align:center;padding:30px;color:{C['dim']}'>Run the simulation to see analytics</div>", unsafe_allow_html=True)
        return
    ctrl = st.session_state.controller
    summary = ctrl.get_simulation_summary()
    mh = summary.get("metrics_history", [])
    fig = Charts.time_series_metrics(mh)
    st.plotly_chart(fig, use_container_width=True, key="ts_metrics")
    col1, col2 = st.columns(2)
    with col1:
        ah = summary.get("allocation_history", [])
        env = ctrl.sim_engine.environment if ctrl.sim_engine else None
        zn = env.zone_names if env else []
        fig = Charts.decision_heatmap(ah, zn)
        st.plotly_chart(fig, use_container_width=True, key="heatmap")
    with col2:
        aw = summary.get("ai_weight_history", [])
        if aw:
            fig = Charts.criteria_weight_evolution(aw)
            st.plotly_chart(fig, use_container_width=True, key="weight_evo")
    if st.session_state.simulation_complete:
        st.markdown("<div class='panel-title'>Performance Scorecard</div>", unsafe_allow_html=True)
        sc = MetricsDisplay.get_performance_scorecard(mh)
        cols = st.columns(len(sc["scores"]))
        for i, s in enumerate(sc["scores"]):
            color = C['accent'] if s["status"] == "🟢" else C['warn'] if s["status"] == "🟡" else C['danger']
            with cols[i]:
                st.markdown(f"""<div class="kpi-card" style="border-top:3px solid {color}">
                    <div class="kpi-val" style="color:{color}">{s['value']:.3f}</div>
                    <div class="kpi-label">{s['metric']}</div>
                    <div class="kpi-target">Target: {s['target']}</div></div>""", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;margin-top:12px;font-size:16px;font-weight:700;color:{C['accent']}'>{sc['overall']}</div>", unsafe_allow_html=True)


def render_tab_ai():
    ctrl = st.session_state.controller
    st.markdown("<div class='panel-title'>🤖 AI Explanation Panel</div>", unsafe_allow_html=True)
    if st.session_state.step_results:
        latest = st.session_state.step_results[-1]
        si = latest["step"]
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📝 Explain Current Step", use_container_width=True):
                exp = ctrl.get_llm_explanation(latest)
                st.session_state.llm_explanations[si] = exp
        with c2:
            if len(st.session_state.step_results) > 1:
                if st.button("⏮ Explain Previous", use_container_width=True):
                    prev = st.session_state.step_results[-2]
                    exp = ctrl.get_llm_explanation(prev)
                    st.session_state.llm_explanations[prev["step"]] = exp
        if si in st.session_state.llm_explanations:
            st.markdown(f"<div class='ai-panel'><div class='ai-tag'>AI-Generated Explanation</div><div style='font-size:13px;line-height:1.6'>{st.session_state.llm_explanations[si]}</div></div>", unsafe_allow_html=True)
        elif latest.get("template_explanation"):
            st.markdown(f"<div class='ai-panel'><div class='ai-tag'>Template Explanation</div><div style='font-size:13px;line-height:1.6'>{latest['template_explanation']}</div></div>", unsafe_allow_html=True)
        tradeoffs = latest.get("tradeoffs", {}).get("tradeoffs", [])
        if tradeoffs:
            st.markdown("<div class='panel-title' style='margin-top:12px'>Trade-off Analysis</div>", unsafe_allow_html=True)
            for t in tradeoffs:
                ic = "🔴" if t["severity"] == "high" else "🟡" if t["severity"] == "moderate" else "🟢"
                st.markdown(f"<div class='neg-round'>{ic} <b>{t['type']}</b>: {t['description']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='panel' style='text-align:center;padding:30px;color:{C['dim']}'>Run a simulation step to generate explanations</div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div class='panel-title'>💬 Ask AI</div>", unsafe_allow_html=True)
    q = st.text_input("Your question:", placeholder="Why did Zone C receive fewer resources?", label_visibility="collapsed")
    if st.button("🔍 Ask", use_container_width=False) and q:
        resp = ctrl.get_llm_query_response(q)
        st.session_state.ask_ai_history.append({"question": q, "answer": resp})
    for qa in reversed(st.session_state.ask_ai_history):
        st.markdown(f"<div class='ai-panel'><div class='ai-tag'>Q: {qa['question']}</div><div style='font-size:13px;margin-top:6px'>{qa['answer']}</div></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div class='panel-title'>📊 Insight Report</div>", unsafe_allow_html=True)
    if st.session_state.simulation_complete:
        if st.button("📋 Generate Full Report", use_container_width=True):
            st.session_state.insight_report = ctrl.get_llm_insights()
        if st.session_state.insight_report:
            st.markdown(f"<div class='ai-panel'><div class='ai-tag'>AI Insight Report</div><div style='font-size:13px;line-height:1.6;margin-top:8px'>{st.session_state.insight_report}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:{C['dim']};font-size:12px'>Complete the simulation to generate insights</div>", unsafe_allow_html=True)


def render_footer():
    if not st.session_state.step_results:
        return
    metrics = st.session_state.step_results[-1].get("metrics", {})
    cards = MetricsDisplay.get_kpi_cards(metrics)
    cols = st.columns(len(cards))
    for i, card in enumerate(cards):
        color = {
            "good": C['accent'], "warning": C['warn'], "bad": C['danger']
        }.get(card["status"], C['dim'])
        with cols[i]:
            st.markdown(f"""<div class="kpi-card" style="border-top:2px solid {color}">
                <div class="kpi-icon">{card['icon']}</div>
                <div class="kpi-label">{card['label']}</div>
                <div class="kpi-val" style="color:{color}">{card['value']}</div>
                <div class="kpi-target">Target: {card['target']}</div></div>""", unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="ESARS — Disaster Response", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
    init_session_state()
    st.markdown(get_css(), unsafe_allow_html=True)
    render_stats_bar()
    render_sidebar()
    t1, t2, t3, t4, t5, t6 = st.tabs(["🌐 Global Overview", "👥 Agents", "⚙ Decision Engine", "📦 Allocation", "📈 Analytics", "🤖 AI Insights"])
    with t1: render_tab_overview()
    with t2: render_tab_agents()
    with t3: render_tab_decision()
    with t4: render_tab_allocation()
    with t5: render_tab_analytics()
    with t6: render_tab_ai()
    render_footer()


if __name__ == "__main__":
    main()
