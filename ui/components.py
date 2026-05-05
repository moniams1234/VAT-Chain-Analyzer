# ui/components.py  —  VAT Chain Analyzer  —  GOFIN-style rendering
import streamlit as st
import pandas as pd
from logic.models import RuleEngineResult, DeliveryType, ConfidenceLevel, TransactionInput
from data.legal_basis import LEGAL_BASIS
from data.countries import get_country_name, is_eu_country


# ── tiny helpers ─────────────────────────────────────────────────────────────

def _d_badge(d_type: DeliveryType) -> str:
    MAP = {
        DeliveryType.WDT:            ("badge-wdt",      "WDT"),
        DeliveryType.WNT:            ("badge-wnt",      "WNT"),
        DeliveryType.EXPORT:         ("badge-export",   "EKSPORT"),
        DeliveryType.IMPORT:         ("badge-import",   "IMPORT"),
        DeliveryType.DOMESTIC:       ("badge-domestic", "KRAJOWA"),
        DeliveryType.OUTSIDE_COUNTRY:("badge-outside",  "POZA KRAJEM"),
        DeliveryType.TRIANGULAR:     ("badge-wdt",      "TRÓJSTRONNA"),
        DeliveryType.UNKNOWN:        ("badge-unknown",  "WERYFIKACJA"),
    }
    cls, lbl = MAP.get(d_type, ("badge-unknown", d_type.value))
    return f'<span class="badge {cls}">{lbl}</span>'


def _conf(c: ConfidenceLevel) -> str:
    MAP = {
        ConfidenceLevel.HIGH:                 ("confidence-high",   "✓ wysoki"),
        ConfidenceLevel.MEDIUM:               ("confidence-medium", "~ średni"),
        ConfidenceLevel.LOW:                  ("confidence-low",    "! niski"),
        ConfidenceLevel.REQUIRES_VERIFICATION:("confidence-verify", "⚠ weryfikacja"),
    }
    cls, lbl = MAP.get(c, ("confidence-verify", c.value))
    return f'<span class="{cls}">{lbl}</span>'


# ════════════════════════════════════════════════════════════════════════════
# GOFIN-STYLE CHAIN DIAGRAM
# ════════════════════════════════════════════════════════════════════════════

def render_chain_diagram(input_data: TransactionInput, result: RuleEngineResult | None = None):
    """
    Główny schemat: A → B → C poziomo z podpisami dostaw,
    + truck-line transportu fizycznego od pierwszego do ostatniego.
    """
    n = len(input_data.parties)
    from_cc = input_data.transport_from_country
    to_cc   = input_data.transport_to_country

    # build HTML diagram
    nodes_html = ""
    for i, p in enumerate(input_data.parties):
        is_pl  = p.is_polish
        is_org = (i == input_data.transport_organizer_index)
        extra  = (" is-pl" if is_pl else "") + (" is-org" if is_org else "")
        flag_pl  = "🇵🇱 " if is_pl else ""
        flag_eu  = "🇪🇺 " if (p.is_eu and not is_pl) else ""
        org_tag  = " 🚚" if is_org else ""
        eu_badge = (
            '<span class="badge beu" style="font-size:.58rem">UE</span>'
            if p.is_eu else
            '<span class="badge bnoneu" style="font-size:.58rem">poza UE</span>'
        )
        nodes_html += f'''
<div class="chain-node{extra}">
  <div class="n-letter">{chr(65+i)}</div>
  <div class="n-name">{flag_pl}{flag_eu}{p.name}{org_tag}</div>
  <div class="n-country">{p.country_name} {eu_badge}</div>
  <div class="n-status">{p.vat_status.value}</div>
</div>'''

        if i < n - 1:
            is_mov = result and result.deliveries[i].is_movable
            mov_cls = " is-mov" if is_mov else ""
            d_type_lbl = ""
            if result:
                d = result.deliveries[i]
                d_type_lbl = f'<div style="font-size:.58rem;margin-top:2px">{_d_badge(d.delivery_type)}</div>'
            nodes_html += f'''
<div class="chain-arrow{mov_cls}">
  <div class="del-label">Dostawa {i+1}</div>
  <div class="arr-line">
    <div class="arr-dash"></div>
    <div class="arr-head">▶</div>
  </div>
  {d_type_lbl}
</div>'''

    from_name = get_country_name(from_cc)
    to_name   = get_country_name(to_cc)
    org_name  = input_data.parties[input_data.transport_organizer_index].name

    # transport physical bar
    transport_html = f'''
<div class="transport-bar">
  🚚 <strong>Transport fizyczny:</strong>
  <strong>{from_cc}</strong> ({from_name})
  &nbsp;→&nbsp;
  <strong>{to_cc}</strong> ({to_name})
  &nbsp;│&nbsp; organizator: <strong>{org_name}</strong>
  &nbsp;│&nbsp; <code>{input_data.incoterms}</code>
  &nbsp;│&nbsp; {input_data.transport_type.value}
</div>'''

    st.markdown(
        f'<div class="chain-diagram">'
        f'<div class="chain-row">{nodes_html}</div>'
        f'{transport_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# GOFIN-STYLE DELIVERY COMMENTS
# ════════════════════════════════════════════════════════════════════════════

def render_delivery_comments(result: RuleEngineResult):
    """
    Sekcja 'Komentarz do schematu' w stylu GOFIN:
    Dostawa 1 — opis, Dostawa 2 — opis, itd.
    """
    st.markdown('<div class="sec-title">📝 Komentarz do schematu</div>', unsafe_allow_html=True)

    for d in result.deliveries:
        is_mov = d.is_movable
        mov_cls = " is-mov" if is_mov else ""
        mov_tag = (
            '<span class="badge badge-movable" style="margin-left:6px">📦 RUCHOMA</span>'
            if is_mov else
            '<span class="badge badge-immovable" style="margin-left:6px">⬛ nieruchoma</span>'
        )
        lbl = chr(65 + d.delivery_index)
        lbl2 = chr(66 + d.delivery_index)

        # Legal basis short list
        lb_parts = [LEGAL_BASIS[k]["short"] for k in d.legal_basis_keys if k in LEGAL_BASIS]
        lb_str = " | ".join(lb_parts[:3]) if lb_parts else "—"

        # JPK codes
        jpk_str = " ".join(
            f'<span class="badge badge-wdt">{c}</span>'
            for c in d.jpk_codes
        ) if d.jpk_codes else "—"

        # Who resolves VAT in Poland
        pl_side = ""
        if d.seller.is_polish:
            pl_side = f"Polski podmiot <strong>{d.seller.name}</strong> → strona <strong>sprzedawcy</strong>"
        elif d.buyer.is_polish:
            pl_side = f"Polski podmiot <strong>{d.buyer.name}</strong> → strona <strong>nabywcy</strong>"

        st.markdown(f'''
<div class="del-comment{mov_cls}">
  <div class="dc-head">
    Dostawa {d.delivery_index+1}: {lbl} ({d.seller.name}) → {lbl2} ({d.buyer.name})
    {mov_tag}
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:.4rem .75rem;font-size:.83rem">
    <div><span style="color:#64748b;font-size:.7rem;font-weight:700;text-transform:uppercase">Rodzaj VAT</span><br>{_d_badge(d.delivery_type)} {d.delivery_type.value}</div>
    <div><span style="color:#64748b;font-size:.7rem;font-weight:700;text-transform:uppercase">Kraj opodatkowania</span><br><strong>{d.taxation_country}</strong> — {d.taxation_country_name}</div>
    <div style="grid-column:1/-1"><span style="color:#64748b;font-size:.7rem;font-weight:700;text-transform:uppercase">Opis</span><br>{d.notes}</div>
    {'<div><span style="color:#64748b;font-size:.7rem;font-weight:700;text-transform:uppercase">Polski podmiot</span><br>' + pl_side + '</div>' if pl_side else ''}
    <div><span style="color:#64748b;font-size:.7rem;font-weight:700;text-transform:uppercase">JPK_V7</span><br>{jpk_str}</div>
    <div><span style="color:#64748b;font-size:.7rem;font-weight:700;text-transform:uppercase">Pewność</span><br>{_conf(d.confidence)}</div>
    <div style="grid-column:1/-1"><span style="color:#64748b;font-size:.7rem;font-weight:700;text-transform:uppercase">Podstawa prawna</span><br><span style="font-size:.78rem;color:#475569">{lb_str}</span></div>
  </div>
</div>''', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 1: SUMMARY (compact)
# ════════════════════════════════════════════════════════════════════════════

def render_summary(input_data: TransactionInput):
    st.markdown('<div class="sec-title">📋 Podsumowanie</div>', unsafe_allow_html=True)
    cols = st.columns(3)

    with cols[0]:
        st.markdown('<div class="vat-card"><div class="vat-card-header">⛓ Podmioty</div>', unsafe_allow_html=True)
        for i, p in enumerate(input_data.parties):
            eu_b = '<span class="badge badge-eu">UE</span>' if p.is_eu else '<span class="badge badge-non-eu">poza UE</span>'
            pl_b = ' <span class="badge badge-pl">PL</span>' if p.is_polish else ''
            st.markdown(
                f"**{chr(65+i)} — {p.name}**{pl_b}<br>{eu_b} {p.country_name}<br>"
                f"<small style='color:#475569'>{p.vat_status.value}</small>",
                unsafe_allow_html=True,
            )
            if i < len(input_data.parties) - 1:
                st.markdown("<div style='color:#94a3b8;font-size:.8rem;margin:2px 0'>↓</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cols[1]:
        org = input_data.parties[input_data.transport_organizer_index]
        st.markdown(
            f'<div class="vat-card"><div class="vat-card-header">🚚 Transport</div>'
            f'<p><strong>Organizator:</strong> {org.name}</p>'
            f'<p><strong>Trasa:</strong> {input_data.transport_from_country} → {input_data.transport_to_country}</p>'
            f'<p><strong>Rodzaj:</strong> {input_data.transport_type.value}</p>'
            f'<p><strong>Incoterms:</strong> <code>{input_data.incoterms}</code></p>'
            f'<p><strong>Opuszcza UE:</strong> {"✅" if input_data.goods_leave_eu else "❌"}</p>'
            f'<p><strong>Wjeżdża do UE:</strong> {"✅" if input_data.goods_enter_eu else "❌"}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with cols[2]:
        docs_html = "".join(f'<div style="padding:1px 0">✅ {d}</div>' for d in input_data.documents) if input_data.documents else '<span class="badge badge-unknown">Brak</span>'
        vat_ok = "✅ Tak" if input_data.intermediary_provided_vat_of_origin else "❌ Nie"
        st.markdown(
            f'<div class="vat-card"><div class="vat-card-header">📄 Dokumenty</div>'
            f'{docs_html}'
            f'<p style="margin-top:.5rem"><strong>VAT UE kraju wysyłki:</strong> {vat_ok}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════
# SECTION 2: SCHEMA (result-time visual)
# ════════════════════════════════════════════════════════════════════════════

def render_schema(input_data: TransactionInput, result: RuleEngineResult):
    st.markdown('<div class="sec-title">🔗 Schemat transakcji</div>', unsafe_allow_html=True)
    render_chain_diagram(input_data, result)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 3: DELIVERY TABLE
# ════════════════════════════════════════════════════════════════════════════

def render_delivery_table(result: RuleEngineResult):
    st.markdown('<div class="sec-title">📊 Tabela klasyfikacji dostaw</div>', unsafe_allow_html=True)

    rows = []
    for d in result.deliveries:
        lb_short = ", ".join(LEGAL_BASIS[k]["short"] for k in d.legal_basis_keys if k in LEGAL_BASIS)
        rows.append({
            "Dostawa": f"{d.delivery_index+1}: {chr(65+d.delivery_index)}→{chr(66+d.delivery_index)}",
            "Sprzedawca": d.seller.name,
            "Nabywca":    d.buyer.name,
            "Ruchoma":    "📦 TAK" if d.is_movable else "⬛ NIE",
            "Rodzaj VAT": d.delivery_type.value,
            "Kraj opod.": f"{d.taxation_country} — {d.taxation_country_name}",
            "Pewność":    d.confidence.value,
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    for d in result.deliveries:
        with st.expander(f"📌 Dostawa {d.delivery_index+1}: {d.seller.name} → {d.buyer.name} | {d.delivery_type.value}"):
            st.markdown(f"**Opis:** {d.notes}")
            for k in d.legal_basis_keys:
                if k in LEGAL_BASIS:
                    lb = LEGAL_BASIS[k]
                    st.markdown(
                        f'<div class="alert-info"><strong>{lb["short"]}</strong><br>{lb["full"]}</div>',
                        unsafe_allow_html=True,
                    )


# ════════════════════════════════════════════════════════════════════════════
# SECTION 4: POLISH PARTY
# ════════════════════════════════════════════════════════════════════════════

def render_polish_party_analysis(result: RuleEngineResult):
    st.markdown('<div class="sec-title">🇵🇱 Analiza polskiego podmiotu</div>', unsafe_allow_html=True)

    if not result.polish_party_analyses:
        st.markdown('<div class="alert-danger">Brak polskich podmiotów.</div>', unsafe_allow_html=True)
        return

    for a in result.polish_party_analyses:
        st.markdown(f'<div class="vat-card"><div class="vat-card-header">🇵🇱 {a.party.name} — {a.party.vat_status.value}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Rola:** {a.role_description}")
            st.markdown(f"**VAT należny:** {'✅' if a.vat_output else '❌'} | **VAT naliczony:** {'✅' if a.vat_input else '❌'}", unsafe_allow_html=True)
        with c2:
            if a.may_need_foreign_registration:
                st.markdown(f'<div class="alert-warning">⚠️ Możliwy obowiązek rejestracji VAT zagranicą — {a.foreign_registration_country}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-success">✅ Brak zidentyfikowanego obowiązku rejestracji zagranicznej (wymaga weryfikacji)</div>', unsafe_allow_html=True)
        if a.jpk_v7_entries:
            for e in a.jpk_v7_entries:
                st.markdown(f'<div class="alert-info" style="margin:2px 0">📋 {e}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 5: TAX OBLIGATION
# ════════════════════════════════════════════════════════════════════════════

def render_tax_obligation(result: RuleEngineResult):
    st.markdown('<div class="sec-title">⏰ Obowiązek podatkowy</div>', unsafe_allow_html=True)
    if not result.tax_obligation:
        st.markdown('<div class="alert-info">Nie określono obowiązku podatkowego dla polskiego podmiotu.</div>', unsafe_allow_html=True)
        return
    to = result.tax_obligation
    lb = LEGAL_BASIS.get(to.legal_basis_key, {})
    st.markdown(
        f'<div class="vat-card"><div class="vat-card-header">⚡ Moment powstania</div>'
        f'<p><strong>{to.moment_of_obligation}</strong></p>'
        f'<p><strong>Okres rozliczeniowy:</strong> {to.settlement_period}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if lb:
        st.markdown(f'<div class="alert-info"><strong>{lb.get("short","")}</strong><br>{lb.get("full","")}</div>', unsafe_allow_html=True)
    if to.zero_rate_applicable and to.zero_rate_conditions:
        st.markdown("**Warunki stawki 0%:**")
        for c in to.zero_rate_conditions:
            st.markdown(f'<div class="alert-success" style="margin:2px 0">✅ {c}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 6: JPK_V7
# ════════════════════════════════════════════════════════════════════════════

def render_jpk(result: RuleEngineResult):
    st.markdown('<div class="sec-title">📁 JPK_V7</div>', unsafe_allow_html=True)
    s = result.jpk_summary
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f'<div class="vat-card"><div class="vat-card-header">Oznaczenia specjalne</div>'
            f'<p><strong>TT_WNT:</strong> {"✅ Stosować" if s.get("tt_wnt") else "❌ Nie dotyczy"}</p>'
            f'<p><strong>TT_D:</strong> {"✅ Stosować" if s.get("tt_d") else "❌ Nie dotyczy"}</p>'
            f'</div>', unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="vat-card"><div class="vat-card-header">⚠️ GTU</div>'
            f'<p style="font-size:.83rem">{s.get("gtu_warning","")}</p>'
            f'</div>', unsafe_allow_html=True,
        )
    for e in s.get("entries", []):
        codes = " ".join(f'<span class="badge badge-wdt">{c}</span>' for c in e.get("kody_jpk", []))
        st.markdown(
            f'<div class="alert-info" style="margin:3px 0"><strong>{e["dostawa"]}</strong> — {e["typ"]}'
            f'{"<br>" + codes if codes else ""}</div>', unsafe_allow_html=True,
        )
    if s.get("triangular_note"):
        st.markdown(f'<div class="alert-warning">📌 {s["triangular_note"]}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 7: WARNINGS
# ════════════════════════════════════════════════════════════════════════════

def render_warnings(result: RuleEngineResult):
    if not result.warnings and not result.requires_verification:
        return
    st.markdown('<div class="sec-title">⚠️ Ryzyka i ostrzeżenia</div>', unsafe_allow_html=True)
    for w in result.warnings:
        st.markdown(f'<div class="alert-warning">⚠️ {w}</div>', unsafe_allow_html=True)
    for v in result.requires_verification:
        st.markdown(f'<div class="alert-danger">🔍 {v}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SECTION 8: LEGAL BASIS
# ════════════════════════════════════════════════════════════════════════════

def render_legal_basis(result: RuleEngineResult):
    if not result.applied_legal_basis:
        return
    st.markdown('<div class="sec-title">⚖️ Podstawy prawne</div>', unsafe_allow_html=True)
    for k in result.applied_legal_basis:
        if k in LEGAL_BASIS:
            lb = LEGAL_BASIS[k]
            with st.expander(f"📜 {lb['short']}"):
                st.markdown(f"**Kontekst:** {lb['context']}")
                st.markdown(lb['full'])


# ════════════════════════════════════════════════════════════════════════════
# AI COMMENTARY
# ════════════════════════════════════════════════════════════════════════════

def render_ai_commentary(commentary: str, from_cache: bool):
    st.markdown('<div class="sec-title">🤖 Komentarz ekspercki AI</div>', unsafe_allow_html=True)
    src = '<span class="badge badge-domestic">📦 Z cache</span>' if from_cache else '<span class="badge badge-export">🌐 API</span>'
    st.markdown(
        f'<div class="vat-card-header">Analiza AI &nbsp; {src}</div>'
        f'<div class="alert-warning" style="margin-bottom:.75rem">⚠️ <strong>Ważne:</strong> Komentarz AI jest wyłącznie opisowy. Nie zmienia klasyfikacji silnika regułowego.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="vat-card">{commentary}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# DISCLAIMER
# ════════════════════════════════════════════════════════════════════════════

def render_disclaimer():
    st.markdown(
        '<div class="disclaimer">⚖️ <strong>Zastrzeżenie prawne:</strong> Aplikacja ma charakter pomocniczy i edukacyjny. '
        'Nie stanowi porady podatkowej. Wynik wymaga weryfikacji na podstawie dokumentów transakcyjnych, '
        'aktualnych przepisów, interpretacji podatkowych i orzecznictwa. '
        'Skonsultuj się z doradcą podatkowym przed podjęciem decyzji.</div>',
        unsafe_allow_html=True,
    )
