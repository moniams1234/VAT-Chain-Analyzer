# app.py
"""
VAT Chain Analyzer — jasny, czytelny layout.
Formularz w głównej części strony (bez sidebaru).
Silnik regułowy: 100% deterministyczny. AI: opcjonalne uzasadnienie.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from ui.styles import CUSTOM_CSS
from ui.components import (
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
SORTED_COUNTRIES  = get_sorted_countries()
COUNTRY_OPTIONS   = [f"{code} — {name}" for code, name in SORTED_COUNTRIES]
COUNTRY_CODE_MAP  = {f"{code} — {name}": code for code, name in SORTED_COUNTRIES}
VAT_STATUSES      = [s.value for s in VatStatus]
TRANSPORT_TYPES   = [t.value for t in TransportType]
INCOTERMS_LIST    = ["EXW", "FCA", "CPT", "CIP", "DAP", "DPU", "DDP", "FAS", "FOB", "CFR", "CIF"]
DOCUMENTS_LIST    = ["CMR", "IE-599", "konosament", "airway bill", "faktura", "potwierdzenie odbioru"]
DEFAULT_COUNTRIES = ["PL", "DE", "FR", "IT", "US", "CN"]

def country_opt(code: str) -> str:
    return f"{code} — {get_country_name(code)}"

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="app-header">'
    '<div class="app-title">⛓ VAT Chain Analyzer</div>'
    '<div class="app-subtitle">'
    'Deterministyczna analiza VAT transakcji łańcuchowych i trójstronnych dla polskich podatników'
    '</div>'
    '<div style="margin-top:0.75rem">'
    '<span class="header-pill">art. 7 ust. 8 ustawy o VAT</span>'
    '<span class="header-pill">art. 22 ust. 2–2e VAT</span>'
    '<span class="header-pill">TSUE C-245/04 EMAG</span>'
    '<span class="header-pill">TSUE C-430/09 Euro Tyre</span>'
    '<span class="header-pill">TSUE C-386/16 Toridas</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ════════════════════════════════════════════════════════════════════════════
# SEKCJA 1 — LICZBA PODMIOTÓW
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="form-section-header">⚙️ Konfiguracja transakcji</div>', unsafe_allow_html=True)

num_parties = st.number_input(
    "Liczba podmiotów w łańcuchu",
    min_value=3, max_value=6, value=3, step=1,
    help="Minimalna liczba podmiotów to 3 (transakcja łańcuchowa). Maksimum 6.",
)
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SEKCJA 2 — DANE PODMIOTÓW
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="form-section-header">👥 Podmioty w łańcuchu</div>', unsafe_allow_html=True)

n = int(num_parties)
party_configs = []

# Grid: 3 → 3 cols, 4 → 2×2, 5–6 → 3 cols per row
if n == 3:
    grid_cols = 3
elif n == 4:
    grid_cols = 2
else:
    grid_cols = 3

# render parties in rows
for row_start in range(0, n, grid_cols):
    row_end = min(row_start + grid_cols, n)
    cols = st.columns(row_end - row_start)
    for col_pos, i in enumerate(range(row_start, row_end)):
        label = chr(65 + i)
        default_code = DEFAULT_COUNTRIES[i] if i < len(DEFAULT_COUNTRIES) else "PL"
        with cols[col_pos]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem">'
                f'<div style="width:32px;height:32px;border-radius:8px;background:#ede9ff;'
                f'color:#5b4fcf;font-weight:800;font-size:1rem;display:flex;'
                f'align-items:center;justify-content:center;">{label}</div>'
                f'<span style="font-weight:700;font-size:0.9rem;color:#1e3a5f">Podmiot {label}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            name = st.text_input(
                "Nazwa",
                value=f"Podmiot {label}",
                key=f"name_{i}",
                label_visibility="collapsed",
                placeholder=f"Nazwa podmiotu {label}",
            )
            default_opt = country_opt(default_code)
            country_sel = st.selectbox(
                f"Kraj {label}",
                options=COUNTRY_OPTIONS,
                index=COUNTRY_OPTIONS.index(default_opt) if default_opt in COUNTRY_OPTIONS else 0,
                key=f"country_{i}",
            )
            cc = COUNTRY_CODE_MAP.get(country_sel, "PL")
            vat_sel = st.selectbox(
                f"Status VAT {label}",
                options=VAT_STATUSES,
                index=1 if i > 0 else 0,
                key=f"vat_{i}",
            )
            party_configs.append({"name": name, "country_code": cc, "vat_status": vat_sel, "index": i})

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SEKCJA 3 — TRANSPORT I WARUNKI DOSTAWY
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="form-section-header">🚚 Transport i warunki dostawy</div>', unsafe_allow_html=True)

party_labels = [f"{chr(65+i)} — {party_configs[i]['name']}" for i in range(n)]

col_org, col_type, col_inc = st.columns(3)
with col_org:
    organizer_label = st.selectbox(
        "Organizator transportu",
        options=party_labels,
        index=0,
        help="Który podmiot organizuje fizyczny przewóz towaru (art. 22 ust. 2–2d ustawy o VAT)",
    )
    organizer_idx = party_labels.index(organizer_label)
with col_type:
    transport_type_str = st.selectbox("Rodzaj transportu", options=TRANSPORT_TYPES)
with col_inc:
    incoterms = st.selectbox("Incoterms", options=INCOTERMS_LIST)

col_from, col_to = st.columns(2)
with col_from:
    from_opt = st.selectbox(
        "Transport z kraju",
        options=COUNTRY_OPTIONS,
        index=COUNTRY_OPTIONS.index(country_opt("PL")),
        key="from_country",
    )
    from_country = COUNTRY_CODE_MAP.get(from_opt, "PL")
with col_to:
    to_opt = st.selectbox(
        "Transport do kraju",
        options=COUNTRY_OPTIONS,
        index=COUNTRY_OPTIONS.index(country_opt("DE")),
        key="to_country",
    )
    to_country = COUNTRY_CODE_MAP.get(to_opt, "DE")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    goods_leave_eu = st.checkbox("Towar opuszcza UE (eksport)", help="Towary wywożone poza terytorium UE")
with col_c2:
    goods_enter_eu = st.checkbox("Towar wjeżdża do UE (import)", help="Towary przywożone spoza UE")
with col_c3:
    intermediary_vat = st.checkbox(
        "Pośrednik podał VAT UE kraju wysyłki",
        help="Art. 22 ust. 2c — wpływa na przypisanie dostawy ruchomej",
    )

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SEKCJA 4 — DOKUMENTY
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="form-section-header">📄 Dostępne dokumenty</div>', unsafe_allow_html=True)

documents = st.multiselect(
    "Wybierz dokumenty posiadane w transakcji",
    options=DOCUMENTS_LIST,
    default=["CMR", "faktura"],
    help="Obecność dokumentów wpływa na prawo do stawki 0% (art. 42, art. 41 ust. 6 ustawy o VAT)",
)
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SEKCJA 5 — AI (opcjonalne)
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="form-section-header">🤖 Komentarz ekspercki AI <span style="font-weight:400;font-size:0.8rem;color:#94a3b8">(opcjonalne)</span></div>', unsafe_allow_html=True)

use_ai = st.checkbox(
    "Wygeneruj komentarz ekspercki AI po analizie",
    help="AI opisuje wynik silnika regułowego — nie zmienia klasyfikacji VAT.",
)
if use_ai:
    st.markdown(
        '<div class="alert-warning" style="margin-top:0.5rem">'
        '💡 <strong>Informacja:</strong> Generowanie komentarza AI może wiązać się z kosztem API OpenAI. '
        'Odpowiedzi są cache\'owane lokalnie (SHA256) — identyczny scenariusz nie generuje ponownego wywołania API.'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.85rem;margin:0.25rem 0 0">'
        'AI jest opcjonalne. Wynik silnika regułowego jest w pełni deterministyczny i nie wymaga AI.</p>',
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# BUDOWANIE MODELU DANYCH
# ════════════════════════════════════════════════════════════════════════════
parties: list[Party] = []
for cfg in party_configs:
    cc = cfg["country_code"]
    try:
        vat_st = VatStatus(cfg["vat_status"])
    except ValueError:
        vat_st = VatStatus.ACTIVE_VAT
    parties.append(Party(
        name=cfg["name"],
        country_code=cc,
        country_name=get_country_name(cc),
        vat_status=vat_st,
        is_polish=(cc == "PL"),
        is_eu=is_eu_country(cc),
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

has_polish = any(p.is_polish for p in parties)

# ════════════════════════════════════════════════════════════════════════════
# CTA BUTTON
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
col_btn, _ = st.columns([2, 1])
with col_btn:
    st.markdown('<div class="btn-cta">', unsafe_allow_html=True)
    analyze_clicked = st.button("⚡ Analizuj transakcję VAT", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Guard: brak polskiego podmiotu ──────────────────────────────────────────
if analyze_clicked and not has_polish:
    st.markdown(
        '<div class="alert-danger" style="text-align:center;padding:1.25rem;margin-top:1rem">'
        '🇵🇱 <strong>Aplikacja analizuje wyłącznie transakcje, w których uczestniczy podmiot polski.</strong><br>'
        '<span style="font-size:0.875rem">Zmień kraj jednego z podmiotów na Polska (PL).</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
# WYNIKI
# ════════════════════════════════════════════════════════════════════════════
if analyze_clicked and has_polish:
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    with st.spinner("Silnik regułowy w toku…"):
        result = classify_vat_transaction(input_data)

    # Banner
    chain_label = (
        f"✅ Transakcja łańcuchowa — {result.num_deliveries} dostawy"
        if result.is_chain_transaction
        else "ℹ️ Nie jest transakcją łańcuchową"
    )
    tri_label = "  |  🔺 Możliwa procedura trójstronna uproszczona (art. 135–138)" if result.triangular_simplified_possible else ""
    st.markdown(
        f'<div class="chain-banner">{chain_label}{tri_label}</div>',
        unsafe_allow_html=True,
    )

    # ── Taby wynikowe ──────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Podsumowanie",
        "📊 Klasyfikacja",
        "🇵🇱 Polski podmiot",
        "⏰ Obowiązek",
        "📁 JPK_V7",
        "⚠️ Ryzyka",
        "⚖️ Prawo",
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
                '<div class="alert-success">✅ Silnik regułowy nie wykrył krytycznych ryzyk dla podanych danych wejściowych.</div>',
                unsafe_allow_html=True,
            )

    with tab7:
        render_legal_basis(result)

    # ── AI Commentary ──────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)

    if use_ai:
        col_ai, _ = st.columns([2, 1])
        with col_ai:
            st.markdown('<div class="btn-cta">', unsafe_allow_html=True)
            generate_ai = st.button("🤖 Wygeneruj komentarz ekspercki AI", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if generate_ai:
            api_key_present = bool(
                os.environ.get("OPENAI_API_KEY") or
                (hasattr(st, "secrets") and st.secrets.get("OPENAI_API_KEY"))
            )
            if not api_key_present:
                st.markdown(
                    '<div class="alert-danger" style="margin-top:0.75rem">'
                    '🔑 <strong>Brak klucza API.</strong> Ustaw zmienną środowiskową '
                    '<code>OPENAI_API_KEY</code> lub dodaj do <code>.streamlit/secrets.toml</code>.'
                    '</div>',
                    unsafe_allow_html=True,
                )
            else:
                with st.spinner("Generuję komentarz ekspercki AI…"):
                    from ai.ai_service import generate_ai_commentary
                    commentary, from_cache = generate_ai_commentary(input_data, result)
                render_ai_commentary(commentary, from_cache)
    else:
        st.markdown(
            '<div class="alert-info">'
            '🤖 <strong>Komentarz AI jest wyłączony.</strong> Zaznacz opcję AI w formularzu powyżej, '
            'aby po analizie pojawił się przycisk generowania komentarza eksperckiego.'
            '</div>',
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════════════════════
# EKRAN STARTOWY
# ════════════════════════════════════════════════════════════════════════════
elif not analyze_clicked:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="welcome-card">'
        '<div style="font-size:3rem;margin-bottom:0.75rem">⛓</div>'
        '<h2>Gotowy do analizy</h2>'
        '<p style="max-width:480px;margin:0.5rem auto 1.5rem">Uzupełnij formularz powyżej — dane podmiotów, '
        'transport i dokumenty — a następnie kliknij <strong>Analizuj transakcję VAT</strong>.<br>'
        'Wymagany jest co najmniej jeden podmiot polski (PL).</p>'
        '<div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap">'
        '<div class="welcome-pill"><div class="wp-icon">⚖️</div>'
        '<div class="wp-label">Silnik regułowy<br>art. 7 ust. 8 VAT</div></div>'
        '<div class="welcome-pill"><div class="wp-icon">🏛</div>'
        '<div class="wp-label">TSUE<br>C-245/04 · C-430/09</div></div>'
        '<div class="welcome-pill"><div class="wp-icon">🔺</div>'
        '<div class="wp-label">Trójstronna<br>art. 135–138</div></div>'
        '<div class="welcome-pill"><div class="wp-icon">📁</div>'
        '<div class="wp-label">JPK_V7<br>TT_WNT · TT_D</div></div>'
        '<div class="welcome-pill"><div class="wp-icon">🤖</div>'
        '<div class="wp-label">AI opcjonalne<br>nie zmienia klas.</div></div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Disclaimer ───────────────────────────────────────────────────────────────
render_disclaimer()
