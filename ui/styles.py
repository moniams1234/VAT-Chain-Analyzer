# ui/styles.py

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ══════════════════════════════════════════════════════
   RESET & ROOT
══════════════════════════════════════════════════════ */
:root {
    --bg:          #f6f8fb;
    --surface:     #ffffff;
    --surface-2:   #f1f5f9;
    --border:      #e2e8f0;
    --border-focus:#6366f1;

    --navy:        #1e3a5f;
    --violet:      #5b4fcf;
    --violet-lt:   #ede9ff;
    --orange:      #e8610a;
    --orange-lt:   #fff4ed;

    --text-primary:   #0f172a;
    --text-secondary: #475569;
    --text-muted:     #94a3b8;

    --success:  #16a34a;
    --success-bg:#f0fdf4;
    --warn:     #b45309;
    --warn-bg:  #fffbeb;
    --danger:   #dc2626;
    --danger-bg:#fef2f2;
    --info:     #1d4ed8;
    --info-bg:  #eff6ff;

    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --shadow-sm: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.06);
    --shadow-md: 0 4px 16px rgba(0,0,0,.08), 0 2px 6px rgba(0,0,0,.06);
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: var(--bg) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
    color: var(--text-primary) !important;
}
[data-testid="stMain"], [data-testid="block-container"] {
    background-color: var(--bg) !important;
}

/* kill sidebar */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
#MainMenu, footer { visibility: hidden !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Dark text everywhere ── */
p, span, div, li, td, th, label,
.stMarkdown, .stMarkdown p,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {
    color: var(--text-primary) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}

/* ── INPUTS: white bg, dark text ── */
.stTextInput input,
.stNumberInput input,
input[type="text"],
input[type="number"] {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}

/* selectbox */
.stSelectbox > div > div,
.stSelectbox > div > div > div,
[data-baseweb="select"],
[data-baseweb="select"] > div,
[data-baseweb="select"] input,
div[data-baseweb="select"] div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
}
[data-baseweb="select"] > div {
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
[data-baseweb="popover"] ul,
[data-baseweb="menu"],
[role="listbox"] {
    background-color: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-md) !important;
}
[role="option"], [data-baseweb="menu-item"] {
    color: #0f172a !important;
    background-color: #ffffff !important;
}
[role="option"]:hover { background-color: var(--violet-lt) !important; }
[aria-selected="true"] { background-color: var(--violet-lt) !important; color: var(--violet) !important; }

/* multiselect */
.stMultiSelect [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border-color: var(--border) !important;
}
[data-baseweb="tag"] {
    background-color: var(--violet-lt) !important;
    color: var(--violet) !important;
    border: 1px solid rgba(91,79,207,0.25) !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span { color: var(--violet) !important; }

/* textarea */
textarea {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}

/* labels */
.stTextInput label, .stNumberInput label,
.stSelectbox label, .stMultiSelect label,
.stCheckbox label, .stRadio label {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}
.stCheckbox label { text-transform: none !important; font-size: 0.9rem !important; }
.stCheckbox span, [data-testid="stCheckbox"] label p { color: var(--text-primary) !important; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, var(--violet) 0%, #7c6ddc 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1.4rem !important;
    box-shadow: 0 2px 8px rgba(91,79,207,0.3) !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(91,79,207,0.4) !important;
}
.stButton > button:disabled {
    background: #e2e8f0 !important;
    color: #94a3b8 !important;
    box-shadow: none !important;
    transform: none !important;
}
.btn-cta .stButton > button {
    background: linear-gradient(135deg, var(--orange) 0%, #f08030 100%) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    padding: 0.7rem 2rem !important;
    box-shadow: 0 3px 12px rgba(232,97,10,0.35) !important;
    width: 100% !important;
}
.btn-cta .stButton > button:hover {
    box-shadow: 0 6px 20px rgba(232,97,10,0.45) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface-2) !important;
    border-radius: var(--radius-sm) !important;
    padding: 3px !important;
    border: 1px solid var(--border) !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    border-radius: 6px !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: var(--violet) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    background: var(--surface) !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stExpander"] summary { color: var(--text-primary) !important; font-weight: 600 !important; }
[data-testid="stExpander"] > div > div { background: var(--surface) !important; }

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] th {
    background: var(--surface-2) !important;
    color: var(--text-secondary) !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
}
[data-testid="stDataFrame"] td { color: var(--text-primary) !important; font-size: 0.85rem !important; }

/* ── ALERTS ── */
.alert-success, .alert-warning, .alert-danger, .alert-info {
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    margin: 0.4rem 0;
    line-height: 1.55;
}
.alert-success { background: var(--success-bg); border-left: 4px solid var(--success); }
.alert-success, .alert-success * { color: #14532d !important; }
.alert-warning { background: var(--warn-bg); border-left: 4px solid #f59e0b; }
.alert-warning, .alert-warning * { color: #78350f !important; }
.alert-danger  { background: var(--danger-bg); border-left: 4px solid var(--danger); }
.alert-danger, .alert-danger * { color: #7f1d1d !important; }
.alert-info    { background: var(--info-bg); border-left: 4px solid #3b82f6; }
.alert-info, .alert-info * { color: #1e3a8a !important; }

/* ── CARDS ── */
.vat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
}
.vat-card-header {
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em;
    color: var(--text-muted) !important; margin-bottom: 0.75rem;
}
.vat-card, .vat-card p, .vat-card div, .vat-card span { color: var(--text-primary) !important; }

.form-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem 1.75rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.25rem;
}
.form-section-header {
    font-size: 1rem; font-weight: 700;
    color: var(--navy) !important;
    margin: 0 0 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--border);
    display: flex; align-items: center; gap: 8px;
}
.form-section-header, .form-section-header * { color: var(--navy) !important; }

/* ── APP HEADER ── */
.app-header {
    background: linear-gradient(135deg, var(--navy) 0%, #2d4f80 100%);
    border-radius: var(--radius-lg);
    padding: 1.75rem 2rem;
    margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.app-header::after {
    content: '';
    position: absolute; right: -30px; top: -30px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 70%);
    border-radius: 50%;
}
.app-title {
    font-size: 1.75rem; font-weight: 800;
    color: #ffffff !important; -webkit-text-fill-color: #ffffff;
    margin: 0 0 0.35rem; letter-spacing: -0.03em;
}
.app-subtitle { color: rgba(255,255,255,0.72) !important; font-size: 0.82rem; line-height: 1.6; }
.header-pill {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px; padding: 2px 9px;
    font-size: 0.7rem; font-weight: 600;
    color: rgba(255,255,255,0.85) !important; letter-spacing: 0.03em;
    margin: 6px 4px 0 0;
}

/* ── SECTION TITLE ── */
.section-title {
    font-size: 1rem; font-weight: 700;
    color: var(--navy) !important;
    margin: 1.5rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--border);
    display: flex; align-items: center; gap: 8px;
}
.section-title, .section-title * { color: var(--navy) !important; }

/* ── BADGES ── */
.badge {
    display: inline-block; padding: 2px 8px;
    border-radius: 20px; font-size: 0.7rem;
    font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.04em; line-height: 1.6;
}
.badge-wdt      { background:#ede9ff; color:#4f39c7; border:1px solid #c4b8f7; }
.badge-wnt      { background:#f0e8ff; color:#7c3aed; border:1px solid #d4bbfc; }
.badge-export   { background:#fff4ed; color:#c2410c; border:1px solid #fed7aa; }
.badge-import   { background:#fffbeb; color:#b45309; border:1px solid #fde68a; }
.badge-domestic { background:#f0fdf4; color:#15803d; border:1px solid #bbf7d0; }
.badge-outside  { background:#f8fafc; color:#475569; border:1px solid #cbd5e1; }
.badge-unknown  { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.badge-movable  { background:#fff4ed; color:#c2410c; border:1px solid #fed7aa; }
.badge-immovable{ background:#f8fafc; color:#64748b; border:1px solid #e2e8f0; }
.badge-pl       { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.badge-eu       { background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; }
.badge-non-eu   { background:#f8fafc; color:#475569; border:1px solid #cbd5e1; }

/* ── PARTY NODE ── */
.party-node {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 0.75rem;
    text-align: center;
}
.party-node, .party-node p, .party-node div, .party-node span { color: var(--text-primary) !important; }
.party-node.polish    { border-color: #ef4444; background:#fff5f5; }
.party-node.organizer { border-color: var(--orange); background: var(--orange-lt); }

/* ── TRANSPORT FLOW ── */
.transport-flow {
    display: flex; align-items: center; gap: 8px;
    padding: 0.6rem 1rem;
    background: var(--orange-lt); border: 1px solid #fed7aa;
    border-radius: var(--radius-sm);
    font-size: 0.875rem; font-weight: 600;
    color: #c2410c !important; margin-top: 1rem;
}
.transport-flow, .transport-flow * { color: #c2410c !important; }

/* ── CHAIN BANNER ── */
.chain-banner {
    background: linear-gradient(90deg, #ede9ff 0%, #f5f3ff 100%);
    border: 1px solid #c4b8f7;
    border-radius: var(--radius-md);
    padding: 0.85rem 1.25rem;
    font-weight: 700; font-size: 0.95rem;
    color: #4f39c7 !important; margin-bottom: 1.25rem;
    display: flex; align-items: center; gap: 10px;
}
.chain-banner, .chain-banner * { color: #4f39c7 !important; }

/* ── DISCLAIMER ── */
.disclaimer {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.9rem 1.25rem;
    font-size: 0.78rem; margin-top: 3rem; text-align: center; line-height: 1.6;
}
.disclaimer, .disclaimer * { color: var(--text-muted) !important; }

/* ── WELCOME ── */
.welcome-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 2.5rem;
    text-align: center; box-shadow: var(--shadow-sm);
}
.welcome-card h2 { color: var(--navy) !important; font-size: 1.35rem !important; }
.welcome-card p  { color: var(--text-secondary) !important; }
.welcome-pill {
    display: inline-flex; flex-direction: column;
    align-items: center; gap: 6px; padding: 1rem;
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: var(--radius-md); min-width: 110px;
}
.welcome-pill .wp-icon  { font-size: 1.75rem; }
.welcome-pill .wp-label { font-size: 0.72rem; font-weight: 600; color: var(--text-secondary) !important; text-align: center; line-height: 1.4; }

hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
.stSpinner > div { border-top-color: var(--violet) !important; }
.confidence-high   { color: var(--success) !important; font-weight: 700; }
.confidence-medium { color: var(--warn) !important; font-weight: 700; }
.confidence-low    { color: var(--danger) !important; font-weight: 700; }
.confidence-verify { color: var(--danger) !important; font-weight: 700; }
</style>
"""
