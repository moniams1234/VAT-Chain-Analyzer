# ui/styles.py

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --navy: #0f1b35;
    --navy-mid: #1a2d52;
    --violet: #5b3fa6;
    --violet-light: #7c5cc4;
    --orange: #f07830;
    --orange-light: #f59550;
    --white: #f8f9fc;
    --gray-light: #e8ecf4;
    --gray-mid: #8895b3;
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
    --card-bg: rgba(26, 45, 82, 0.6);
    --card-border: rgba(91, 63, 166, 0.3);
}

/* ── Root & Background ── */
.stApp {
    background: linear-gradient(135deg, #0a1128 0%, #0f1b35 40%, #1a1040 100%);
    font-family: 'Sora', sans-serif;
    color: var(--white);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Headings ── */
h1, h2, h3 {
    font-family: 'Sora', sans-serif;
    font-weight: 800;
    letter-spacing: -0.02em;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1b35 0%, #1a1040 100%);
    border-right: 1px solid var(--card-border);
}
[data-testid="stSidebar"] * { color: var(--white) !important; }

/* ── Inputs & Selects ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(15, 27, 53, 0.8) !important;
    border: 1px solid var(--card-border) !important;
    color: var(--white) !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
}
.stSelectbox > div > div:hover,
.stTextInput > div > div > input:focus {
    border-color: var(--violet-light) !important;
    box-shadow: 0 0 0 2px rgba(91, 63, 166, 0.25) !important;
}

/* ── Labels ── */
.stSelectbox label,
.stTextInput label,
.stNumberInput label,
.stCheckbox label,
.stRadio label,
.stMultiSelect label {
    color: var(--gray-light) !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--violet) 0%, var(--violet-light) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(91, 63, 166, 0.4) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(91, 63, 166, 0.6) !important;
    background: linear-gradient(135deg, var(--violet-light) 0%, var(--orange) 100%) !important;
}

/* ── CTA Button ── */
.cta-button > button {
    background: linear-gradient(135deg, var(--orange) 0%, var(--orange-light) 100%) !important;
    font-size: 1.1rem !important;
    padding: 0.8rem 2rem !important;
    box-shadow: 0 4px 25px rgba(240, 120, 48, 0.5) !important;
    width: 100% !important;
}
.cta-button > button:hover {
    background: linear-gradient(135deg, var(--orange-light) 0%, #fbb25a 100%) !important;
    box-shadow: 0 8px 35px rgba(240, 120, 48, 0.7) !important;
}

/* ── Cards ── */
.vat-card {
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.vat-card-header {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--orange);
    margin-bottom: 0.75rem;
}

/* ── Section titles ── */
.section-title {
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--white);
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--violet);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.badge-wdt { background: rgba(91, 63, 166, 0.3); color: #c4b0f5; border: 1px solid rgba(91,63,166,0.5); }
.badge-wnt { background: rgba(91, 63, 166, 0.2); color: #b8a8f0; border: 1px solid rgba(91,63,166,0.4); }
.badge-export { background: rgba(240, 120, 48, 0.2); color: #f59550; border: 1px solid rgba(240,120,48,0.4); }
.badge-import { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245,158,11,0.4); }
.badge-domestic { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.badge-outside { background: rgba(136, 149, 179, 0.2); color: #a8b4cc; border: 1px solid rgba(136,149,179,0.3); }
.badge-unknown { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.badge-movable { background: rgba(240, 120, 48, 0.3); color: #fbbf24; border: 1px solid rgba(240,120,48,0.5); }
.badge-immovable { background: rgba(15, 27, 53, 0.5); color: var(--gray-mid); border: 1px solid rgba(136,149,179,0.2); }
.badge-pl { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239,68,68,0.4); }
.badge-eu { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
.badge-non-eu { background: rgba(136, 149, 179, 0.2); color: #94a3b8; border: 1px solid rgba(136,149,179,0.3); }

/* ── Party node ── */
.party-node {
    background: rgba(15, 27, 53, 0.8);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.party-node.polish { border-color: #ef4444; box-shadow: 0 0 15px rgba(239,68,68,0.2); }
.party-node.organizer { border-color: var(--orange); box-shadow: 0 0 15px rgba(240,120,48,0.25); }

/* ── Alert boxes ── */
.alert-warning {
    background: rgba(245, 158, 11, 0.1);
    border-left: 4px solid var(--warning);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    color: #fde68a;
    font-size: 0.9rem;
}
.alert-danger {
    background: rgba(239, 68, 68, 0.1);
    border-left: 4px solid var(--danger);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    color: #fca5a5;
    font-size: 0.9rem;
}
.alert-info {
    background: rgba(59, 130, 246, 0.1);
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    color: #93c5fd;
    font-size: 0.9rem;
}
.alert-success {
    background: rgba(34, 197, 94, 0.1);
    border-left: 4px solid var(--success);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    color: #86efac;
    font-size: 0.9rem;
}

/* ── Dataframe / Tables ── */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 8px !important;
    color: var(--white) !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: rgba(15, 27, 53, 0.5) !important;
    border: 1px solid var(--card-border) !important;
    border-top: none !important;
}

/* ── Confidence pill ── */
.confidence-high { color: #4ade80; font-weight: 700; }
.confidence-medium { color: #fbbf24; font-weight: 700; }
.confidence-low { color: #f87171; font-weight: 700; }
.confidence-verify { color: #f87171; font-weight: 700; animation: pulse 1.5s infinite; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* ── Disclaimer ── */
.disclaimer {
    background: rgba(15, 27, 53, 0.6);
    border: 1px solid rgba(136, 149, 179, 0.2);
    border-radius: 8px;
    padding: 1rem 1.5rem;
    color: var(--gray-mid);
    font-size: 0.8rem;
    margin-top: 3rem;
    text-align: center;
}

/* ── Header hero ── */
.app-header {
    background: linear-gradient(135deg, rgba(91, 63, 166, 0.3) 0%, rgba(240, 120, 48, 0.15) 100%);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(91,63,166,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.app-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #c4b0f5 50%, var(--orange) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}
.app-subtitle {
    color: var(--gray-mid);
    font-size: 0.95rem;
    margin-top: 0.5rem;
}

/* ── Transport arrow ── */
.transport-flow {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(240, 120, 48, 0.1);
    border-radius: 8px;
    border: 1px dashed rgba(240, 120, 48, 0.3);
    font-size: 0.9rem;
    color: var(--orange-light);
    font-weight: 600;
}

/* ── Multiselect ── */
.stMultiSelect > div > div {
    background: rgba(15, 27, 53, 0.8) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 8px !important;
}

/* ── Radio ── */
.stRadio > div { flex-direction: row; gap: 1rem; }

/* ── Checkbox ── */
.stCheckbox > label > div:first-child {
    background: rgba(15, 27, 53, 0.8) !important;
    border-color: var(--card-border) !important;
}

/* ── Progress / Spinner ── */
.stSpinner > div { border-top-color: var(--violet) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15, 27, 53, 0.5) !important;
    border-radius: 10px !important;
    padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--gray-mid) !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--violet) !important;
    color: white !important;
}

/* ── Divider ── */
hr { border-color: var(--card-border) !important; }

/* ── Code / mono ── */
code { font-family: 'JetBrains Mono', monospace !important; }
</style>
"""
