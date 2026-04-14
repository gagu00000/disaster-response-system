"""
Streamlit Dashboard — Dark Operations Center Theme
Premium UI with 6 tabs, live stats bar, agent cards, AHP/Fuzzy panels.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import json
import base64
import streamlit.components.v1 as components
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
.stApp, .stMarkdown, .stTabs, p, label, h1, h2, h3, h4, h5, h6 {{ font-family: 'Inter', sans-serif !important; }}
span:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded):not(.material-icons) {{ font-family: 'Inter', sans-serif !important; }}
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
/* Button variants via sidebar context */
section[data-testid="stSidebar"] .stButton:first-child button {{ background: {C['accent']}22 !important; color: {C['accent']} !important; border: 1px solid {C['accent']} !important; }}
section[data-testid="stSidebar"] .stButton:first-child button:hover {{ background: {C['accent']}44 !important; }}
/* Metric cards dark theme */
div[data-testid="stMetric"] {{ background: {C['panel']}; border: 1px solid {C['panel_border']}; border-radius: 10px; padding: 14px; }}
div[data-testid="stMetric"] label {{ color: {C['dim']} !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: {C['accent']} !important; font-weight: 700; }}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] svg {{ display: none; }}
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
/* Section headers */
.section-header {{ font-size:13px; color:{C['text']}; font-weight:600; margin-bottom:4px; display:flex; align-items:center; gap:8px; }}
.section-sub {{ font-size:11px; color:{C['dim']}; margin-bottom:14px; }}
/* Dark scrollbar */
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:{C['bg']}; }}
::-webkit-scrollbar-thumb {{ background:#333; border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:#555; }}
/* Consistent section spacing */
.stTabs [data-baseweb="tab-panel"] {{ padding-top:20px; }}
.panel {{ margin-bottom:16px; }}
/* Divider styling */
hr {{ border-color: {C['panel_border']} !important; }}
</style>"""


def init_session_state():
    defaults = {
        "controller": Controller(), "initialized": False, "step_results": [],
        "current_step": 0, "simulation_complete": False, "scenario_narration": "",
        "llm_explanations": {}, "ask_ai_history": [], "insight_report": "",
        "chat_messages": [], "viewing_step": 0, "confirm_reset": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_viewed_step():
    """Return the step result for the currently selected viewing step."""
    idx = st.session_state.get("viewing_step", len(st.session_state.step_results) - 1)
    idx = min(idx, len(st.session_state.step_results) - 1)
    return st.session_state.step_results[idx] if st.session_state.step_results else None


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
    # Show viewed-step indicator when not viewing the latest
    if st.session_state.step_results and st.session_state.viewing_step < len(st.session_state.step_results) - 1:
        viewed = st.session_state.viewing_step + 1
        total = len(st.session_state.step_results)
        st.markdown(f"<div style='text-align:center;padding:6px;background:{C['warn']}15;border:1px solid {C['warn']}44;border-radius:6px;margin-bottom:8px;font-size:12px;color:{C['warn']}'><b>📋 Viewing Step {viewed}</b> of {total} — use sidebar slider to navigate</div>", unsafe_allow_html=True)


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
            st.session_state.update({"initialized": True, "simulation_complete": False, "step_results": [], "current_step": 0, "viewing_step": 0,
                                     "scenario_narration": ctrl.get_scenario_narration(), "llm_explanations": {}, "ask_ai_history": [], "insight_report": "", "confirm_reset": False})
            st.rerun()
        if reset:
            if st.session_state.step_results and not st.session_state.confirm_reset:
                st.session_state.confirm_reset = True
                st.rerun()
            else:
                st.session_state.update({"initialized": False, "step_results": [], "simulation_complete": False, "current_step": 0, "viewing_step": 0, "confirm_reset": False})
                st.rerun()
        if st.session_state.confirm_reset:
            st.warning("Reset will clear all simulation data.")
            rc1, rc2 = st.columns(2)
            with rc1:
                if st.button("✅ Confirm Reset", use_container_width=True):
                    st.session_state.update({"initialized": False, "step_results": [], "simulation_complete": False, "current_step": 0, "viewing_step": 0, "confirm_reset": False})
                    st.rerun()
            with rc2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.confirm_reset = False
                    st.rerun()
            st.rerun()
        if st.session_state.initialized and not st.session_state.simulation_complete:
            c1, c2 = st.columns(2)
            with c1:
                step_clicked = st.button("⏭ STEP", use_container_width=True)
            with c2:
                all_clicked = st.button("⏩ ALL", use_container_width=True)
            if step_clicked:
                with st.spinner("Running step..."):
                    r = st.session_state.controller.run_step()
                    if "error" not in r:
                        st.session_state.step_results.append(r)
                        st.session_state.current_step += 1
                        if st.session_state.controller.sim_engine.is_complete:
                            st.session_state.simulation_complete = True
                st.rerun()
            if all_clicked:
                with st.spinner("Running all steps..."):
                    results = st.session_state.controller.run_all_steps()
                    st.session_state.step_results.extend(results)
                    st.session_state.current_step += len(results)
                    st.session_state.simulation_complete = True
                st.rerun()
        if st.session_state.simulation_complete:
            st.markdown(f"<div style='text-align:center;padding:8px;background:{C['accent']}15;border:1px solid {C['accent']}33;border-radius:8px;color:{C['accent']};font-size:12px;font-weight:600;margin-top:8px'>✓ SIMULATION COMPLETE</div>", unsafe_allow_html=True)
        if len(st.session_state.step_results) > 1:
            st.markdown(f"<div style='font-size:10px;color:{C['dim']};text-transform:uppercase;letter-spacing:1px;margin-top:12px;margin-bottom:4px'>View Step</div>", unsafe_allow_html=True)
            max_idx = len(st.session_state.step_results) - 1
            st.session_state.viewing_step = st.slider(
                "Step", 0, max_idx, max_idx, label_visibility="collapsed",
                format=f"Step %d of {max_idx + 1}"
            )
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
        st.markdown(f"<div class='panel' style='text-align:center;padding:50px'><div style='font-size:36px;margin-bottom:12px'>🌍</div><div style='font-size:15px;color:{C['text']};font-weight:600;margin-bottom:8px'>No Active Simulation</div><div style='font-size:13px;color:{C['dim']}'>Select a scenario from the sidebar and click <b style=\"color:{C['accent']}\">\u25b6 START</b> to begin</div></div>", unsafe_allow_html=True)
        return
    st.markdown(f"<div class='section-header'>Situation Overview</div><div class='section-sub'>Current disaster zone status, resource pool, and active events</div>", unsafe_allow_html=True)
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
        latest = get_viewed_step()
        events = latest.get("events", [])
        if events:
            st.markdown("<div class='panel-title'>⚡ Dynamic Events</div>", unsafe_allow_html=True)
            for e in events:
                st.markdown(f"<div class='neg-round'><span class='neg-round-title'>⚠ {e['type'].replace('_',' ').title()}</span> — <span class='neg-round-desc'>{e['zone']}: {e['description']}</span></div>", unsafe_allow_html=True)


def render_tab_agents():
    if not st.session_state.step_results:
        st.markdown(f"<div class='panel' style='text-align:center;padding:40px'><div style='font-size:32px;margin-bottom:10px'>👥</div><div style='font-size:13px;color:{C['dim']}'>Run a simulation step to see agent negotiations and proposals</div></div>", unsafe_allow_html=True)
        return
    latest = get_viewed_step()
    nr = latest.get("allocation_result", {}).get("negotiation_result", {})
    st.markdown(f"<div class='section-header'>Agent Negotiation</div><div class='section-sub'>Multi-agent proposals, dissent analysis, and consensus building for Step {latest.get('step', '?')}</div>", unsafe_allow_html=True)
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
            st.dataframe(df.style.format("{:.1f}").background_gradient(cmap="YlGn", axis=1), use_container_width=True)
        st.markdown("<div class='panel-title' style='margin-top:16px'>Proposals vs Consensus</div>", unsafe_allow_html=True)
        consensus = latest.get("final_allocation", {})
        fig = Charts.negotiation_divergence(proposals, consensus)
        st.plotly_chart(fig, use_container_width=True, key="neg_div")
    st.markdown("<div class='panel-title'>Negotiation Rounds</div>", unsafe_allow_html=True)
    record = nr.get("negotiation_record", {})
    rounds_list = record.get("rounds", [])
    for r in rounds_list:
        is_last = r['round'] == len(rounds_list)
        with st.expander(f"Round {r['round']}: {r['name']}", expanded=is_last):
            st.markdown(f"<span style='color:{C['dim']};font-size:12px'>{r.get('description','')}</span>", unsafe_allow_html=True)
            if "contested_zones" in r and r["contested_zones"]:
                st.warning(f"Contested: {', '.join(r['contested_zones'])}")
            if "final_allocation" in r:
                st.json(r["final_allocation"])


def render_tab_decision():
    if not st.session_state.step_results:
        st.markdown(f"<div class='panel' style='text-align:center;padding:40px'><div style='font-size:32px;margin-bottom:10px'>⚙️</div><div style='font-size:13px;color:{C['dim']}'>Run a simulation step to see AHP weights, fuzzy assessments, and decision logic</div></div>", unsafe_allow_html=True)
        return
    latest = get_viewed_step()
    nr = latest.get("allocation_result", {}).get("negotiation_result", {})
    agent_states = nr.get("agent_states", {})
    st.markdown(f"<div class='section-header'>Decision Engine</div><div class='section-sub'>AHP criteria weights, fuzzy urgency assessment, and agent priority comparison for Step {latest.get('step', '?')}</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='panel'><div class='panel-title'>AHP Criteria Weights</div>", unsafe_allow_html=True)
        agent_weights = {at: s.get("weights", {}) for at, s in agent_states.items()}
        colors_map = {"Emergency Response": C['emergency'], "Government Agency": C['gov'], "NGO": C['ngo'], "AI Coordinator": C['ai_agent']}
        if agent_weights:
            agent_tabs = st.tabs(list(agent_weights.keys()))
            for tab, (agent_name, weights) in zip(agent_tabs, agent_weights.items()):
                with tab:
                    color = colors_map.get(agent_name, C['accent'])
                    for criterion, val in weights.items():
                        pct = val * 100
                        st.markdown(f"""<div class="ahp-bar-wrap"><div class="ahp-bar-label"><span>{criterion.title()}</span><span>{pct:.0f}%</span></div>
                            <div class="ahp-bar"><div class="ahp-bar-fill" style="width:{pct}%;background:{color}"></div></div></div>""", unsafe_allow_html=True)
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
        st.markdown("<div class='panel'><div class='panel-title'>Consensus Delta (Agent vs Final)</div>", unsafe_allow_html=True)
        proposals = nr.get("proposals", {})
        consensus = latest.get("final_allocation", {})
        if proposals and consensus:
            delta_data = {}
            for agent, prop in proposals.items():
                delta_data[agent] = {z: prop.get(z, 0) - consensus.get(z, 0) for z in consensus}
            df = pd.DataFrame(delta_data).T
            st.dataframe(df.style.format("{:+.1f}").background_gradient(cmap="RdYlGn", axis=None, vmin=-20, vmax=20), use_container_width=True)
            st.markdown(f"<div style='font-size:11px;color:{C['dim']};margin-top:4px'>Positive = agent wanted more than consensus, Negative = wanted less</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_tab_allocation():
    if not st.session_state.step_results:
        st.markdown(f"<div class='panel' style='text-align:center;padding:40px'><div style='font-size:32px;margin-bottom:10px'>📦</div><div style='font-size:13px;color:{C['dim']}'>Run a simulation step to see resource allocation and fairness metrics</div></div>", unsafe_allow_html=True)
        return
    latest = get_viewed_step()
    alloc = latest.get("final_allocation", {})
    zones = latest.get("post_state", [])
    st.markdown(f"<div class='section-header'>Resource Allocation</div><div class='section-sub'>Distribution of resources across zones with fairness analysis for Step {latest.get('step', '?')}</div>", unsafe_allow_html=True)
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
    ).background_gradient(subset=["Allocated"], cmap="YlGn").background_gradient(subset=["Severity"], cmap="YlOrRd"), use_container_width=True)


def render_tab_analytics():
    if not st.session_state.step_results:
        st.markdown(f"<div class='panel' style='text-align:center;padding:40px'><div style='font-size:32px;margin-bottom:10px'>📈</div><div style='font-size:13px;color:{C['dim']}'>Run the full simulation to see time-series analytics and performance trends</div></div>", unsafe_allow_html=True)
        return
    st.markdown(f"<div class='section-header'>Performance Analytics</div><div class='section-sub'>Time-series trends, allocation heatmaps, and strategy comparison</div>", unsafe_allow_html=True)
    ctrl = st.session_state.controller
    summary = ctrl.get_simulation_summary()
    mh = summary.get("metrics_history", [])
    # Generate quick insight from metrics
    if mh:
        last_m = mh[-1]
        cov = last_m.get("response_coverage", 0)
        gini = last_m.get("gini_coefficient", 0)
        cov_status = f"<span style='color:{C['accent']}'>above target</span>" if cov > 0.70 else f"<span style='color:{C['warn']}'>below target</span>"
        gini_status = f"<span style='color:{C['accent']}'>fair</span>" if gini < 0.30 else f"<span style='color:{C['warn']}'>unequal</span>"
        st.markdown(f"<div style='font-size:12px;color:{C['dim']};margin-bottom:8px'>Coverage is {cov_status} at {cov:.1%} | Gini is {gini_status} at {gini:.3f}</div>", unsafe_allow_html=True)
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
        st.markdown("<div class='panel-title'>Baseline Comparison</div>", unsafe_allow_html=True)
        baselines = summary.get("baselines", {})
        last_alloc = st.session_state.step_results[-1].get("final_allocation", {}) if st.session_state.step_results else {}
        if baselines and last_alloc:
            fig = Charts.baseline_comparison(last_alloc, baselines)
            st.plotly_chart(fig, use_container_width=True, key="baseline_cmp")
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
    st.markdown(f"<div class='section-header'>AI Insights & Explanations</div><div class='section-sub'>LLM-powered explanations of decisions, trade-offs, and full simulation reports</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>🤖 AI Explanation Panel</div>", unsafe_allow_html=True)
    if st.session_state.step_results:
        latest = st.session_state.step_results[-1]
        si = latest["step"]
        c1, c2 = st.columns(2)
        with c1:
            explain_current = st.button("📝 Explain Current Step", use_container_width=True)
        with c2:
            explain_prev = len(st.session_state.step_results) > 1 and st.button("⏮ Explain Previous", use_container_width=True)
        if explain_current:
            with st.spinner("Generating AI explanation..."):
                exp = ctrl.get_llm_explanation(latest)
                st.session_state.llm_explanations[si] = exp
        if explain_prev:
            with st.spinner("Generating AI explanation..."):
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
        st.markdown(f"<div class='panel' style='text-align:center;padding:40px'><div style='font-size:32px;margin-bottom:10px'>🤖</div><div style='font-size:13px;color:{C['dim']}'>Run a simulation step, then use AI to explain decisions and trade-offs</div></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div class='panel-title'>📊 Insight Report</div>", unsafe_allow_html=True)
    if st.session_state.simulation_complete:
        report_clicked = st.button("📋 Generate Full Report", use_container_width=True)
        if report_clicked:
            with st.spinner("Generating insight report..."):
                st.session_state.insight_report = ctrl.get_llm_insights()
        if st.session_state.insight_report:
            st.markdown(f"<div class='ai-panel'><div class='ai-tag'>AI Insight Report</div><div style='font-size:13px;line-height:1.6;margin-top:8px'>{st.session_state.insight_report}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:{C['dim']};font-size:12px'>Complete the simulation to generate insights</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{C['dim']};font-size:12px;margin-top:12px'>💬 Use the floating chat widget (bottom-right) to ask questions about simulation data.</div>", unsafe_allow_html=True)


def _build_widget_context():
    """Build simulation context string for the floating chat widget."""
    ctrl = st.session_state.controller
    if not ctrl.is_initialized:
        return "No simulation has been run yet. Please initialize and run a scenario first."
    try:
        summary = ctrl.get_simulation_summary()
        parts = []
        scenario = summary.get("scenario", {})
        if scenario:
            parts.append(f"Scenario: {scenario.get('name', '?')} | Type: {scenario.get('type', '?')} | Steps: {summary.get('total_steps_completed', 0)}")
        zones = summary.get("final_zone_states", [])
        if zones:
            parts.append("ZONE STATUS:")
            for z in zones:
                parts.append(f"  {z['name']}: Severity={z['current_severity']:.1f}/10, Pop={z['population']}, Resources={z['cumulative_resources_received']:.1f}, Unmet={z['unmet_demand']:.1f}, Resilience={z['resilience_index']:.3f}")
        metrics = summary.get("final_metrics", {})
        if metrics:
            parts.append("FINAL METRICS:")
            for k, v in metrics.items():
                if isinstance(v, float):
                    parts.append(f"  {k}: {v:.4f}")
                elif isinstance(v, int):
                    parts.append(f"  {k}: {v}")
        alloc_history = summary.get("allocation_history", [])
        if alloc_history:
            parts.append(f"ALLOCATION HISTORY (last 3 of {len(alloc_history)}):")
            for ah in alloc_history[-3:]:
                allocs = ah.get("allocations", {})
                alloc_str = ", ".join(f"{z}={v:.1f}" for z, v in allocs.items())
                parts.append(f"  Step {ah.get('step', '?')}: {alloc_str}")
        mh = summary.get("metrics_history", [])
        if mh:
            parts.append(f"METRICS OVER TIME ({len(mh)} steps):")
            for m in mh:
                parts.append(f"  Step {m.get('step','?')}: Coverage={m.get('response_coverage',0):.3f}, Gini={m.get('gini_coefficient',0):.3f}, Resilience={m.get('avg_resilience',0):.3f}")
        return "\n".join(parts) if parts else "Simulation initialized but no steps completed yet."
    except Exception:
        return "Error reading simulation data."


def render_chat_widget():
    """Render a floating chat popup widget that calls Ollama directly via JS."""
    context = _build_widget_context()
    system_prompt = (
        "You are the ESARS AI Assistant for a multi-agent disaster response simulation.\\n\\n"
        "RULES:\\n"
        "1. Answer ONLY using the SIMULATION DATA below. No external knowledge.\\n"
        "2. Reference specific numbers: zone names, severity scores, allocations, Gini, coverage.\\n"
        "3. If data is insufficient, say: I don't have enough simulation data to answer that.\\n"
        "4. Keep answers concise (2-5 sentences) unless asked for detail.\\n"
        "5. Professional, neutral language only.\\n"
        "6. For unrelated questions: I can only answer questions about the simulation.\\n\\n"
        "SIMULATION DATA:\\n" + context.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    )
    system_prompt_js = json.dumps(system_prompt)
    ctrl = st.session_state.controller
    is_online = ctrl.llm_available
    status_text = "Online" if is_online else "Offline"
    status_color = "#22c55e" if is_online else "#ef4444"

    widget_html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{font-family:'Inter',sans-serif;background:transparent;overflow:hidden;height:100%;width:100%}}
.chat-toggle{{position:absolute;bottom:0;right:0;width:56px;height:56px;border-radius:50%;
  background:linear-gradient(135deg,#7c3aed,#a855f7);border:none;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 4px 24px rgba(168,85,247,0.45);transition:transform .2s,box-shadow .2s;z-index:10}}
.chat-toggle:hover{{transform:scale(1.1);box-shadow:0 6px 32px rgba(168,85,247,0.65)}}
.chat-toggle svg{{width:26px;height:26px;fill:#fff}}
.chat-panel{{position:absolute;bottom:68px;right:0;width:370px;max-height:480px;
  background:#111119;border-radius:16px;border:1px solid #2a2a3e;
  box-shadow:0 16px 56px rgba(0,0,0,0.6);display:none;flex-direction:column;
  overflow:hidden;z-index:9}}
.chat-panel.open{{display:flex}}
.chat-header{{background:linear-gradient(135deg,#1a1a2e,#252542);padding:14px 16px;
  display:flex;align-items:center;gap:12px;border-bottom:1px solid #2a2a3e;flex-shrink:0}}
.chat-header-icon{{width:40px;height:40px;border-radius:12px;
  background:linear-gradient(135deg,#7c3aed,#a855f7);display:flex;align-items:center;
  justify-content:center;font-size:20px;flex-shrink:0}}
.chat-header-text{{flex:1}}
.chat-header-title{{font-size:14px;font-weight:600;color:#f0f0f0}}
.chat-header-sub{{font-size:11px;color:#777;margin-top:2px}}
.chat-status{{display:flex;align-items:center;gap:6px;font-size:11px;color:{status_color};font-weight:500}}
.chat-status-dot{{width:8px;height:8px;border-radius:50%;background:{status_color};animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
.chat-messages{{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;
  min-height:180px;max-height:260px}}
.chat-messages::-webkit-scrollbar{{width:4px}}
.chat-messages::-webkit-scrollbar-thumb{{background:#333;border-radius:4px}}
.msg-wrap{{display:flex;flex-direction:column}}
.msg-wrap.user{{align-items:flex-end}}
.msg-wrap.bot{{align-items:flex-start}}
.msg{{max-width:85%;padding:10px 14px;border-radius:12px;font-size:13px;line-height:1.55;
  color:#e0e0e0;word-wrap:break-word;white-space:pre-wrap}}
.msg.bot{{background:#1a1a2e;border:1px solid #2a2a3e;border-bottom-left-radius:4px}}
.msg.user{{background:linear-gradient(135deg,#7c3aed,#6d28d9);color:#fff;border-bottom-right-radius:4px}}
.msg-time{{font-size:10px;color:#555;margin-top:3px}}
.typing{{display:none;align-self:flex-start;padding:10px 14px;background:#1a1a2e;
  border:1px solid #2a2a3e;border-radius:12px;border-bottom-left-radius:4px;gap:5px;align-items:center}}
.typing.show{{display:flex}}
.tdot{{width:6px;height:6px;border-radius:50%;background:#888;animation:tdot 1.4s infinite}}
.tdot:nth-child(2){{animation-delay:.2s}}.tdot:nth-child(3){{animation-delay:.4s}}
@keyframes tdot{{0%,100%{{opacity:.3;transform:translateY(0)}}50%{{opacity:1;transform:translateY(-3px)}}}}
.suggestions{{padding:8px 14px 10px;display:flex;flex-wrap:wrap;gap:6px;flex-shrink:0;border-top:1px solid #1e1e2e}}
.sug-btn{{background:transparent;border:1px solid #3a3a5e;color:#999;padding:5px 12px;
  border-radius:16px;font-size:11px;cursor:pointer;transition:all .15s;font-family:'Inter',sans-serif}}
.sug-btn:hover{{border-color:#a855f7;color:#a855f7;background:rgba(168,85,247,.08)}}
.chat-input-area{{padding:10px 14px;border-top:1px solid #2a2a3e;display:flex;gap:8px;
  background:#0d0d14;flex-shrink:0}}
.chat-input{{flex:1;background:#1a1a28;border:1px solid #2a2a3e;border-radius:10px;
  padding:10px 14px;color:#e0e0e0;font-size:13px;outline:none;font-family:'Inter',sans-serif;
  transition:border-color .2s}}
.chat-input:focus{{border-color:#a855f7}}
.chat-input::placeholder{{color:#555}}
.send-btn{{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,#00d4aa,#00b894);
  border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;
  transition:transform .15s,opacity .15s;flex-shrink:0}}
.send-btn:hover{{transform:scale(1.06)}}.send-btn:disabled{{opacity:.35;cursor:not-allowed;transform:none}}
.send-btn svg{{width:18px;height:18px;fill:#fff}}
</style></head><body>
<button class="chat-toggle" id="toggleBtn" onclick="toggleChat()">
  <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>
</button>
<div class="chat-panel" id="chatPanel">
  <div class="chat-header">
    <div class="chat-header-icon">🤖</div>
    <div class="chat-header-text">
      <div class="chat-header-title">AI Dashboard Assistant</div>
      <div class="chat-header-sub">Ask anything about your data</div>
    </div>
    <div class="chat-status"><div class="chat-status-dot"></div>{status_text}</div>
  </div>
  <div class="chat-messages" id="msgsDiv"></div>
  <div class="typing" id="typingInd"><div class="tdot"></div><div class="tdot"></div><div class="tdot"></div></div>
  <div class="suggestions" id="sugDiv">
    <button class="sug-btn" onclick="sendSug('What is the current coverage?')">What is the current coverage?</button>
    <button class="sug-btn" onclick="sendSug('Which zone needs most help?')">Which zone needs most help?</button>
    <button class="sug-btn" onclick="sendSug('Explain the fairness metrics')">Explain fairness metrics</button>
    <button class="sug-btn" onclick="sendSug('What are the trade-offs?')">What are the trade-offs?</button>
  </div>
  <div class="chat-input-area">
    <input type="text" class="chat-input" id="chatIn" placeholder="Ask about the simulation..." onkeydown="if(event.key==='Enter')sendMsg()"/>
    <button class="send-btn" id="sendBtn" onclick="sendMsg()">
      <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
    </button>
  </div>
</div>
<script>
const SYS={system_prompt_js};
const OURL='http://localhost:11434/api/chat';
const MDL='mistral';
const SK='esars_chat_hist';
let chatOpen=false,msgs=[],disp=[],busy=false;
function ld(){{try{{const s=localStorage.getItem(SK);if(s){{disp=JSON.parse(s);msgs=[{{role:'system',content:SYS}}];disp.forEach(m=>msgs.push({{role:m.role,content:m.content}}))}}else{{msgs=[{{role:'system',content:SYS}}];disp=[]}}}}catch(e){{msgs=[{{role:'system',content:SYS}}];disp=[]}}}}
function sv(){{try{{localStorage.setItem(SK,JSON.stringify(disp))}}catch(e){{}}}}
function toggleChat(){{chatOpen=!chatOpen;document.getElementById('chatPanel').classList.toggle('open',chatOpen);if(chatOpen&&disp.length===0)addBot("Hello! I'm your ESARS AI Assistant powered by Mistral. Ask me anything about zone allocations, agent decisions, fairness metrics, or simulation outcomes.")}}
function gt(){{const n=new Date();return n.toLocaleTimeString([],{{hour:'2-digit',minute:'2-digit'}})}}
function sb(){{const d=document.getElementById('msgsDiv');d.scrollTop=d.scrollHeight}}
function render(){{const d=document.getElementById('msgsDiv');d.innerHTML='';disp.forEach(m=>{{const w=document.createElement('div');w.className='msg-wrap '+(m.role==='user'?'user':'bot');const b=document.createElement('div');b.className='msg '+(m.role==='user'?'user':'bot');b.textContent=m.content;const t=document.createElement('div');t.className='msg-time';t.textContent=m.time||'';w.appendChild(b);w.appendChild(t);d.appendChild(w)}});sb()}}
function addBot(txt){{disp.push({{role:'assistant',content:txt,time:gt()}});msgs.push({{role:'assistant',content:txt}});sv();render()}}
async function sendMsg(){{if(busy)return;const inp=document.getElementById('chatIn');const txt=inp.value.trim();if(!txt)return;inp.value='';document.getElementById('sugDiv').style.display='none';disp.push({{role:'user',content:txt,time:gt()}});msgs.push({{role:'user',content:txt}});sv();render();busy=true;document.getElementById('typingInd').classList.add('show');document.getElementById('sendBtn').disabled=true;sb();try{{const r=await fetch(OURL,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{model:MDL,messages:msgs,stream:false,options:{{temperature:0.3,num_predict:500}}}})}}); if(!r.ok)throw new Error('API '+r.status);const d=await r.json();addBot(d.message?.content||'No response.')}}catch(e){{addBot('Could not reach Ollama. Make sure it is running. Error: '+e.message)}}finally{{busy=false;document.getElementById('typingInd').classList.remove('show');document.getElementById('sendBtn').disabled=false}}}}
function sendSug(t){{document.getElementById('chatIn').value=t;sendMsg()}}
ld();render();
</script></body></html>"""

    # Use components.html with height=0 so it takes no page space.
    # The script inside escapes the iframe and injects the widget into the PARENT document body.
    b64 = base64.b64encode(widget_html.encode()).decode()
    injector_html = f"""
<script>
(function() {{
    var doc = window.parent.document;
    var old = doc.getElementById('esars-chat-widget');
    if (old) old.remove();
    var w = doc.createElement('div');
    w.id = 'esars-chat-widget';
    w.style.cssText = 'position:fixed;bottom:24px;right:24px;width:400px;height:560px;z-index:999999;pointer-events:none;';
    var f = doc.createElement('iframe');
    f.src = 'data:text/html;base64,{b64}';
    f.style.cssText = 'width:100%;height:100%;border:none;background:transparent;pointer-events:auto;';
    w.appendChild(f);
    doc.body.appendChild(w);
}})();
</script>
"""
    components.html(injector_html, height=0, scrolling=False)


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
    render_chat_widget()


if __name__ == "__main__":
    main()
