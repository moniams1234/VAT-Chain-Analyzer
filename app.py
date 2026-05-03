# app.py
"""
VAT Chain Analyzer — Aplikacja do analizy VAT transakcji łańcuchowych i trójstronnych.

Zasada architektoniczna:
- 90% pracy wykonuje deterministyczny silnik regułowy (logic/rule_engine.py)
- AI jest opcjonalne i służy wyłącznie do opisu/uzasadnienia — NIE zmienia klasyfikacji
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from ui.styles import CUSTOM_CSS
from ui.components import (
    render_summary, render_schema, render_delivery_table,
    render_polish_party_analysis, render_tax_obligation,
    render_jpk, render_warnings, render_legal_basis,
    render_ai_commentary, render_disclaimer,
)
from logic.models import (
    Party, TransactionInput, VatStatus, TransportType
)
from logic.vat_classifier import classify_vat_transaction
from data.countries import is_eu_country, get_country_name, get_sorted_countries, EU_COUNTRIES

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VAT Chain Analyzer",
    page_icon="⛓",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
SORTED_COUNTRIES = get_sorted_countries()
COUNTRY_OPTIONS = [f"{code} — {name}" for code, name in SORTED_COUNTRIES]
COUNTRY_CODE_MAP = {f"{code} — {name}": code for code, name in SORTED_COUNTRIES}

VAT_STATUSES = [s.value for s in VatStatus]
TRANSPORT_TYPES = [t.value for t in TransportType]
INCOTERMS_LIST = ["EXW", "FCA", "CPT", "CIP", "DAP", "DPU", "DDP", "FAS", "FOB", "CFR", "CIF"]
DOCUMENTS_LIST = ["CMR", "IE-599", "konosament", "airway bill", "faktura", "potwierdzenie odbioru"]


def get_default_country_option(code: str) -> str:
    name = get_country_name(code)
    return f"{code} — {name}"


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="app-header">'
    '<h1 class="app-title">⛓ VAT Chain Analyzer</h1>'
    '<p class="app-subtitle">'
    'Deterministyczna analiza VAT transakcji łańcuchowych i trójstronnych | '
    'Podstawa: art. 7 ust. 8, art. 22 ust. 2–2e ustawy o VAT | TSUE C-245/04, C-430/09, C-386/16, C-401/18'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Sidebar — form inputs ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-weight:800;font-size:1.1rem;margin-bottom:1rem;color:#c4b0f5">'
        '⚙️ Konfiguracja transakcji'
        '</div>',
        unsafe_allow_html=True,
    )

    # Number of parties
    num_parties = st.number_input(
        "Liczba podmiotów w łańcuchu",
        min_value=3, max_value=6, value=3, step=1,
        help="Minimalna liczba podmiotów do analizy transakcji łańcuchowej: 3",
    )

    st.markdown("---")
    st.markdown(
        '<div style="font-weight:700;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#f07830;margin-bottom:0.5rem">'
        '👥 Podmioty'
        '</div>',
        unsafe_allow_html=True,
    )

    # Party inputs
    party_configs = []
    default_countries = ["PL", "DE", "FR", "IT", "US", "CN"]

    for i in range(int(num_parties)):
        label = chr(65 + i)
        with st.expander(f"Podmiot {label}", expanded=(i < 3)):
            name = st.text_input(
                f"Nazwa podmiotu {label}",
                value=f"Podmiot {label}",
                key=f"name_{i}",
            )
            default_code = default_countries[i] if i < len(default_countries) else "PL"
            default_opt = get_default_country_option(default_code)
            country_opt = st.selectbox(
                f"Kraj {label}",
                options=COUNTRY_OPTIONS,
                index=COUNTRY_OPTIONS.index(default_opt) if default_opt in COUNTRY_OPTIONS else 0,
                key=f"country_{i}",
            )
            country_code = COUNTRY_CODE_MAP.get(country_opt, "PL")
            vat_status_str = st.selectbox(
                f"Status VAT {label}",
                options=VAT_STATUSES,
                index=1 if i > 0 else 0,
                key=f"vat_{i}",
            )
            party_configs.append({
                "name": name,
                "country_code": country_code,
                "vat_status": vat_status_str,
                "index": i,
            })

    st.markdown("---")
    st.markdown(
        '<div style="font-weight:700;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#f07830;margin-bottom:0.5rem">'
        '🚚 Transport'
        '</div>',
        unsafe_allow_html=True,
    )

    party_labels = [f"{chr(65+i)} — {party_configs[i]['name']}" for i in range(int(num_parties))]
    organizer_label = st.selectbox("Organizator transportu", options=party_labels, index=0)
    organizer_idx = party_labels.index(organizer_label)

    col_from, col_to = st.columns(2)
    with col_from:
        default_from = get_default_country_option("PL")
        from_opt = st.selectbox(
            "Transport z (kraj)",
            options=COUNTRY_OPTIONS,
            index=COUNTRY_OPTIONS.index(default_from),
            key="from_country",
        )
        from_country = COUNTRY_CODE_MAP.get(from_opt, "PL")
    with col_to:
        default_to = get_default_country_option("DE")
        to_opt = st.selectbox(
            "Transport do (kraj)",
            options=COUNTRY_OPTIONS,
            index=COUNTRY_OPTIONS.index(default_to),
            key="to_country",
        )
        to_country = COUNTRY_CODE_MAP.get(to_opt, "DE")

    transport_type_str = st.selectbox("Rodzaj transportu", options=TRANSPORT_TYPES)
    incoterms = st.selectbox("Incoterms", options=INCOTERMS_LIST)

    st.markdown("---")
    st.markdown(
        '<div style="font-weight:700;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#f07830;margin-bottom:0.5rem">'
        '📋 Szczegóły'
        '</div>',
        unsafe_allow_html=True,
    )

    intermediary_vat = st.checkbox(
        "Pośrednik podał numer VAT UE kraju wysyłki",
        help="Art. 22 ust. 2c — wpływa na przypisanie dostawy ruchomej",
    )
    goods_leave_eu = st.checkbox("Towar opuszcza UE (eksport)")
    goods_enter_eu = st.checkbox("Towar wjeżdża do UE (import)")

    documents = st.multiselect(
        "Dostępne dokumenty",
        options=DOCUMENTS_LIST,
        default=["CMR", "faktura"],
    )

    st.markdown("---")
    st.markdown(
        '<div style="font-weight:700;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#f07830;margin-bottom:0.5rem">'
        '🤖 AI (opcjonalne)'
        '</div>',
        unsafe_allow_html=True,
    )

    use_ai = st.checkbox(
        "Wygeneruj komentarz ekspercki AI",
        help="AI opisuje wynik silnika regułowego — nie zmienia klasyfikacji VAT.",
    )
    if use_ai:
        st.markdown(
            '<div class="alert-warning" style="font-size:0.75rem">'
            '💰 Uwaga: generowanie komentarza AI może wiązać się z kosztem API OpenAI.'
            '</div>',
            unsafe_allow_html=True,
        )

# ── Build model objects ──────────────────────────────────────────────────────
parties: list[Party] = []
for cfg in party_configs:
    cc = cfg["country_code"]
    is_pl = cc == "PL"
    is_eu = is_eu_country(cc)
    try:
        vat_st = VatStatus(cfg["vat_status"])
    except ValueError:
        vat_st = VatStatus.ACTIVE_VAT

    parties.append(Party(
        name=cfg["name"],
        country_code=cc,
        country_name=get_country_name(cc),
        vat_status=vat_st,
        is_polish=is_pl,
        is_eu=is_eu,
        index=cfg["index"],
    ))

try:
    transport_type = TransportType(transport_type_str)
except ValueError:
    transport_type = TransportType.ROAD

input_data = TransactionInput(
    parties=parties,
    transport_organizer_index=organizer_idx,
    transport_from_country=from_country,
    transport_to_country=to_country,
    transport_type=transport_type,
    incoterms=incoterms,
    intermediary_provided_vat_of_origin=intermediary_vat,
    goods_leave_eu=goods_leave_eu,
    goods_enter_eu=goods_enter_eu,
    documents=documents,
    use_ai=use_ai,
)

# ── Polish party check ───────────────────────────────────────────────────────
has_polish = any(p.is_polish for p in parties)

# ── CTA button ───────────────────────────────────────────────────────────────
col_cta, col_empty = st.columns([3, 1])
with col_cta:
    st.markdown('<div class="cta-button">', unsafe_allow_html=True)
    analyze_clicked = st.button("⚡ Analizuj transakcję VAT", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── No Polish party guard ────────────────────────────────────────────────────
if analyze_clicked and not has_polish:
    st.markdown(
        '<div class="alert-danger" style="text-align:center;padding:2rem;font-size:1.1rem">'
        '🇵🇱 Aplikacja analizuje wyłącznie transakcje, w których uczestniczy podmiot polski.<br>'
        '<small>Dodaj podmiot z Polski (PL) w panelu po lewej stronie.</small>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── Main analysis ────────────────────────────────────────────────────────────
if analyze_clicked and has_polish:
    with st.spinner("Analizuję transakcję — silnik regułowy w toku..."):
        result = classify_vat_transaction(input_data)

    # Chain info banner
    chain_color = "#5b3fa6" if result.is_chain_transaction else "#22c55e"
    chain_label = f"✅ Transakcja łańcuchowa ({result.num_deliveries} dostawy)" if result.is_chain_transaction else "ℹ️ Nie jest transakcją łańcuchową"
    triangular_label = " | 🔺 Możliwa procedura trójstronna uproszczona" if result.triangular_simplified_possible else ""
    st.markdown(
        f'<div style="background:rgba{tuple(int(chain_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))};">'
        f'<div class="alert-info" style="font-size:1rem;font-weight:700">'
        f'{chain_label}{triangular_label}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Tabs for sections ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Podsumowanie",
        "📊 Klasyfikacja",
        "🇵🇱 Polski podmiot",
        "⏰ Obowiązek",
        "📁 JPK_V7",
        "⚠️ Ryzyka",
        "⚖️ Podstawy prawne",
    ])

    with tab1:
        render_summary(input_data)
        render_schema(input_data, result)

    with tab2:
        render_delivery_table(result)

    with tab3:
        render_polish_party_analysis(result)

    with tab4:
        render_tax_obligation(result)

    with tab5:
        render_jpk(result)

    with tab6:
        render_warnings(result)
        if not result.warnings and not result.requires_verification:
            st.markdown(
                '<div class="alert-success">✅ Silnik regułowy nie wykrył krytycznych ryzyk dla podanych danych.</div>',
                unsafe_allow_html=True,
            )

    with tab7:
        render_legal_basis(result)

    # ── AI Commentary ──
    st.markdown("---")
    ai_col1, ai_col2 = st.columns([1, 3])
    with ai_col1:
        st.markdown('<div class="cta-button">', unsafe_allow_html=True)
        generate_ai = st.button("🤖 Wygeneruj komentarz AI", use_container_width=True, disabled=not use_ai)
        st.markdown('</div>', unsafe_allow_html=True)
        if not use_ai:
            st.markdown(
                '<div style="font-size:0.75rem;color:#8895b3">Włącz opcję AI w panelu bocznym.</div>',
                unsafe_allow_html=True,
            )

    if generate_ai and use_ai:
        api_key_present = bool(
            os.environ.get("OPENAI_API_KEY") or
            (hasattr(st, "secrets") and st.secrets.get("OPENAI_API_KEY"))
        )
        if not api_key_present:
            st.markdown(
                '<div class="alert-danger">🔑 Brak klucza API — analiza AI jest niedostępna. '
                'Ustaw zmienną środowiskową <code>OPENAI_API_KEY</code> lub dodaj do <code>.streamlit/secrets.toml</code>.</div>',
                unsafe_allow_html=True,
            )
        else:
            with st.spinner("Generuję komentarz ekspercki AI..."):
                from ai.ai_service import generate_ai_commentary
                commentary, from_cache = generate_ai_commentary(input_data, result)
            render_ai_commentary(commentary, from_cache)

# ── Welcome screen (before analysis) ────────────────────────────────────────
elif not analyze_clicked:
    st.markdown(
        '<div class="vat-card" style="text-align:center;padding:3rem">'
        '<div style="font-size:4rem;margin-bottom:1rem">⛓</div>'
        '<h2 style="color:#c4b0f5">Gotowy do analizy</h2>'
        '<p style="color:#8895b3;max-width:500px;margin:0 auto">'
        'Skonfiguruj transakcję w panelu po lewej stronie, a następnie kliknij '
        '<strong style="color:#f07830">Analizuj transakcję VAT</strong>.'
        '<br><br>Aplikacja wymaga co najmniej jednego podmiotu polskiego.'
        '</p>'
        '<br>'
        '<div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap">'
        '<div style="text-align:center"><div style="font-size:2rem">⚖️</div><div style="font-size:0.8rem;color:#8895b3">Silnik regułowy<br>art. 7 ust. 8, art. 22 VAT</div></div>'
        '<div style="text-align:center"><div style="font-size:2rem">🏛</div><div style="font-size:0.8rem;color:#8895b3">Orzecznictwo TSUE<br>C-245/04 · C-430/09 · C-386/16</div></div>'
        '<div style="text-align:center"><div style="font-size:2rem">🤖</div><div style="font-size:0.8rem;color:#8895b3">AI opcjonalne<br>nie zmienia klasyfikacji</div></div>'
        '<div style="text-align:center"><div style="font-size:2rem">📁</div><div style="font-size:0.8rem;color:#8895b3">JPK_V7<br>TT_WNT · TT_D · GTU</div></div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Disclaimer ───────────────────────────────────────────────────────────────
render_disclaimer()
