# app.py — VAT Chain Analyzer — GOFIN-style UX
"""
Architektura:
  - Silnik regułowy: 100% deterministyczny (logic/rule_engine.py)
  - AI: opcjonalne uzasadnienie, NIE zmienia klasyfikacji
  - Transport domyślnie: kraj A → kraj ostatniego podmiotu
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from ui.styles import CUSTOM_CSS
from ui.components import (
    render_chain_diagram, render_delivery_comments,
    render_summary, render_schema, render_delivery_table,
    render_polish_party_analysis, render_tax_obligation,
    render_jpk, render_warnings, render_legal_basis,
    render_ai_commentary, render_disclaimer,
)
from logic.models import Party, TransactionInput, VatStatus, TransportType
from logic.vat_classifier import classify_vat_transaction
from data.countries import is_eu_country, get_country_name, get_sorted_countries

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VAT Chain Analyzer",
    page_icon="⛓",
    layout="centered",
    initial_sidebar_state="collapsed",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
SORTED_COUNTRIES = get_sorted_countries()
CO = [f"{c} — {n}" for c, n in SORTED_COUNTRIES]
CM = {f"{c} — {n}": c for c, n in SORTED_COUNTRIES}
VAT_STATUSES   = [s.value for s in VatStatus]
TRANSPORT_TYPES = [t.value for t in TransportType]
INCOTERMS_LIST  = ["EXW","FCA","CPT","CIP","DAP","DPU","DDP","FAS","FOB","CFR","CIF"]
DOCS_LIST       = ["CMR","IE-599","konosament","airway bill","faktura","potwierdzenie odbioru"]
DEFAULT_CC      = ["PL","DE","FR","IT","US","CN"]

def copt(code: str) -> str:
    return f"{code} — {get_country_name(code)}"

def cidx(code: str) -> int:
    opt = copt(code)
    return CO.index(opt) if opt in CO else 0

# ════════════════════════════════════════════════════════════════════════════
# PRZYKŁADY GOFIN
# ════════════════════════════════════════════════════════════════════════════
EXAMPLES = {
    "ex1": {
        "label": "1 · UE klasyczne (PL→DE→FR, org. B)",
        "desc":  "PL sprzedaje do DE, DE do FR. DE organizuje transport PL→FR. Dostawa ruchoma DE→FR (WDT), dostawa PL→DE nieruchoma w Polsce.",
        "n": 3,
        "names":   ["Spółka PL","GmbH DE","SA Francja"],
        "cc":      ["PL","DE","FR"],
        "vat":     ["podatnik VAT UE","podatnik VAT UE","podatnik VAT UE"],
        "org": 1, "from": "PL", "to": "FR",
        "transport": "drogowy", "incoterms": "DAP",
        "leave_eu": False, "enter_eu": False, "interm_vat": False,
        "docs": ["CMR","faktura"],
        "import_mode": False,
    },
    "ex2": {
        "label": "2 · Import + WDT (CN→PL→FR)",
        "desc":  "Chiński dostawca sprzedaje do polskiej spółki, która odsprzedaje do Francji. Towar jedzie z Chin do Francji, importer: PL w Polsce. PL: import + WDT.",
        "n": 3,
        "names":   ["Dostawca CN","Spółka PL","SA Francja"],
        "cc":      ["CN","PL","FR"],
        "vat":     ["podatnik spoza UE","podatnik VAT UE","podatnik VAT UE"],
        "org": 1, "from": "CN", "to": "FR",
        "transport": "morski", "incoterms": "CIF",
        "leave_eu": False, "enter_eu": True, "interm_vat": False,
        "docs": ["konosament","IE-599","faktura"],
        "import_mode": True,
        "import_country": "PL", "importer_idx": 1,
    },
    "ex3": {
        "label": "3 · PL pierwszy dostawca (PL→DE→NL)",
        "desc":  "PL sprzedaje do DE, DE do NL. PL organizuje transport PL→NL. Dostawa ruchoma PL→DE (WDT z PL), DE→NL nieruchoma w NL.",
        "n": 3,
        "names":   ["Producent PL","Dystrybutor DE","Nabywca NL"],
        "cc":      ["PL","DE","NL"],
        "vat":     ["podatnik VAT UE","podatnik VAT UE","podatnik VAT UE"],
        "org": 0, "from": "PL", "to": "NL",
        "transport": "drogowy", "incoterms": "FCA",
        "leave_eu": False, "enter_eu": False, "interm_vat": False,
        "docs": ["CMR","faktura","potwierdzenie odbioru"],
        "import_mode": False,
    },
}

# ── Session state init ───────────────────────────────────────────────────────
def _ss_init():
    defaults = {
        "num_parties": 3,
        "party_names":  ["Podmiot A","Podmiot B","Podmiot C","Podmiot D","Podmiot E","Podmiot F"],
        "party_cc":     ["PL","DE","FR","IT","US","CN"],
        "party_vat":    [VAT_STATUSES[0]] + [VAT_STATUSES[1]]*5,
        "org_idx":      0,
        "from_cc":      "PL",
        "to_cc":        "DE",
        "transport":    TRANSPORT_TYPES[0],
        "incoterms":    "FCA",
        "leave_eu":     False,
        "enter_eu":     False,
        "interm_vat":   False,
        "docs":         ["CMR","faktura"],
        "import_mode":  False,
        "import_cc":    "PL",
        "importer_idx": 0,
        "adv_transport":False,
        "use_ai":       False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_ss_init()

def load_example(key: str):
    ex = EXAMPLES[key]
    n  = ex["n"]
    st.session_state["num_parties"] = n
    for i in range(n):
        st.session_state["party_names"][i] = ex["names"][i]
        st.session_state["party_cc"][i]    = ex["cc"][i]
        st.session_state["party_vat"][i]   = ex["vat"][i]
    st.session_state["org_idx"]      = ex["org"]
    st.session_state["from_cc"]      = ex["from"]
    st.session_state["to_cc"]        = ex["to"]
    st.session_state["transport"]    = ex["transport"]
    st.session_state["incoterms"]    = ex["incoterms"]
    st.session_state["leave_eu"]     = ex["leave_eu"]
    st.session_state["enter_eu"]     = ex["enter_eu"]
    st.session_state["interm_vat"]   = ex.get("interm_vat", False)
    st.session_state["docs"]         = ex["docs"]
    st.session_state["import_mode"]  = ex.get("import_mode", False)
    st.session_state["import_cc"]    = ex.get("import_country","PL")
    st.session_state["importer_idx"] = ex.get("importer_idx", 1)
    # sync from/to with party countries when no adv override
    st.session_state["adv_transport"] = False

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="app-hdr">'
    '<div class="app-title">⛓ VAT Chain Analyzer</div>'
    '<div class="app-sub">Deterministyczna analiza VAT transakcji łańcuchowych i trójstronnych · tylko podmioty polskie</div>'
    '<div>'
    '<span class="hpill">art. 7 ust. 8 VAT</span>'
    '<span class="hpill">art. 22 ust. 2–2e VAT</span>'
    '<span class="hpill">TSUE C-245/04</span>'
    '<span class="hpill">TSUE C-430/09</span>'
    '<span class="hpill">TSUE C-386/16</span>'
    '<span class="hpill">art. 22 ust. 4 import</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ════════════════════════════════════════════════════════════════════════════
# PRZYKŁADY — przyciski wczytaj
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="fsec"><div class="fsec-hdr">📚 Wczytaj przykład</div>', unsafe_allow_html=True)
ex_cols = st.columns(3)
for i, (k, ex) in enumerate(EXAMPLES.items()):
    with ex_cols[i]:
        if st.button(ex["label"], key=f"ex_{k}", use_container_width=True):
            load_example(k)
            st.rerun()
        st.caption(ex["desc"])
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# KROK 1 — LICZBA PODMIOTÓW
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="fsec"><div class="fsec-hdr">⚙️ Liczba podmiotów w łańcuchu</div>', unsafe_allow_html=True)
n = st.number_input(
    "Podmioty (3–6)",
    min_value=3, max_value=6,
    value=int(st.session_state["num_parties"]), step=1,
    key="num_parties_input",
    help="Minimalna liczba podmiotów do transakcji łańcuchowej: 3",
)
st.session_state["num_parties"] = int(n)
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# KROK 2 — SCHEMAT (interaktywny, GOFIN-style)
# ════════════════════════════════════════════════════════════════════════════
n = int(st.session_state["num_parties"])

# Determine from/to from party selection (live preview)
# We draw the diagram BEFORE the details form so user sees it first
# Build temp parties for preview
def _preview_parties():
    result = []
    for i in range(n):
        cc  = st.session_state["party_cc"][i] if i < len(st.session_state["party_cc"]) else DEFAULT_CC[min(i, 5)]
        nm  = st.session_state["party_names"][i] if i < len(st.session_state["party_names"]) else f"Podmiot {chr(65+i)}"
        vs  = st.session_state["party_vat"][i] if i < len(st.session_state["party_vat"]) else VAT_STATUSES[0]
        try: vat_st = VatStatus(vs)
        except: vat_st = VatStatus.EU_VAT
        result.append(Party(
            name=nm, country_code=cc, country_name=get_country_name(cc),
            vat_status=vat_st, is_polish=(cc=="PL"), is_eu=is_eu_country(cc), index=i,
        ))
    return result

prev_parties = _preview_parties()
from_cc_default = prev_parties[0].country_code if prev_parties else "PL"
to_cc_default   = prev_parties[-1].country_code if prev_parties else "DE"
if not st.session_state["adv_transport"]:
    st.session_state["from_cc"] = from_cc_default
    st.session_state["to_cc"]   = to_cc_default

# org_idx clamp
org_idx = min(int(st.session_state["org_idx"]), n - 1)
st.session_state["org_idx"] = org_idx

try:
    tr_type = TransportType(st.session_state["transport"])
except:
    tr_type = TransportType.ROAD

prev_input = TransactionInput(
    parties=prev_parties,
    transport_organizer_index=org_idx,
    transport_from_country=st.session_state["from_cc"],
    transport_to_country=st.session_state["to_cc"],
    transport_type=tr_type,
    incoterms=st.session_state["incoterms"],
    intermediary_provided_vat_of_origin=st.session_state["interm_vat"],
    goods_leave_eu=st.session_state["leave_eu"],
    goods_enter_eu=st.session_state["enter_eu"],
    documents=list(st.session_state["docs"]),
    use_ai=False,
)

st.markdown('<div class="fsec-hdr" style="margin-top:.25rem;margin-bottom:.4rem">🔗 Schemat transakcji</div>', unsafe_allow_html=True)
render_chain_diagram(prev_input, result=None)  # live preview before analysis

# ════════════════════════════════════════════════════════════════════════════
# KROK 3 — PODMIOTY
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="fsec"><div class="fsec-hdr">👥 Podmioty w łańcuchu</div>', unsafe_allow_html=True)

grid_cols = 3 if n <= 3 else (2 if n == 4 else 3)
for row_start in range(0, n, grid_cols):
    row_end = min(row_start + grid_cols, n)
    cols = st.columns(row_end - row_start)
    for ci, i in enumerate(range(row_start, row_end)):
        lbl = chr(65 + i)
        cc_default = st.session_state["party_cc"][i] if i < len(st.session_state["party_cc"]) else DEFAULT_CC[min(i,5)]
        nm_default = st.session_state["party_names"][i] if i < len(st.session_state["party_names"]) else f"Podmiot {lbl}"
        vt_default = st.session_state["party_vat"][i] if i < len(st.session_state["party_vat"]) else VAT_STATUSES[1]
        with cols[ci]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:.3rem">'
                f'<div style="width:28px;height:28px;border-radius:7px;background:#eaedfa;color:#4f5fb3;'
                f'font-weight:800;font-size:.95rem;display:flex;align-items:center;justify-content:center">{lbl}</div>'
                f'<span style="font-weight:700;font-size:.85rem;color:#2c3972">Podmiot {lbl}</span></div>',
                unsafe_allow_html=True,
            )
            nm = st.text_input("Nazwa", value=nm_default, key=f"nm_{i}", label_visibility="collapsed", placeholder=f"Podmiot {lbl}")
            st.session_state["party_names"][i] = nm

            cc_sel = st.selectbox(f"Kraj {lbl}", options=CO, index=cidx(cc_default), key=f"cc_{i}")
            cc_val = CM.get(cc_sel, "PL")
            st.session_state["party_cc"][i] = cc_val

            # show UE/non-UE indicator
            is_eu_val = is_eu_country(cc_val)
            eu_txt = "🇪🇺 kraj UE" if is_eu_val else "🌍 poza UE"
            eu_col = "#1d4ed8" if is_eu_val else "#475569"
            st.markdown(f'<div style="font-size:.7rem;color:{eu_col};margin:-6px 0 2px;font-weight:600">{eu_txt}</div>', unsafe_allow_html=True)

            vt_sel = st.selectbox(f"Status VAT {lbl}", options=VAT_STATUSES,
                                  index=VAT_STATUSES.index(vt_default) if vt_default in VAT_STATUSES else 0,
                                  key=f"vt_{i}")
            st.session_state["party_vat"][i] = vt_sel

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# KROK 4 — TRANSPORT I PRZYPISANIE DOSTAWY RUCHOMEJ
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="fsec"><div class="fsec-hdr">🚚 Transport i przypisanie dostawy ruchomej</div>', unsafe_allow_html=True)

party_labels = [f"{chr(65+i)} — {st.session_state['party_names'][i]}" for i in range(n)]

c1, c2, c3 = st.columns(3)
with c1:
    org_default = min(int(st.session_state["org_idx"]), n-1)
    org_sel = st.selectbox(
        "Organizator transportu",
        options=party_labels, index=org_default,
        help="Który podmiot organizuje fizyczny przewóz towaru (art. 22 ust. 2–2d ustawy o VAT)",
    )
    org_idx = party_labels.index(org_sel)
    st.session_state["org_idx"] = org_idx
with c2:
    tr_sel = st.selectbox("Rodzaj transportu", options=TRANSPORT_TYPES,
                          index=TRANSPORT_TYPES.index(st.session_state["transport"]) if st.session_state["transport"] in TRANSPORT_TYPES else 0)
    st.session_state["transport"] = tr_sel
with c3:
    inc_sel = st.selectbox("Incoterms", options=INCOTERMS_LIST,
                           index=INCOTERMS_LIST.index(st.session_state["incoterms"]) if st.session_state["incoterms"] in INCOTERMS_LIST else 0)
    st.session_state["incoterms"] = inc_sel

# Transport domyślnie A → ostatni; opcja zaawansowana
adv = st.checkbox(
    "⚙️ Inne miejsce rozpoczęcia / zakończenia transportu",
    value=bool(st.session_state["adv_transport"]),
    help="Domyślnie towar jedzie od podmiotu A do ostatniego podmiotu. Zaznacz tylko jeśli start/koniec jest inny.",
)
st.session_state["adv_transport"] = adv

if adv:
    ca, cb = st.columns(2)
    with ca:
        from_sel = st.selectbox("Transport z kraju", options=CO,
                                index=cidx(st.session_state["from_cc"]), key="from_sel")
        st.session_state["from_cc"] = CM.get(from_sel, "PL")
    with cb:
        to_sel = st.selectbox("Transport do kraju", options=CO,
                              index=cidx(st.session_state["to_cc"]), key="to_sel")
        st.session_state["to_cc"] = CM.get(to_sel, "PL")
else:
    # auto-sync from party A to last party
    parties_now = _preview_parties()
    if parties_now:
        st.session_state["from_cc"] = parties_now[0].country_code
        st.session_state["to_cc"]   = parties_now[-1].country_code
    st.markdown(
        f'<div class="al al-info" style="margin:.3rem 0">'
        f'📍 Towar transportowany domyślnie z kraju <strong>{st.session_state["from_cc"]}</strong>'
        f' ({get_country_name(st.session_state["from_cc"])}) do kraju <strong>{st.session_state["to_cc"]}</strong>'
        f' ({get_country_name(st.session_state["to_cc"])})'
        f'</div>',
        unsafe_allow_html=True,
    )

# Ostrzeżenie: transport nie A → ostatni
from_cc_now = st.session_state["from_cc"]
to_cc_now   = st.session_state["to_cc"]
parties_check = _preview_parties()
if parties_check and (from_cc_now != parties_check[0].country_code or to_cc_now != parties_check[-1].country_code):
    st.markdown(
        '<div class="al al-warn">⚠️ W transakcji łańcuchowej towar powinien być transportowany bezpośrednio od pierwszego dostawcy do ostatniego nabywcy. '
        'Inny przebieg wymaga weryfikacji, czy nadal mamy transakcję łańcuchową.</div>',
        unsafe_allow_html=True,
    )

cb1, cb2, cb3 = st.columns(3)
with cb1:
    lv = st.checkbox("Towar opuszcza UE (eksport)", value=bool(st.session_state["leave_eu"]))
    st.session_state["leave_eu"] = lv
with cb2:
    ev = st.checkbox("Towar wjeżdża do UE (import)", value=bool(st.session_state["enter_eu"]))
    st.session_state["enter_eu"] = ev
with cb3:
    iv = st.checkbox("Pośrednik podał VAT UE kraju wysyłki",
                     value=bool(st.session_state["interm_vat"]),
                     help="Art. 22 ust. 2c — wpływa na przypisanie dostawy ruchomej")
    st.session_state["interm_vat"] = iv

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# KROK 5 — TRYB IMPORTOWY (warunkowy)
# ════════════════════════════════════════════════════════════════════════════
# Detect import scenario automatically
parties_live  = _preview_parties()
first_non_eu  = parties_live and not parties_live[0].is_eu
has_eu_dest   = parties_live and any(p.is_eu for p in parties_live[1:])
suggest_import = first_non_eu and has_eu_dest

if suggest_import or st.session_state["import_mode"]:
    st.markdown('<div class="fsec"><div class="fsec-hdr">📦 Pytania importowe</div>', unsafe_allow_html=True)

    if suggest_import and not st.session_state["import_mode"]:
        st.markdown(
            '<div class="al al-info">ℹ️ Wykryto scenariusz importowy: pierwszy podmiot poza UE, transport do UE. '
            'Uzupełnij poniższe dane, aby uzyskać prawidłową klasyfikację (art. 22 ust. 4 ustawy o VAT).</div>',
            unsafe_allow_html=True,
        )

    imp_toggle = st.checkbox(
        "Aktywuj tryb importowy",
        value=bool(st.session_state["import_mode"]),
        help="Wymagane gdy towar pochodzi z kraju trzeciego i jest importowany w UE",
    )
    st.session_state["import_mode"] = imp_toggle

    if imp_toggle:
        im1, im2 = st.columns(2)
        with im1:
            imp_cc_sel = st.selectbox(
                "Kraj importu (gdzie dokonano odprawy celnej)",
                options=CO, index=cidx(st.session_state["import_cc"]), key="imp_cc_sel",
            )
            st.session_state["import_cc"] = CM.get(imp_cc_sel, "PL")
        with im2:
            eu_parties_labels = [f"{chr(65+i)} — {st.session_state['party_names'][i]}"
                                  for i in range(n) if is_eu_country(st.session_state["party_cc"][i])]
            all_party_labels = [f"{chr(65+i)} — {st.session_state['party_names'][i]}" for i in range(n)]
            importer_default = min(int(st.session_state["importer_idx"]), n-1)
            imp_lbl = st.selectbox(
                "Importer (podmiot w dokumentach celnych)",
                options=all_party_labels, index=importer_default, key="imp_lbl_sel",
                help="Art. 22 ust. 4: dostawa przez importera uznana za dokonaną w kraju importu",
            )
            imp_idx = all_party_labels.index(imp_lbl)
            st.session_state["importer_idx"] = imp_idx

        imp_cc = st.session_state["import_cc"]
        imp_nm = st.session_state["party_names"][imp_idx]
        imp_country_name = get_country_name(imp_cc)
        st.markdown(
            f'<div class="import-box">📦 <strong>Importer:</strong> {imp_nm} · '
            f'<strong>Kraj importu:</strong> {imp_cc} ({imp_country_name})<br>'
            f'<small>Art. 22 ust. 4: Dostawa dokonywana przez podatnika, który jest jednocześnie '
            f'podatnikiem z tytułu importu, uznawana jest za dokonaną w {imp_country_name}.</small>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# KROK 6 — DOKUMENTY
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="fsec"><div class="fsec-hdr">📄 Dokumenty</div>', unsafe_allow_html=True)
docs_sel = st.multiselect(
    "Posiadane dokumenty (wpływają na stawkę 0%)",
    options=DOCS_LIST,
    default=list(st.session_state["docs"]),
    help="art. 42 (WDT), art. 41 ust. 6 (eksport)",
)
st.session_state["docs"] = docs_sel
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# KROK 7 — AI opcjonalne
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="fsec"><div class="fsec-hdr">🤖 Komentarz AI <span style="font-weight:400;font-size:.78rem;color:#94a3b8">(opcjonalne)</span></div>', unsafe_allow_html=True)
use_ai = st.checkbox(
    "Wygeneruj komentarz ekspercki AI po analizie",
    value=bool(st.session_state["use_ai"]),
    help="AI opisuje wynik silnika regułowego — nie zmienia klasyfikacji VAT.",
)
st.session_state["use_ai"] = use_ai
if use_ai:
    st.markdown('<div class="al al-warn" style="margin:.3rem 0">💡 Generowanie komentarza AI może wiązać się z kosztem API OpenAI. Identyczne scenariusze korzystają z cache (SHA256).</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# BUDOWANIE MODELU
# ════════════════════════════════════════════════════════════════════════════
parties: list[Party] = []
for i in range(n):
    cc  = st.session_state["party_cc"][i] if i < len(st.session_state["party_cc"]) else DEFAULT_CC[min(i,5)]
    nm  = st.session_state["party_names"][i] if i < len(st.session_state["party_names"]) else f"Podmiot {chr(65+i)}"
    vs  = st.session_state["party_vat"][i] if i < len(st.session_state["party_vat"]) else VAT_STATUSES[0]
    try: vat_st = VatStatus(vs)
    except: vat_st = VatStatus.EU_VAT
    parties.append(Party(
        name=nm, country_code=cc, country_name=get_country_name(cc),
        vat_status=vat_st, is_polish=(cc=="PL"), is_eu=is_eu_country(cc), index=i,
    ))

try: tr_type = TransportType(st.session_state["transport"])
except: tr_type = TransportType.ROAD

input_data = TransactionInput(
    parties=parties,
    transport_organizer_index=min(int(st.session_state["org_idx"]), n-1),
    transport_from_country=st.session_state["from_cc"],
    transport_to_country=st.session_state["to_cc"],
    transport_type=tr_type,
    incoterms=st.session_state["incoterms"],
    intermediary_provided_vat_of_origin=bool(st.session_state["interm_vat"]),
    goods_leave_eu=bool(st.session_state["leave_eu"]),
    goods_enter_eu=bool(st.session_state["enter_eu"]),
    documents=list(st.session_state["docs"]),
    use_ai=bool(st.session_state["use_ai"]),
)
has_polish = any(p.is_polish for p in parties)

# ════════════════════════════════════════════════════════════════════════════
# CTA BUTTON
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:.25rem'></div>", unsafe_allow_html=True)
ca_btn, _ = st.columns([2, 1])
with ca_btn:
    st.markdown('<div class="btn-cta">', unsafe_allow_html=True)
    analyze = st.button("⚡ Analizuj transakcję VAT", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Walidacja ────────────────────────────────────────────────────────────────
if analyze:
    errors = []
    if not has_polish:
        errors.append("🇵🇱 Aplikacja analizuje wyłącznie transakcje z udziałem podmiotu polskiego. Zmień kraj jednego z podmiotów na PL.")
    if st.session_state["import_mode"] and not st.session_state["enter_eu"]:
        errors.append("📦 Tryb importowy wymaga zaznaczenia opcji 'Towar wjeżdża do UE'.")
    if errors:
        for e in errors:
            st.markdown(f'<div class="al al-err">{e}</div>', unsafe_allow_html=True)
        st.stop()

# ════════════════════════════════════════════════════════════════════════════
# WYNIKI
# ════════════════════════════════════════════════════════════════════════════
if analyze and has_polish:
    st.markdown("<hr>", unsafe_allow_html=True)
    with st.spinner("Silnik regułowy w toku…"):
        result = classify_vat_transaction(input_data)

    # Chain banner
    tri = " │ 🔺 Możliwa procedura trójstronna uproszczona (art. 135–138)" if result.triangular_simplified_possible else ""
    ch  = f"✅ Transakcja łańcuchowa — {result.num_deliveries} {'dostawy' if result.num_deliveries < 5 else 'dostaw'}" if result.is_chain_transaction else "ℹ️ Nie jest transakcją łańcuchową"
    st.markdown(f'<div class="chain-banner">{ch}{tri}</div>', unsafe_allow_html=True)

    # Import info banner
    if st.session_state["import_mode"] and st.session_state["enter_eu"]:
        imp_idx = min(int(st.session_state["importer_idx"]), n-1)
        imp_name = parties[imp_idx].name
        imp_cc   = st.session_state["import_cc"]
        st.markdown(
            f'<div class="import-box">📦 <strong>Tryb importowy:</strong> importer — '
            f'<strong>{imp_name}</strong> · kraj importu — <strong>{imp_cc} ({get_country_name(imp_cc)})</strong> · '
            f'art. 22 ust. 4 ustawy o VAT</div>',
            unsafe_allow_html=True,
        )

    # ── Schemat z wynikami ─────────────────────────────────────────────────
    st.markdown('<div class="sec-title">🔗 Schemat transakcji — wynik analizy</div>', unsafe_allow_html=True)
    render_chain_diagram(input_data, result)

    # ── Komentarz GOFIN-style ──────────────────────────────────────────────
    render_delivery_comments(result)

    # ── Taby szczegółowe ───────────────────────────────────────────────────
    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "📋 Podsumowanie",
        "📊 Tabela",
        "🇵🇱 Polski podmiot",
        "⏰ Obowiązek",
        "📁 JPK_V7",
        "⚠️ Ryzyka",
        "⚖️ Prawo",
    ])
    with t1: render_summary(input_data)
    with t2: render_delivery_table(result)
    with t3: render_polish_party_analysis(result)
    with t4: render_tax_obligation(result)
    with t5: render_jpk(result)
    with t6:
        render_warnings(result)
        if not result.warnings and not result.requires_verification:
            st.markdown('<div class="al al-ok">✅ Silnik regułowy nie wykrył krytycznych ryzyk.</div>', unsafe_allow_html=True)
    with t7: render_legal_basis(result)

    # ── AI ──────────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    if use_ai:
        ca2, _ = st.columns([2, 1])
        with ca2:
            st.markdown('<div class="btn-cta">', unsafe_allow_html=True)
            gen_ai = st.button("🤖 Wygeneruj komentarz ekspercki AI", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        if gen_ai:
            api_ok = bool(os.environ.get("OPENAI_API_KEY") or
                         (hasattr(st,"secrets") and st.secrets.get("OPENAI_API_KEY")))
            if not api_ok:
                st.markdown('<div class="al al-err">🔑 Brak klucza API. Ustaw zmienną <code>OPENAI_API_KEY</code>.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Generuję komentarz AI…"):
                    from ai.ai_service import generate_ai_commentary
                    commentary, from_cache = generate_ai_commentary(input_data, result)
                render_ai_commentary(commentary, from_cache)
    else:
        st.markdown('<div class="al al-info">🤖 Komentarz AI wyłączony. Włącz opcję AI w formularzu.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# EKRAN STARTOWY
# ════════════════════════════════════════════════════════════════════════════
elif not analyze:
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="welcome-card">'
        '<div style="font-size:2.75rem;margin-bottom:.6rem">⛓</div>'
        '<h2>Gotowy do analizy</h2>'
        '<p style="max-width:430px;margin:.4rem auto 1.2rem">'
        'Wczytaj przykład GOFIN lub skonfiguruj transakcję ręcznie. '
        'Kliknij <strong>Analizuj transakcję VAT</strong> — wymagany podmiot polski (PL).</p>'
        '<div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap">'
        '<div class="wp"><div class="wpi">⚖️</div><div class="wpl">Silnik regułowy<br>art. 7 ust. 8</div></div>'
        '<div class="wp"><div class="wpi">🔺</div><div class="wpl">Trójstronna<br>art. 135–138</div></div>'
        '<div class="wp"><div class="wpi">📦</div><div class="wpl">Import<br>art. 22 ust. 4</div></div>'
        '<div class="wp"><div class="wpi">📁</div><div class="wpl">JPK_V7<br>TT_WNT · TT_D</div></div>'
        '<div class="wp"><div class="wpi">🏛</div><div class="wpl">TSUE<br>C-245/04 · C-430/09</div></div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

render_disclaimer()
