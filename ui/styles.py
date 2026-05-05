# ui/styles.py  —  VAT Chain Analyzer  —  jasny profesjonalny motyw
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ══ TOKENS ══════════════════════════════════════════════════════════════ */
:root {
  --bg:        #f5f7fb;
  --surf:      #ffffff;
  --surf2:     #f1f4f9;
  --border:    #dde3ee;
  --focus:     #4f5fb3;

  --navy:      #2c3972;
  --violet:    #4f5fb3;
  --violet-lt: #eaedfa;
  --orange:    #f97316;
  --orange-lt: #fff7ed;

  --ink:       #0f172a;
  --ink2:      #475569;
  --muted:     #94a3b8;

  --ok:        #15803d;  --ok-bg:  #f0fdf4;
  --warn:      #92400e;  --warn-bg:#fffbeb;
  --err:       #b91c1c;  --err-bg: #fef2f2;
  --info:      #1e40af;  --info-bg:#eff6ff;

  --r4:4px; --r8:8px; --r12:12px; --r16:16px;
  --shadow: 0 1px 4px rgba(0,0,0,.08),0 1px 2px rgba(0,0,0,.05);
  --shadow2:0 4px 14px rgba(0,0,0,.08),0 2px 6px rgba(0,0,0,.05);
}

/* ══ BASE ════════════════════════════════════════════════════════════════ */
html,body,.stApp,[data-testid="stAppViewContainer"] {
  background:#f5f7fb !important;
  font-family:'Inter',system-ui,sans-serif !important;
  color:#0f172a !important;
}
[data-testid="stMain"],[data-testid="block-container"] {
  background:#f5f7fb !important;
  padding-top:1rem !important;
}
/* kill sidebar */
[data-testid="stSidebar"],[data-testid="collapsedControl"] { display:none !important; }
#MainMenu,footer { visibility:hidden !important; }
header[data-testid="stHeader"] { background:transparent !important; }

/* ══ GLOBAL TEXT — DARK EVERYWHERE ══════════════════════════════════════ */
p,span,div,li,td,th,label,
.stMarkdown,.stMarkdown p,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {
  color:#0f172a !important;
  font-family:'Inter',system-ui,sans-serif !important;
}
h1,h2,h3,h4,h5,h6 {
  color:#0f172a !important; font-weight:700 !important;
  font-family:'Inter',system-ui,sans-serif !important;
}
code,pre { font-family:'JetBrains Mono',monospace !important; color:#2c3972 !important; }

/* ══ FORM INPUTS ═════════════════════════════════════════════════════════ */
/* text / number */
.stTextInput input,
.stNumberInput input,
input[type=text],input[type=number] {
  background:#fff !important; color:#0f172a !important;
  border:1.5px solid var(--border) !important;
  border-radius:var(--r8) !important;
  font-size:.88rem !important;
  font-family:'Inter',sans-serif !important;
  padding:.4rem .7rem !important;
}
.stTextInput input::placeholder { color:#94a3b8 !important; }
.stTextInput input:focus,.stNumberInput input:focus {
  border-color:var(--focus) !important;
  box-shadow:0 0 0 3px rgba(79,95,179,.15) !important; outline:none !important;
}
/* selectbox */
.stSelectbox>div>div,
.stSelectbox>div>div>div,
[data-baseweb=select],
[data-baseweb=select]>div,
[data-baseweb=select] input,
div[data-baseweb=select] div {
  background:#fff !important; color:#0f172a !important;
  font-family:'Inter',sans-serif !important;
}
[data-baseweb=select]>div {
  border:1.5px solid var(--border) !important;
  border-radius:var(--r8) !important;
}
[data-baseweb=select]>div:focus-within {
  border-color:var(--focus) !important;
  box-shadow:0 0 0 3px rgba(79,95,179,.15) !important;
}
[data-baseweb=popover] ul,[data-baseweb=menu],[role=listbox] {
  background:#fff !important; border:1px solid var(--border) !important;
  border-radius:var(--r12) !important; box-shadow:var(--shadow2) !important;
}
[role=option],[data-baseweb=menu-item] {
  color:#0f172a !important; background:#fff !important;
}
[role=option]:hover  { background:var(--violet-lt) !important; }
[aria-selected=true] { background:var(--violet-lt) !important; color:var(--violet) !important; }
/* multiselect */
.stMultiSelect [data-baseweb=select]>div {
  background:#fff !important; color:#0f172a !important; border-color:var(--border) !important;
}
[data-baseweb=tag] {
  background:var(--violet-lt) !important; color:var(--violet) !important;
  border:1px solid rgba(79,95,179,.3) !important; border-radius:6px !important;
}
[data-baseweb=tag] span { color:var(--violet) !important; }
/* textarea */
textarea { background:#fff !important; color:#0f172a !important; border:1.5px solid var(--border) !important; border-radius:var(--r8) !important; }

/* labels */
.stTextInput label,.stNumberInput label,
.stSelectbox label,.stMultiSelect label,
.stCheckbox label,.stRadio label {
  color:#475569 !important; font-size:.76rem !important;
  font-weight:700 !important; text-transform:uppercase !important;
  letter-spacing:.05em !important;
}
.stCheckbox label { text-transform:none !important; font-size:.88rem !important; }
.stCheckbox span,[data-testid=stCheckbox] label p { color:#0f172a !important; }

/* ══ BUTTONS ═════════════════════════════════════════════════════════════ */
.stButton>button {
  background:linear-gradient(135deg,var(--violet) 0%,#6572cc 100%) !important;
  color:#fff !important; border:none !important;
  border-radius:var(--r8) !important;
  font-family:'Inter',sans-serif !important;
  font-weight:600 !important; font-size:.88rem !important;
  padding:.5rem 1.2rem !important;
  box-shadow:0 2px 8px rgba(79,95,179,.28) !important;
  transition:all .15s ease !important;
}
.stButton>button:hover {
  transform:translateY(-1px) !important;
  box-shadow:0 4px 14px rgba(79,95,179,.38) !important;
}
.stButton>button:disabled {
  background:#e2e8f0 !important; color:#94a3b8 !important;
  box-shadow:none !important; transform:none !important;
}
.btn-cta .stButton>button {
  background:linear-gradient(135deg,var(--orange) 0%,#fb923c 100%) !important;
  font-size:.95rem !important; font-weight:700 !important;
  padding:.65rem 2rem !important;
  box-shadow:0 3px 12px rgba(249,115,22,.35) !important; width:100% !important;
}
.btn-cta .stButton>button:hover {
  box-shadow:0 5px 18px rgba(249,115,22,.45) !important;
}
.btn-secondary .stButton>button {
  background:#fff !important; color:var(--violet) !important;
  border:1.5px solid var(--violet) !important;
  box-shadow:none !important;
}
.btn-secondary .stButton>button:hover {
  background:var(--violet-lt) !important; transform:none !important;
}

/* ══ TABS ════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb=tab-list] {
  background:var(--surf2) !important; border-radius:var(--r8) !important;
  padding:3px !important; border:1px solid var(--border) !important; gap:2px !important;
}
.stTabs [data-baseweb=tab] {
  color:var(--ink2) !important; font-weight:600 !important;
  font-size:.79rem !important; border-radius:6px !important;
  background:transparent !important; padding:5px 12px !important;
}
.stTabs [aria-selected=true] {
  background:#fff !important; color:var(--violet) !important;
  box-shadow:var(--shadow) !important;
}
.stTabs [data-baseweb=tab-panel] { padding-top:.75rem !important; }

/* ══ EXPANDER ════════════════════════════════════════════════════════════ */
[data-testid=stExpander] {
  border:1px solid var(--border) !important;
  border-radius:var(--r8) !important; background:#fff !important;
  margin-bottom:.4rem !important;
}
[data-testid=stExpander] summary { color:#0f172a !important; font-weight:600 !important; font-size:.85rem !important; }
[data-testid=stExpander]>div>div { background:#fff !important; }

/* ══ DATAFRAME ═══════════════════════════════════════════════════════════ */
[data-testid=stDataFrame] {
  border-radius:var(--r12) !important; overflow:hidden !important;
  border:1px solid var(--border) !important;
}
[data-testid=stDataFrame] th {
  background:var(--surf2) !important; color:var(--ink2) !important;
  font-size:.72rem !important; font-weight:700 !important; text-transform:uppercase !important;
}
[data-testid=stDataFrame] td { color:#0f172a !important; font-size:.83rem !important; }

/* ══ ALERTS ══════════════════════════════════════════════════════════════ */
.al { border-radius:var(--r8); padding:.65rem .9rem; font-size:.85rem; margin:.3rem 0; line-height:1.5; }
.al-ok   { background:var(--ok-bg);   border-left:4px solid var(--ok);   }
.al-ok,.al-ok *   { color:#14532d !important; }
.al-warn { background:var(--warn-bg); border-left:4px solid #f59e0b;     }
.al-warn,.al-warn * { color:#78350f !important; }
.al-err  { background:var(--err-bg);  border-left:4px solid var(--err);  }
.al-err,.al-err *  { color:#7f1d1d !important; }
.al-info { background:var(--info-bg); border-left:4px solid #3b82f6;     }
.al-info,.al-info * { color:#1e3a8a !important; }
/* legacy aliases */
.alert-success { background:var(--ok-bg);   border-left:4px solid var(--ok);  border-radius:var(--r8); padding:.65rem .9rem; font-size:.85rem; margin:.3rem 0; }
.alert-success,.alert-success * { color:#14532d !important; }
.alert-warning { background:var(--warn-bg); border-left:4px solid #f59e0b; border-radius:var(--r8); padding:.65rem .9rem; font-size:.85rem; margin:.3rem 0; }
.alert-warning,.alert-warning * { color:#78350f !important; }
.alert-danger  { background:var(--err-bg);  border-left:4px solid var(--err);  border-radius:var(--r8); padding:.65rem .9rem; font-size:.85rem; margin:.3rem 0; }
.alert-danger,.alert-danger *  { color:#7f1d1d !important; }
.alert-info    { background:var(--info-bg); border-left:4px solid #3b82f6; border-radius:var(--r8); padding:.65rem .9rem; font-size:.85rem; margin:.3rem 0; }
.alert-info,.alert-info *    { color:#1e3a8a !important; }

/* ══ BADGES ══════════════════════════════════════════════════════════════ */
.badge {
  display:inline-block; padding:2px 7px; border-radius:20px;
  font-size:.68rem; font-weight:700; text-transform:uppercase;
  letter-spacing:.04em; line-height:1.5;
}
.bwdt     {background:#eaedfa;color:#3a4b9e;border:1px solid #b8c1e8;}
.bwnt     {background:#f0ebff;color:#6d28d9;border:1px solid #c4b5fd;}
.bexp     {background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;}
.bimp     {background:#fffbeb;color:#92400e;border:1px solid #fde68a;}
.bdom     {background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;}
.bout     {background:#f8fafc;color:#475569;border:1px solid #cbd5e1;}
.bunk     {background:var(--err-bg);color:var(--err);border:1px solid #fecaca;}
.bmov     {background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;font-weight:800;}
.bimm     {background:#f8fafc;color:#64748b;border:1px solid #e2e8f0;}
.bpl      {background:var(--err-bg);color:var(--err);border:1px solid #fecaca;}
.beu      {background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;}
.bnoneu   {background:#f8fafc;color:#475569;border:1px solid #cbd5e1;}
/* legacy */
.badge-wdt{background:#eaedfa;color:#3a4b9e;border:1px solid #b8c1e8;}
.badge-wnt{background:#f0ebff;color:#6d28d9;border:1px solid #c4b5fd;}
.badge-export{background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;}
.badge-import{background:#fffbeb;color:#92400e;border:1px solid #fde68a;}
.badge-domestic{background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;}
.badge-outside{background:#f8fafc;color:#475569;border:1px solid #cbd5e1;}
.badge-unknown{background:var(--err-bg);color:var(--err);border:1px solid #fecaca;}
.badge-movable{background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;font-weight:800;}
.badge-immovable{background:#f8fafc;color:#64748b;border:1px solid #e2e8f0;}
.badge-pl{background:var(--err-bg);color:var(--err);border:1px solid #fecaca;}
.badge-eu{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;}
.badge-non-eu{background:#f8fafc;color:#475569;border:1px solid #cbd5e1;}

/* ══ CARDS ═══════════════════════════════════════════════════════════════ */
.card {
  background:#fff; border:1px solid var(--border);
  border-radius:var(--r12); padding:1.1rem 1.25rem;
  box-shadow:var(--shadow); margin-bottom:1rem;
}
.card-sm { padding:.75rem 1rem; }
.card-title {
  font-size:.7rem; font-weight:700; text-transform:uppercase;
  letter-spacing:.07em; color:var(--muted); margin-bottom:.6rem;
}
.card,.card p,.card div,.card span { color:#0f172a !important; }
/* legacy vat-card */
.vat-card { background:#fff; border:1px solid var(--border); border-radius:var(--r12); padding:1rem 1.2rem; box-shadow:var(--shadow); margin-bottom:.9rem; }
.vat-card-header { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); margin-bottom:.6rem; }
.vat-card,.vat-card p,.vat-card div,.vat-card span { color:#0f172a !important; }

/* ══ APP HEADER ══════════════════════════════════════════════════════════ */
.app-hdr {
  background:linear-gradient(135deg,var(--navy) 0%,#3d52a0 100%);
  border-radius:var(--r16); padding:1.4rem 1.75rem; margin-bottom:1.25rem;
  position:relative; overflow:hidden;
}
.app-hdr::after {
  content:''; position:absolute; right:-30px; top:-30px;
  width:160px; height:160px;
  background:radial-gradient(circle,rgba(255,255,255,.07) 0%,transparent 70%);
  border-radius:50%;
}
.app-title {
  font-size:1.55rem; font-weight:800;
  color:#fff !important; -webkit-text-fill-color:#fff;
  margin:0 0 .3rem; letter-spacing:-.02em;
}
.app-sub { color:rgba(255,255,255,.7) !important; font-size:.8rem; line-height:1.5; }
.hpill {
  display:inline-block; background:rgba(255,255,255,.13);
  border:1px solid rgba(255,255,255,.22); border-radius:20px;
  padding:2px 8px; font-size:.68rem; font-weight:600;
  color:rgba(255,255,255,.85) !important; margin:.45rem .25rem 0 0;
}

/* ══ SECTION TITLE ═══════════════════════════════════════════════════════ */
.sec-title {
  font-size:.95rem; font-weight:700; color:var(--navy) !important;
  margin:1.4rem 0 .75rem;
  padding-bottom:.45rem; border-bottom:2px solid var(--border);
  display:flex; align-items:center; gap:7px;
}
.sec-title,.sec-title * { color:var(--navy) !important; }
/* legacy */
.section-title { font-size:.95rem; font-weight:700; color:var(--navy) !important; margin:1.4rem 0 .75rem; padding-bottom:.45rem; border-bottom:2px solid var(--border); display:flex; align-items:center; gap:7px; }
.section-title,.section-title * { color:var(--navy) !important; }

/* ══ FORM SECTION ════════════════════════════════════════════════════════ */
.fsec {
  background:#fff; border:1px solid var(--border);
  border-radius:var(--r12); padding:1rem 1.25rem;
  box-shadow:var(--shadow); margin-bottom:.9rem;
}
.fsec-hdr {
  font-size:.85rem; font-weight:700; color:var(--navy) !important;
  margin:0 0 .85rem; display:flex; align-items:center; gap:6px;
}
.fsec-hdr,.fsec-hdr * { color:var(--navy) !important; }

/* ══ GOFIN-STYLE CHAIN DIAGRAM ═══════════════════════════════════════════ */
.chain-diagram {
  background:#fff; border:1px solid var(--border);
  border-radius:var(--r16); padding:1.5rem 1.25rem 1rem;
  box-shadow:var(--shadow2); margin-bottom:1rem;
}
.chain-row {
  display:flex; align-items:center; justify-content:center;
  gap:0; width:100%; position:relative;
}
.chain-node {
  background:#fff; border:2px solid var(--border);
  border-radius:var(--r12); padding:.7rem .9rem; min-width:120px;
  text-align:center; flex-shrink:0; transition:border-color .15s;
}
.chain-node.is-pl    { border-color:#ef4444; background:#fff5f5; }
.chain-node.is-org   { border-color:var(--orange); background:var(--orange-lt); }
.chain-node .n-letter { font-size:1.4rem; font-weight:800; color:var(--violet); line-height:1; }
.chain-node .n-name   { font-size:.75rem; font-weight:700; color:#0f172a; margin-top:2px; }
.chain-node .n-country{ font-size:.68rem; color:#475569; }
.chain-node .n-status { font-size:.62rem; color:#94a3b8; margin-top:1px; }

.chain-arrow {
  display:flex; flex-direction:column; align-items:center;
  gap:2px; padding:0 .25rem; flex-shrink:0; min-width:80px;
}
.chain-arrow .del-label {
  font-size:.6rem; font-weight:700; text-transform:uppercase;
  letter-spacing:.06em; color:var(--violet); white-space:nowrap;
}
.chain-arrow .arr-line {
  display:flex; align-items:center; gap:2px; width:100%;
}
.chain-arrow .arr-dash {
  flex:1; height:2px;
  background:repeating-linear-gradient(90deg,var(--violet) 0,var(--violet) 6px,transparent 6px,transparent 10px);
}
.chain-arrow.is-mov .del-label { color:var(--orange); }
.chain-arrow.is-mov .arr-dash  {
  background:repeating-linear-gradient(90deg,var(--orange) 0,var(--orange) 6px,transparent 6px,transparent 10px);
}
.chain-arrow .arr-head { font-size:.85rem; color:var(--violet); line-height:1; }
.chain-arrow.is-mov .arr-head { color:var(--orange); }

.transport-bar {
  display:flex; align-items:center; gap:8px;
  margin-top:.9rem; padding:.55rem .9rem;
  background:var(--orange-lt); border:1px solid #fed7aa;
  border-radius:var(--r8); font-size:.83rem; font-weight:600;
  color:#c2410c !important;
}
.transport-bar,.transport-bar * { color:#c2410c !important; }
.transport-bar code { color:#c2410c !important; background:rgba(255,255,255,.6) !important; padding:0 4px; border-radius:3px; font-size:.78rem; }

/* ══ DELIVERY COMMENT CARDS (GOFIN-style) ═══════════════════════════════ */
.del-comment {
  background:#fff; border:1px solid var(--border);
  border-left:4px solid var(--violet);
  border-radius:0 var(--r8) var(--r8) 0;
  padding:.75rem 1rem; margin:.4rem 0;
}
.del-comment.is-mov { border-left-color:var(--orange); }
.del-comment .dc-head {
  font-size:.72rem; font-weight:700; text-transform:uppercase;
  letter-spacing:.05em; color:var(--violet); margin-bottom:.35rem;
}
.del-comment.is-mov .dc-head { color:var(--orange); }
.del-comment,.del-comment p,.del-comment div,.del-comment span { color:#0f172a !important; }

/* ══ PARTY NODE (result schema) ══════════════════════════════════════════ */
.party-node {
  background:#fff; border:1.5px solid var(--border);
  border-radius:var(--r12); padding:.9rem .7rem; text-align:center;
}
.party-node,.party-node p,.party-node div,.party-node span { color:#0f172a !important; }
.party-node.polish    { border-color:#ef4444; background:#fff5f5; }
.party-node.organizer { border-color:var(--orange); background:var(--orange-lt); }

/* ══ CHAIN BANNER ════════════════════════════════════════════════════════ */
.chain-banner {
  background:linear-gradient(90deg,var(--violet-lt) 0%,#f3f4fc 100%);
  border:1px solid #b8c1e8; border-radius:var(--r12);
  padding:.8rem 1.1rem; font-weight:700; font-size:.9rem;
  color:var(--violet) !important; margin-bottom:1rem;
  display:flex; align-items:center; gap:8px;
}
.chain-banner,.chain-banner * { color:var(--violet) !important; }

/* ══ WELCOME ═════════════════════════════════════════════════════════════ */
.welcome-card {
  background:#fff; border:1px solid var(--border);
  border-radius:var(--r16); padding:2rem; text-align:center;
  box-shadow:var(--shadow);
}
.welcome-card h2 { color:var(--navy) !important; font-size:1.25rem !important; }
.welcome-card p  { color:#475569 !important; }
.wp {
  display:inline-flex; flex-direction:column; align-items:center;
  gap:4px; padding:.85rem .75rem; background:var(--surf2);
  border:1px solid var(--border); border-radius:var(--r12); min-width:100px;
}
.wp .wpi { font-size:1.6rem; }
.wp .wpl { font-size:.68rem; font-weight:600; color:#475569 !important; text-align:center; line-height:1.35; }

/* ══ DISCLAIMER ══════════════════════════════════════════════════════════ */
.disclaimer {
  background:var(--surf2); border:1px solid var(--border);
  border-radius:var(--r8); padding:.75rem 1.1rem;
  font-size:.75rem; margin-top:2.5rem; text-align:center; line-height:1.55;
}
.disclaimer,.disclaimer * { color:var(--muted) !important; }

/* ══ MISC ════════════════════════════════════════════════════════════════ */
hr { border-color:var(--border) !important; margin:1.25rem 0 !important; }
.stSpinner>div { border-top-color:var(--violet) !important; }
.confidence-high   { color:var(--ok)  !important; font-weight:700; }
.confidence-medium { color:#92400e !important; font-weight:700; }
.confidence-low    { color:var(--err) !important; font-weight:700; }
.confidence-verify { color:var(--err) !important; font-weight:700; }

/* import highlight */
.import-box {
  background:#fffbeb; border:1.5px solid #fde68a;
  border-radius:var(--r8); padding:.75rem 1rem; margin:.5rem 0;
}
.import-box,.import-box * { color:#78350f !important; }

/* number input stepper */
.stNumberInput button { background:var(--surf2) !important; border:1px solid var(--border) !important; color:#0f172a !important; }
</style>
"""
