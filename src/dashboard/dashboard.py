# src/dashboard/dashboard.py
import streamlit as st
import requests
import plotly.graph_objects as go
import streamlit.components.v1 as components

# API local 
API_BASE = "https://l5onbag8e6.execute-api.us-east-1.amazonaws.com/prod"

st.set_page_config(
    page_title="NexaStock AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* Reset y Ocultamiento de Streamlit */
#MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none !important; }
div[data-testid="stHeader"] { display: none !important; }
section[data-testid="stSidebar"] { display: none; }
* { font-family: 'DM Sans', sans-serif; }
body, .stApp { background-color: #f8fafc; }

/* AJUSTE DEL CONTENEDOR NATIVO PARA DAR ESPACIO A LA SIDEBAR */
div[data-testid="stAppViewBlockContainer"] {
    padding-top: 0rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin-left: 64px !important; /* <--- Esto es clave. Mueve TODO el contenido nativo a la derecha. */
    max-width: 100% !important;
}

/* Custom Sidebar estilo Copilot/Enterprise */
.icon-sidebar {
    width: 64px; background: #0f172a;
    display: flex; flex-direction: column; align-items: center;
    padding: 24px 0; gap: 8px;
    position: fixed; top: 0; left: 0; bottom: 0; z-index: 100;
}
.icon-btn {
    width: 44px; height: 44px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; color: #64748b; font-size: 18px; transition: all 0.2s;
}
.icon-btn:hover { color: #f8fafc; background: #1e293b; }
.icon-btn.active { background: #1e293b; color: #818cf8; }

/* ESTO YA NO NECESITA EL MARGIN-LEFT porque lo tiene su contenedor padre stAppViewBlockContainer */
.main-wrap { 
    display: flex; 
    flex-direction: column; 
    min-height: 100vh; 
    background: #f8fafc; 
    margin-left: 0 !important;
}

/* Topbar Minimalista con Logo */
.topbar {
    background: #ffffff; border-bottom: 1px solid #e2e8f0;
    padding: 0 32px; height: 64px;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 50; 
}
.topbar-sub { font-size: 13px; color: #64748b; margin-left: 16px; border-left: 1px solid #e2e8f0; padding-left: 16px; }

.status-pill {
    display: flex; align-items: center; gap: 8px;
    font-size: 12px; font-weight: 500; padding: 6px 12px; border-radius: 20px;
}
.status-pill.online { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }
.status-pill.aws { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-green { background: #22c55e; }
.dot-blue { background: #3b82f6; }

.content { padding: 32px; }

/* Alert Banner */
.alert-banner {
    background: #fff7ed; border: 1px solid #fed7aa; border-radius: 12px;
    padding: 16px 24px; margin-bottom: 24px;
    display: flex; align-items: center; justify-content: space-between;
}
.alert-left { display: flex; align-items: center; gap: 16px; }
.alert-icon { font-size: 24px; color: #ea580c; }
.alert-text { font-size: 15px; font-weight: 600; color: #9a3412; }
.alert-sub { font-size: 13px; color: #c2410c; margin-top: 2px; }
.alert-right { display: flex; align-items: center; gap: 24px; }
.alert-cost-label { font-size: 11px; color: #ea580c; font-weight: 600; text-transform: uppercase; text-align: right; }
.alert-cost { font-size: 24px; font-weight: 700; color: #ea580c; font-family: 'DM Mono', monospace; line-height: 1; }
.btn-orange { background: #ea580c; color: #fff; padding: 10px 20px; border-radius: 8px; font-weight: 500; font-size: 13px; cursor: pointer; border: none; }

/* KPI Grid Estilo SaaS */
.kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 24px; margin-bottom: 32px; }
.kpi-card { border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; position: relative; background: #fff; }
.kpi-card.gray { border-top: 3px solid #cbd5e1; }
.kpi-card.red { background: #fef2f2; border-top: 3px solid #fca5a5; }
.kpi-card.amber { background: #fffbeb; border-top: 3px solid #fcd34d; }
.kpi-card.green { background: #f0fdf4; border-top: 3px solid #86efac; }

.kpi-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.kpi-label { font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-icon { font-size: 20px; opacity: 0.2; }
.kpi-number { font-size: 36px; font-weight: 700; color: #0f172a; line-height: 1; }
.kpi-number.red { color: #dc2626; }
.kpi-number.amber { color: #d97706; }
.kpi-number.green { color: #16a34a; font-size: 28px; }
.kpi-trend { font-size: 12px; font-weight: 500; color: #64748b; margin-top: 12px; display: flex; align-items: center; gap: 4px; }
.kpi-trend.red { color: #ef4444; }
.kpi-trend.green { color: #22c55e; }

/* Paneles Generales */
.panel { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05); }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.panel-title { font-size: 15px; font-weight: 600; color: #0f172a; display: flex; align-items: center; gap: 8px; }

/* Componentes Nativos Streamlit sobreescritos */
.stButton > button {
    background: #4f46e5 !important; color: #fff !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 500 !important; font-size: 14px !important;
    padding: 10px 24px !important; transition: all 0.2s;
}
.stButton > button:hover { background: #4338ca !important; box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2); }
.stTextInput > div > div > input {
    border: 1px solid #cbd5e1 !important; border-radius: 8px !important;
    font-size: 14px !important; padding: 12px !important;
    background: #ffffff !important; color: #0f172a !important;
}
.stTextInput > div > div > input:focus { border-color: #6366f1 !important; box-shadow: 0 0 0 1px #6366f1 !important; }
</style>
""", unsafe_allow_html=True)


# ── API ────────────────────────────────────────────────────────────────────────

def api_get(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def api_post(path, payload):
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

# ── Data ───────────────────────────────────────────────────────────────────────

inventory = api_get("/inventory/") or []
risk      = api_get("/risk/analysis") or {}
purchase  = api_get("/purchase/plan") or {}
connected = bool(inventory)

critical   = risk.get("critical", [])
high_risk  = risk.get("high_risk", [])
ok_prods   = risk.get("ok", [])
plan       = purchase.get("plan", [])
total_cost = purchase.get("total_estimated_cost", 0)

total     = len(inventory)
inv_value = sum(p.get("stock",0) * p.get("price",0) for p in inventory)


# ── Sidebar ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="icon-sidebar">
  <div class="icon-btn active">⊞</div>
  <div class="icon-btn">◈</div>
  <div class="icon-btn">📈</div>
  <div class="icon-btn">🤖</div>
</div>
""", unsafe_allow_html=True)

# ── Topbar ──────────────────────────────────────────────────────────────
# <--- CAMBIO 3: Topbar con Logo en SVG puro (Red Neuronal/Cubo)
tbar_left, tbar_right = st.columns([2, 1])

with tbar_left:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; padding-top: 10px;">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.3); border-radius: 8px;">
            <rect width="24" height="24" rx="6" fill="url(#grad1)"/>
            <path d="M12 6L17 9V15L12 18L7 15V9L12 6Z" stroke="white" stroke-width="1.5" stroke-linejoin="round"/>
            <circle cx="12" cy="12" r="2" fill="white"/>
            <line x1="12" y1="6" x2="12" y2="10" stroke="white" stroke-width="1.5"/>
            <line x1="7" y1="15" x2="10" y2="13" stroke="white" stroke-width="1.5"/>
            <line x1="17" y1="15" x2="14" y2="13" stroke="white" stroke-width="1.5"/>
            <defs>
                <linearGradient id="grad1" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#4f46e5"/>
                    <stop offset="1" stop-color="#4338ca"/>
                </linearGradient>
            </defs>
        </svg>
        <div style="font-size: 20px; font-weight: 700; color: #0f172a; letter-spacing: -0.5px;">NexaStock <span style="color: #4f46e5;">AI</span></div>
    </div>
    """, unsafe_allow_html=True)

with tbar_right:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; justify-content: flex-end; padding-top: 10px; padding-right: 32px;">
        <div class="status-pill aws"><span class="status-dot dot-blue"></span>AWS · us-east-1</div>
        <div class="status-pill online"><span class="status-dot dot-green"></span>{'Live' if connected else 'Offline'}</div>
    </div>
    """, unsafe_allow_html=True)

if not connected:
    st.error("Cannot connect to API. Make sure FastAPI is running.")
    st.stop()

# ── Alert Banner ───────────────────────────────────────────────────────────────

if critical:
    names_str = ", ".join(p.get("name","?") for p in critical[:2])
    if len(critical) > 2: names_str += " and others"
    
    st.markdown(f"""
    <div class="alert-banner">
      <div class="alert-left">
        <div class="alert-icon">⚠</div>
        <div>
          <div class="alert-text">{len(critical)} products critically out of stock</div>
          <div class="alert-sub">{names_str} — immediate action required</div>
        </div>
      </div>
      <div class="alert-right">
        <div>
          <div class="alert-cost-label">Restock cost</div>
          <div class="alert-cost">${total_cost:,.2f}</div>
        </div>
        <button class="btn-orange">Review Plan →</button>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── KPIs ───────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card gray">
    <div class="kpi-header">
      <div class="kpi-label">Total Products</div>
      <div class="kpi-icon">📦</div>
    </div>
    <div class="kpi-number">{total}</div>
    <div class="kpi-trend">— Tracked in real-time</div>
  </div>
  
  <div class="kpi-card red">
    <div class="kpi-header">
      <div class="kpi-label">Critical</div>
      <div class="kpi-icon">⚠</div>
    </div>
    <div class="kpi-number red">{len(critical)}</div>
    <div class="kpi-trend red">↘ Out of stock now</div>
  </div>
  
  <div class="kpi-card amber">
    <div class="kpi-header">
      <div class="kpi-label">High Risk</div>
      <div class="kpi-icon">❗</div>
    </div>
    <div class="kpi-number amber">{len(high_risk)}</div>
    <div class="kpi-trend red">↘ Below reorder threshold</div>
  </div>
  
  <div class="kpi-card green">
    <div class="kpi-header">
      <div class="kpi-label">Inventory Value</div>
      <div class="kpi-icon">$</div>
    </div>
    <div class="kpi-number green">${inv_value:,.0f}</div>
    <div class="kpi-trend green">↗ Current stock value</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Chart + Actions ────────────────────────────────────────────────────────────

col_chart, col_actions = st.columns([1.5, 1])

with col_chart:
    status_map = {p["name"]: p.get("status","OK") for p in critical + high_risk + ok_prods}
    color_map  = {"CRITICAL": "#ef4444", "HIGH_RISK": "#f59e0b", "OK": "#6366f1"}
    names_list    = [p.get("name","?") for p in inventory]
    stocks_list   = [p.get("stock",0) for p in inventory]
    reorders_list = [p.get("reorder_level",0) for p in inventory]
    colors_list   = [color_map.get(status_map.get(n,"OK"),"#6366f1") for n in names_list]
    short_names   = [n.split()[0][:12] for n in names_list]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=short_names, y=stocks_list, marker_color=colors_list,
        name="Current Stock",
        hovertemplate="<b>%{x}</b><br>Stock: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=short_names, y=reorders_list, mode="lines",
        line=dict(color="#0f172a", width=2, dash="dash"),
        name="Dynamic Threshold",
        hovertemplate="<b>%{x}</b><br>Threshold: %{y}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        margin=dict(l=0, r=0, t=20, b=0), height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1,
                    font=dict(size=12, color="#64748b"), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#64748b"), linecolor="#e2e8f0"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(size=11, color="#64748b"), zeroline=False),
        bargap=0.3,
    )
    
    st.markdown("""
    <div class="panel" style="height: 100%;">
      <div class="panel-header">
        <div class="panel-title">Stock Levels vs Dynamic Threshold <span class="badge-ai" style="background:#e0e7ff;color:#4f46e5;">Live</span></div>
      </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_actions:
    all_issues = critical + high_risk
    rows_html = ""
    for p in all_issues[:6]:
        name   = p.get("name","?")
        stock  = p.get("stock",0)
        reorder = p.get("reorder_level",0)
        status = p.get("status","OK")
        
        if status == "CRITICAL":
            badge = '<span style="font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;background:#fef2f2;color:#dc2626;border:1px solid #fee2e2;">Critical</span>'
        else:
            badge = '<span style="font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;background:#fffbeb;color:#d97706;border:1px solid #fef3c7;">High Risk</span>'
            
        rows_html += f"""
        <div style="display:flex;align-items:center;justify-content:space-between;padding:16px 0;border-bottom:1px solid #f1f5f9">
          <div>
            <div style="font-size:14px;font-weight:600;color:#0f172a">{name}</div>
            <div style="font-size:12px;color:#64748b;margin-top:4px">Stock: {stock} · Reorder at: {reorder}</div>
          </div>
          <div>{badge}</div>
        </div>"""

    components.html(f"""<!DOCTYPE html><html><head>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
      *{{box-sizing:border-box;margin:0;padding:0;font-family:'DM Sans',sans-serif}}
      .panel{{background:#fff;border:1px solid #e2e8f0;border-radius:166px;padding:24px; height: 100vh;}}
      .pt{{font-size:15px;font-weight:600;color:#0f172a;margin-bottom:8px;display:flex;align-items:center;gap:12px}}
      .ptag{{font-size:11px;font-weight:600;color:#dc2626;background:#fef2f2;padding:4px 10px;border-radius:12px}}
    </style></head><body>
    <div class="panel">
      <div class="pt">Action Required <span class="ptag">{len(all_issues)} items</span></div>
      <div style="margin-top: 16px;">{rows_html}</div>
    </div></body></html>""", height=470)

st.markdown("<br>", unsafe_allow_html=True)

# ── AI Insights & Chat ─────────────────────────────────────────────────────────

col_insights, col_chat = st.columns([1, 1])

with col_insights:
    st.markdown("""
    <div class="panel" style="height: 100%;">
      <div class="panel-header">
        <div class="panel-title">AI Executive Summary <span class="badge-ai">GPT-4o</span></div>
      </div>
    """, unsafe_allow_html=True)
    
    if "ai_summary" not in st.session_state:
        st.session_state.ai_summary = None

    if st.button("Generate executive summary"):
        with st.spinner("Analyzing data..."):
            result = api_get("/ai/summary")
            st.session_state.ai_summary = result.get("summary","No summary.") if result else "API unavailable."

    if st.session_state.ai_summary:
        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid #4f46e5; border-radius:8px; padding:20px; margin-top: 16px;">
          <p style="font-size:14px;color:#334155;line-height:1.6;margin:0">{st.session_state.ai_summary}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_chat:
    st.markdown("""
    <div class="panel" style="height: 100%;">
      <div class="panel-header">
        <div class="panel-title">Copilot Assistant <span class="badge-ai">Interactive</span></div>
      </div>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    c_input, c_btn = st.columns([4,1])
    with c_input:
        user_input = st.text_input("q", placeholder="Ask anything about the supply chain...", label_visibility="collapsed", key="copilot_q")
    with c_btn:
        ask = st.button("Ask Copilot", use_container_width=True)

    if ask and user_input.strip():
        with st.spinner("Processing..."):
            result = api_post("/ai/copilot", {"question": user_input})
            answer = result.get("answer","No response.") if result else "API unavailable."
        st.session_state.chat_history.append(("you", user_input.strip()))
        st.session_state.chat_history.append(("ai", answer))

    if st.session_state.chat_history:
        msgs_html = ""
        for role, msg in reversed(st.session_state.chat_history):
            safe = msg.replace("\n","<br>")
            if role == "you":
                msgs_html += f'<div style="display:flex;justify-content:flex-end;margin-bottom:16px;"><div style="background:#4f46e5;color:#fff;border-radius:12px 12px 0 12px;padding:12px 16px;font-size:13px;max-width:85%;box-shadow:0 1px 2px rgba(0,0,0,0.05);">{safe}</div></div>'
            else:
                msgs_html += f'<div style="display:flex;justify-content:flex-start;margin-bottom:16px;"><div style="background:#f1f5f9;color:#0f172a;border-radius:12px 12px 12px 0;padding:12px 16px;font-size:13px;max-width:85%;border:1px solid #e2e8f0;line-height:1.6;">{safe}</div></div>'

        components.html(f"""<!DOCTYPE html><html><head>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
          *{{box-sizing:border-box;margin:0;padding:0;font-family:'DM Sans',sans-serif}}
          body{{background:transparent;padding:16px 0 0 0}}
        </style></head><body>
        <div>{msgs_html}</div>
        </body></html>""", height=300, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)