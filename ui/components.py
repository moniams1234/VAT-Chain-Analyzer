# ui/components.py
import streamlit as st
import pandas as pd
from logic.models import RuleEngineResult, DeliveryType, ConfidenceLevel, TransactionInput
from data.legal_basis import LEGAL_BASIS


# ── Helpers ─────────────────────────────────────────────────────────────────

def _delivery_badge(d_type: DeliveryType) -> str:
    map_ = {
        DeliveryType.WDT:           ("badge-wdt",      "WDT"),
        DeliveryType.WNT:           ("badge-wnt",      "WNT"),
        DeliveryType.EXPORT:        ("badge-export",   "EKSPORT"),
        DeliveryType.IMPORT:        ("badge-import",   "IMPORT"),
        DeliveryType.DOMESTIC:      ("badge-domestic", "KRAJOWA"),
        DeliveryType.OUTSIDE_COUNTRY:("badge-outside", "POZA KRAJEM"),
        DeliveryType.TRIANGULAR:    ("badge-wdt",      "TRÓJSTRONNA"),
        DeliveryType.UNKNOWN:       ("badge-unknown",  "WERYFIKACJA"),
    }
    cls, label = map_.get(d_type, ("badge-unknown", d_type.value))
    return f'<span class="badge {cls}">{label}</span>'


def _confidence_html(conf: ConfidenceLevel) -> str:
    map_ = {
        ConfidenceLevel.HIGH:                 ("confidence-high",   "✓ Wysoki"),
        ConfidenceLevel.MEDIUM:               ("confidence-medium", "~ Średni"),
        ConfidenceLevel.LOW:                  ("confidence-low",    "! Niski"),
        ConfidenceLevel.REQUIRES_VERIFICATION:("confidence-verify", "⚠ Weryfikacja"),
    }
    cls, label = map_.get(conf, ("confidence-verify", conf.value))
    return f'<span class="{cls}">{label}</span>'


# ── Section 1: Summary ───────────────────────────────────────────────────────

def render_summary(input_data: TransactionInput):
    st.markdown('<div class="section-title">📋 Podsumowanie transakcji</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown('<div class="vat-card">', unsafe_allow_html=True)
        st.markdown('<div class="vat-card-header">⛓ Podmioty</div>', unsafe_allow_html=True)
        for i, p in enumerate(input_data.parties):
            eu_badge = (
                '<span class="badge badge-eu">UE</span>'
                if p.is_eu
                else '<span class="badge badge-non-eu">poza UE</span>'
            )
            pl_badge = ' <span class="badge badge-pl">PL</span>' if p.is_polish else ''
            st.markdown(
                f"**{chr(65+i)} — {p.name}**{pl_badge}<br>"
                f"{eu_badge} {p.country_name}<br>"
                f"<small style='color:#475569'>{p.vat_status.value}</small>",
                unsafe_allow_html=True,
            )
            if i < len(input_data.parties) - 1:
                st.markdown("<div style='color:#94a3b8;text-align:center;margin:2px 0'>↓</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cols[1]:
        st.markdown('<div class="vat-card">', unsafe_allow_html=True)
        st.markdown('<div class="vat-card-header">🚚 Transport</div>', unsafe_allow_html=True)
        organizer = input_data.parties[input_data.transport_organizer_index]
        st.markdown(
            f"**Organizator:** {organizer.name}<br>"
            f"**Trasa:** {input_data.transport_from_country} → {input_data.transport_to_country}<br>"
            f"**Rodzaj:** {input_data.transport_type.value}<br>"
            f"**Incoterms:** `{input_data.incoterms}`<br>"
            f"**Towar opuszcza UE:** {'✅ Tak' if input_data.goods_leave_eu else '❌ Nie'}<br>"
            f"**Towar wjeżdża do UE:** {'✅ Tak' if input_data.goods_enter_eu else '❌ Nie'}",
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with cols[2]:
        st.markdown('<div class="vat-card">', unsafe_allow_html=True)
        st.markdown('<div class="vat-card-header">📄 Dokumenty</div>', unsafe_allow_html=True)
        if input_data.documents:
            for doc in input_data.documents:
                st.markdown(
                    f'<div style="padding:2px 0;color:#0f172a">✅ {doc}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<span class="badge badge-unknown">Brak dokumentów</span>', unsafe_allow_html=True)
        vat_label = (
            '✅ Tak'
            if input_data.intermediary_provided_vat_of_origin
            else '❌ Nie'
        )
        st.markdown(
            f"<br>**VAT UE kraju wysyłki podany:** {vat_label}",
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)


# ── Section 2: Transaction schema ───────────────────────────────────────────

def render_schema(input_data: TransactionInput, result: RuleEngineResult):
    st.markdown('<div class="section-title">🔗 Schemat transakcji</div>', unsafe_allow_html=True)

    n = len(input_data.parties)
    cols = st.columns(n * 2 - 1)

    for i, party in enumerate(input_data.parties):
        col_idx = i * 2
        with cols[col_idx]:
            is_organizer = (i == input_data.transport_organizer_index)
            extra_cls = ""
            if party.is_polish:
                extra_cls += " polish"
            if is_organizer:
                extra_cls += " organizer"

            label   = chr(65 + i)
            org_tag = " 🚚" if is_organizer else ""
            pl_tag  = " 🇵🇱" if party.is_polish else ""
            eu_tag  = " 🇪🇺" if (party.is_eu and not party.is_polish) else ""

            st.markdown(
                f'<div class="party-node{extra_cls}">'
                f'<div style="font-size:1.4rem;font-weight:800;color:#5b4fcf">{label}</div>'
                f'<div style="font-weight:700;font-size:0.85rem;color:#0f172a">{party.name}{pl_tag}{eu_tag}{org_tag}</div>'
                f'<div style="font-size:0.72rem;color:#475569;margin-top:3px">{party.country_name}</div>'
                f'<div style="font-size:0.68rem;color:#94a3b8;margin-top:2px">{party.vat_status.value}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if i < n - 1:
            with cols[col_idx + 1]:
                d = result.deliveries[i]
                is_mov = d.is_movable
                arrow_color = "#c2410c" if is_mov else "#94a3b8"
                mov_label   = "📦 RUCHOMA" if is_mov else "⬛ NIERUCHOMA"
                st.markdown(
                    f'<div style="display:flex;flex-direction:column;align-items:center;'
                    f'justify-content:center;height:100%;padding:0.4rem 0">'
                    f'<div style="font-size:0.6rem;font-weight:700;color:{arrow_color};margin-bottom:2px">{mov_label}</div>'
                    f'<div style="font-size:1.4rem;color:{arrow_color}">→</div>'
                    f'<div style="margin-top:2px">{_delivery_badge(d.delivery_type)}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    from data.countries import get_country_name
    organizer_name = input_data.parties[input_data.transport_organizer_index].name
    st.markdown(
        f'<div class="transport-flow">'
        f'🚚 Transport fizyczny: <strong>{input_data.transport_from_country}</strong>'
        f' → <strong>{input_data.transport_to_country}</strong>'
        f'&nbsp;|&nbsp; Organizator: <strong>{organizer_name}</strong>'
        f'&nbsp;|&nbsp; {input_data.transport_type.value.upper()}'
        f'&nbsp;|&nbsp; <code style="color:#c2410c">{input_data.incoterms}</code>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Section 3: Delivery classification ──────────────────────────────────────

def render_delivery_table(result: RuleEngineResult):
    st.markdown('<div class="section-title">📊 Klasyfikacja dostaw</div>', unsafe_allow_html=True)

    rows = []
    for d in result.deliveries:
        basis_short = ", ".join(
            LEGAL_BASIS[k]["short"] for k in d.legal_basis_keys if k in LEGAL_BASIS
        )
        rows.append({
            "Dostawa": f"{d.delivery_index+1}: {chr(65+d.delivery_index)}→{chr(66+d.delivery_index)}",
            "Sprzedawca": d.seller.name,
            "Nabywca":    d.buyer.name,
            "Ruchoma":    "📦 TAK" if d.is_movable else "⬛ NIE",
            "Rodzaj VAT": d.delivery_type.value,
            "Kraj opod.": f"{d.taxation_country} — {d.taxation_country_name}",
            "Pewność":    d.confidence.value,
            "Uwagi":      (d.notes[:100] + "…") if len(d.notes) > 100 else d.notes,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    for d in result.deliveries:
        with st.expander(
            f"📌 Dostawa {d.delivery_index+1}: {d.seller.name} → {d.buyer.name} "
            f"| {d.delivery_type.value} | {d.taxation_country_name}"
        ):
            st.markdown(f"**Uwagi:** {d.notes}")
            if d.legal_basis_keys:
                st.markdown("**Podstawy prawne:**")
                for k in d.legal_basis_keys:
                    if k in LEGAL_BASIS:
                        lb = LEGAL_BASIS[k]
                        st.markdown(
                            f'<div class="alert-info"><strong>{lb["short"]}</strong><br>{lb["full"]}</div>',
                            unsafe_allow_html=True,
                        )


# ── Section 4: Polish party analysis ────────────────────────────────────────

def render_polish_party_analysis(result: RuleEngineResult):
    st.markdown('<div class="section-title">🇵🇱 Analiza polskiego podmiotu</div>', unsafe_allow_html=True)

    if not result.polish_party_analyses:
        st.markdown(
            '<div class="alert-danger">Brak polskich podmiotów w transakcji.</div>',
            unsafe_allow_html=True,
        )
        return

    for analysis in result.polish_party_analyses:
        st.markdown('<div class="vat-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="vat-card-header">🇵🇱 {analysis.party.name} — {analysis.party.vat_status.value}</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"**Rola:** {analysis.role_description}")
            st.markdown(
                f"**VAT należny:** {'✅ Tak' if analysis.vat_output else '❌ Nie'}<br>"
                f"**VAT naliczony:** {'✅ Tak' if analysis.vat_input else '❌ Nie'}",
                unsafe_allow_html=True,
            )
        with cols[1]:
            if analysis.may_need_foreign_registration:
                st.markdown(
                    f'<div class="alert-warning">⚠️ Możliwy obowiązek rejestracji VAT za granicą — '
                    f'{analysis.foreign_registration_country}. Wymagana weryfikacja z doradcą podatkowym.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="alert-success">✅ Brak zidentyfikowanego obowiązku rejestracji zagranicznej '
                    '(wymaga weryfikacji).</div>',
                    unsafe_allow_html=True,
                )

        if analysis.jpk_v7_entries:
            st.markdown("**Wskazówki JPK_V7:**")
            for entry in analysis.jpk_v7_entries:
                st.markdown(
                    f'<div class="alert-info" style="margin:2px 0">📋 {entry}</div>',
                    unsafe_allow_html=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)


# ── Section 5: Tax obligation ────────────────────────────────────────────────

def render_tax_obligation(result: RuleEngineResult):
    st.markdown('<div class="section-title">⏰ Obowiązek podatkowy</div>', unsafe_allow_html=True)

    if not result.tax_obligation:
        st.markdown(
            '<div class="alert-info">Nie określono obowiązku podatkowego dla polskiego podmiotu — '
            'brak dostawy klasyfikowanej w Polsce.</div>',
            unsafe_allow_html=True,
        )
        return

    to = result.tax_obligation
    lb = LEGAL_BASIS.get(to.legal_basis_key, {})

    st.markdown('<div class="vat-card">', unsafe_allow_html=True)
    st.markdown('<div class="vat-card-header">⚡ Moment powstania obowiązku podatkowego</div>', unsafe_allow_html=True)
    st.markdown(f"**{to.moment_of_obligation}**")
    st.markdown(f"**Okres rozliczeniowy:** {to.settlement_period}")
    st.markdown('</div>', unsafe_allow_html=True)

    if lb:
        st.markdown(
            f'<div class="alert-info"><strong>{lb.get("short", "")}</strong><br>{lb.get("full", "")}</div>',
            unsafe_allow_html=True,
        )

    if to.zero_rate_applicable and to.zero_rate_conditions:
        st.markdown("**Warunki zastosowania stawki 0%:**")
        for cond in to.zero_rate_conditions:
            st.markdown(
                f'<div class="alert-success" style="margin:3px 0">✅ {cond}</div>',
                unsafe_allow_html=True,
            )


# ── Section 6: JPK_V7 ────────────────────────────────────────────────────────

def render_jpk(result: RuleEngineResult):
    st.markdown('<div class="section-title">📁 JPK_V7</div>', unsafe_allow_html=True)

    summary = result.jpk_summary
    col1, col2 = st.columns(2)
    with col1:
        tt_wnt = summary.get("tt_wnt", False)
        tt_d   = summary.get("tt_d", False)
        st.markdown(
            f'<div class="vat-card">'
            f'<div class="vat-card-header">Oznaczenia specjalne</div>'
            f'<p><strong>TT_WNT:</strong> {"✅ Stosować" if tt_wnt else "❌ Nie dotyczy"}</p>'
            f'<p><strong>TT_D:</strong> {"✅ Stosować" if tt_d else "❌ Nie dotyczy"}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="vat-card">'
            f'<div class="vat-card-header">⚠️ GTU</div>'
            f'<p style="font-size:0.875rem">{summary.get("gtu_warning", "")}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if summary.get("entries"):
        st.markdown("**Wpisy JPK_V7 dla polskiego podmiotu:**")
        for entry in summary["entries"]:
            codes = " ".join(f'<span class="badge badge-wdt">{c}</span>' for c in entry.get("kody_jpk", []))
            st.markdown(
                f'<div class="alert-info" style="margin:3px 0">'
                f'<strong>{entry["dostawa"]}</strong> — {entry["typ"]}'
                f'{"<br>" + codes if codes else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )

    if summary.get("triangular_note"):
        st.markdown(
            f'<div class="alert-warning" style="margin-top:0.5rem">📌 {summary["triangular_note"]}</div>',
            unsafe_allow_html=True,
        )


# ── Warnings & risks ─────────────────────────────────────────────────────────

def render_warnings(result: RuleEngineResult):
    all_issues = result.warnings + result.requires_verification
    if not all_issues:
        return

    st.markdown('<div class="section-title">⚠️ Ryzyka i ostrzeżenia</div>', unsafe_allow_html=True)
    for w in result.warnings:
        st.markdown(f'<div class="alert-warning">⚠️ {w}</div>', unsafe_allow_html=True)
    for v in result.requires_verification:
        st.markdown(f'<div class="alert-danger">🔍 {v}</div>', unsafe_allow_html=True)


# ── Legal basis accordion ────────────────────────────────────────────────────

def render_legal_basis(result: RuleEngineResult):
    if not result.applied_legal_basis:
        return
    st.markdown('<div class="section-title">⚖️ Zastosowane podstawy prawne</div>', unsafe_allow_html=True)
    for key in result.applied_legal_basis:
        if key in LEGAL_BASIS:
            lb = LEGAL_BASIS[key]
            with st.expander(f"📜 {lb['short']}"):
                st.markdown(f"**Kontekst:** {lb['context']}")
                st.markdown(lb['full'])


# ── AI commentary ─────────────────────────────────────────────────────────────

def render_ai_commentary(commentary: str, from_cache: bool):
    st.markdown('<div class="section-title">🤖 Komentarz ekspercki AI</div>', unsafe_allow_html=True)

    source_badge = (
        '<span class="badge badge-domestic">📦 Z cache</span>'
        if from_cache
        else '<span class="badge badge-export">🌐 API</span>'
    )
    st.markdown(
        f'<div class="vat-card-header" style="margin-bottom:0.5rem">'
        f'Analiza AI &nbsp; {source_badge}'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="alert-warning" style="margin-bottom:1rem">'
        '⚠️ <strong>Ważne:</strong> Poniższy komentarz AI ma charakter wyłącznie opisowy. '
        'Nie zmienia klasyfikacji dokonanej przez silnik regułowy. '
        'Klasyfikacja VAT jest wynikiem deterministycznym.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="vat-card">{commentary}</div>',
        unsafe_allow_html=True,
    )


# ── Disclaimer ───────────────────────────────────────────────────────────────

def render_disclaimer():
    st.markdown(
        '<div class="disclaimer">'
        '⚖️ <strong>Zastrzeżenie prawne:</strong> Aplikacja ma charakter pomocniczy i edukacyjny. '
        'Nie stanowi porady podatkowej. Wynik wymaga weryfikacji na podstawie dokumentów transakcyjnych, '
        'aktualnych przepisów, interpretacji podatkowych i orzecznictwa. '
        'Skonsultuj się z doradcą podatkowym przed podjęciem decyzji.'
        '</div>',
        unsafe_allow_html=True,
    )
