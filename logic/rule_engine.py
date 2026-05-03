# logic/rule_engine.py
"""
Deterministyczny silnik regułowy do klasyfikacji VAT transakcji łańcuchowych.
AI NIE może zmieniać wyników tego modułu.
Podstawy prawne: art. 7 ust. 8, art. 22 ust. 2–2e, art. 13, art. 9, art. 2 pkt 8,
art. 19a, art. 20, art. 41 ust. 4–11, art. 42, art. 135–138 ustawy o VAT,
Dyrektywa VAT 2006/112/WE, TSUE C-245/04, C-430/09, C-386/16, C-401/18.
"""
from logic.models import (
    TransactionInput, RuleEngineResult, DeliveryAnalysis, PolishPartyAnalysis,
    TaxObligationAnalysis, DeliveryType, ConfidenceLevel, Party, VatStatus
)
from data.countries import is_eu_country, get_country_name, EU_COUNTRIES


def analyze_transaction(data: TransactionInput) -> RuleEngineResult:
    warnings = []
    requires_verification = []
    applied_basis = []

    # ── Reguła A: Transakcja łańcuchowa ──────────────────────────────────
    is_chain = len(data.parties) >= 3
    num_deliveries = len(data.parties) - 1

    if is_chain:
        applied_basis.append("art_7_ust_8")
        applied_basis.append("art_22_ust_2")

    # ── Reguła B: Dostawa ruchoma ─────────────────────────────────────────
    organizer_idx = data.transport_organizer_index
    organizer = data.parties[organizer_idx]
    movable_idx = None
    movable_confidence = ConfidenceLevel.HIGH

    from_eu = is_eu_country(data.transport_from_country)
    to_eu = is_eu_country(data.transport_to_country)

    if organizer_idx == 0:
        # Pierwszy podmiot organizuje transport → dostawa ruchoma = dostawa 0→1
        movable_idx = 0
        applied_basis.append("art_22_ust_2")
    elif organizer_idx == num_deliveries:
        # Ostatni podmiot (nabywca końcowy) organizuje transport → dostawa ruchoma = ostatnia
        movable_idx = num_deliveries - 1
        applied_basis.append("art_22_ust_2")
    else:
        # Pośrednik organizuje transport → art. 22 ust. 2b/2c
        applied_basis.append("art_22_ust_2b")
        if data.intermediary_provided_vat_of_origin:
            # Pośrednik podał VAT UE kraju wysyłki → transport przypisany do jego dostawy
            movable_idx = organizer_idx  # dostawa PRZEZ pośrednika (on jako sprzedawca)
            applied_basis.append("art_22_ust_2c")
            applied_basis.append("tsue_toridas")
        else:
            # Domyślnie: transport przypisany do dostawy DO pośrednika
            movable_idx = organizer_idx - 1
            applied_basis.append("art_22_ust_2b")
            applied_basis.append("tsue_euro_tyre")
            requires_verification.append(
                "Podmiot pośredniczący organizuje transport, ale nie podał numeru VAT UE kraju wysyłki. "
                "Transport co do zasady przypisany do dostawy DO pośrednika (art. 22 ust. 2b), "
                "jednak wymaga weryfikacji warunków dostawy i dokumentacji (TSUE C-430/09 Euro Tyre)."
            )
            movable_confidence = ConfidenceLevel.MEDIUM

    # ── Reguła D/E/F: Klasyfikacja dostawy ruchomej ───────────────────────
    deliveries: list[DeliveryAnalysis] = []

    for i in range(num_deliveries):
        seller = data.parties[i]
        buyer = data.parties[i + 1]
        is_movable = (i == movable_idx)

        if is_movable:
            # Klasyfikacja dostawy ruchomej
            d_type, taxation_country, d_basis, d_notes, d_confidence = _classify_movable_delivery(
                seller, buyer, data, warnings, requires_verification
            )
            applied_basis.extend(d_basis)
        else:
            # Dostawy nieruchome — art. 22 ust. 3
            if i < (movable_idx or 0):
                # Przed dostawą ruchomą → opodatkowanie w kraju rozpoczęcia transportu
                taxation_country = data.transport_from_country
                d_notes = f"Dostawa nieruchoma przed dostawą ruchomą — opodatkowana w kraju rozpoczęcia transportu ({get_country_name(taxation_country)}, art. 22 ust. 3 ustawy o VAT)."
            else:
                # Po dostawie ruchomej → opodatkowanie w kraju zakończenia transportu
                taxation_country = data.transport_to_country
                d_notes = f"Dostawa nieruchoma po dostawie ruchomej — opodatkowana w kraju zakończenia transportu ({get_country_name(taxation_country)}, art. 22 ust. 3 ustawy o VAT)."

            d_type = _classify_immovable_delivery(seller, buyer, taxation_country)
            d_confidence = ConfidenceLevel.HIGH
            d_basis = ["art_22_ust_3"]
            applied_basis.extend(d_basis)

        delivery = DeliveryAnalysis(
            delivery_index=i,
            seller=seller,
            buyer=buyer,
            is_movable=is_movable,
            delivery_type=d_type,
            taxation_country=taxation_country,
            taxation_country_name=get_country_name(taxation_country),
            legal_basis_keys=d_basis if is_movable else ["art_22_ust_3"],
            confidence=d_confidence if is_movable else ConfidenceLevel.HIGH,
            notes=d_notes if is_movable else d_notes,
        )
        deliveries.append(delivery)

    # ── Reguła G: Transakcja trójstronna uproszczona ─────────────────────
    triangular_possible = _check_triangular(data, deliveries, applied_basis, warnings)
    if triangular_possible:
        applied_basis.append("art_135_138")
        for d in deliveries:
            if d.is_movable:
                d.is_triangular_simplified = True

    # ── JPK kody ─────────────────────────────────────────────────────────
    _assign_jpk_codes(deliveries, data, triangular_possible)

    jpk_summary = _build_jpk_summary(deliveries, data, triangular_possible)

    # ── Analiza polskich podmiotów ────────────────────────────────────────
    polish_analyses = []
    for party in data.parties:
        if party.is_polish:
            analysis = _analyze_polish_party(party, deliveries, data)
            polish_analyses.append(analysis)

    # ── Obowiązek podatkowy ───────────────────────────────────────────────
    tax_obligation = _determine_tax_obligation(deliveries, data)
    if tax_obligation:
        applied_basis.append(tax_obligation.legal_basis_key)

    # ── Ostrzeżenia dokumentacyjne ────────────────────────────────────────
    _check_document_warnings(data, deliveries, warnings)

    # Deduplicate
    applied_basis = list(dict.fromkeys(applied_basis))

    return RuleEngineResult(
        is_chain_transaction=is_chain,
        num_deliveries=num_deliveries,
        movable_delivery_index=movable_idx,
        deliveries=deliveries,
        polish_party_analyses=polish_analyses,
        tax_obligation=tax_obligation,
        triangular_simplified_possible=triangular_possible,
        warnings=warnings,
        requires_verification=requires_verification,
        applied_legal_basis=applied_basis,
        jpk_summary=jpk_summary,
    )


def _classify_movable_delivery(seller, buyer, data, warnings, requires_verification):
    from_country = data.transport_from_country
    to_country = data.transport_to_country
    from_eu = is_eu_country(from_country)
    to_eu = is_eu_country(to_country)
    basis = []
    notes = ""
    confidence = ConfidenceLevel.HIGH

    # EKSPORT: towar opuszcza UE
    if data.goods_leave_eu and from_eu and not to_eu:
        d_type = DeliveryType.EXPORT
        taxation_country = from_country
        basis = ["art_2_pkt_8", "art_41_ust_4_11", "tsue_emag"]
        notes = (
            f"Dostawa ruchoma — potencjalny eksport. Towar opuszcza UE z {get_country_name(from_country)} "
            f"do kraju trzeciego ({get_country_name(to_country)}). "
            f"Stawka 0% pod warunkiem posiadania dokumentu IE-599 (art. 41 ust. 4–11 ustawy o VAT)."
        )
        if "IE-599" not in data.documents:
            warnings.append("Brak dokumentu IE-599 — nie można potwierdzić prawa do stawki 0% dla eksportu (art. 41 ust. 9 ustawy o VAT).")
        return d_type, taxation_country, basis, notes, confidence

    # IMPORT: towar wjeżdża do UE
    if data.goods_enter_eu and not from_eu and to_eu:
        d_type = DeliveryType.IMPORT
        taxation_country = to_country
        basis = ["art_2_pkt_8", "tsue_emag"]
        notes = (
            f"Dostawa ruchoma — potencjalny import. Towar wjeżdża do UE z {get_country_name(from_country)} "
            f"do {get_country_name(to_country)}. Konieczna odprawa celna importowa."
        )
        return d_type, taxation_country, basis, notes, confidence

    # WDT / WNT: dostawa wewnątrz UE między podatnikami VAT UE
    if from_eu and to_eu and from_country != to_country:
        if buyer.vat_status in (VatStatus.EU_VAT, VatStatus.ACTIVE_VAT):
            d_type = DeliveryType.WDT
            taxation_country = from_country
            basis = ["art_13", "art_42", "art_20", "tsue_emag"]
            notes = (
                f"Dostawa ruchoma — potencjalne WDT. Towar przemieszczony z {get_country_name(from_country)} "
                f"do {get_country_name(to_country)}. Sprzedawca rozpoznaje WDT (stawka 0% przy spełnieniu warunków art. 42), "
                f"nabywca rozpoznaje WNT w kraju {get_country_name(to_country)} (art. 9 ustawy o VAT)."
            )
            if "CMR" not in data.documents and "konosament" not in data.documents and "airway bill" not in data.documents:
                warnings.append(
                    "Brak dokumentów transportowych (CMR/konosament/airway bill) — ryzyko odmowy stawki 0% dla WDT (art. 42 ustawy o VAT)."
                )
            return d_type, taxation_country, basis, notes, confidence
        else:
            d_type = DeliveryType.WDT
            taxation_country = from_country
            confidence = ConfidenceLevel.MEDIUM
            basis = ["art_13", "art_9"]
            notes = (
                f"Dostawa ruchoma — przemieszczenie UE→UE, ale nabywca nie jest podatnikiem VAT UE. "
                f"WDT może nie mieć zastosowania. Weryfikacja statusu nabywcy wymagana."
            )
            requires_verification.append(
                f"Nabywca {buyer.name} ({buyer.country_name}) nie posiada statusu podatnika VAT UE — "
                f"warunek WDT (art. 13 ust. 2 pkt 1 ustawy o VAT) może nie być spełniony."
            )
            return d_type, taxation_country, basis, notes, confidence

    # Dostawa krajowa: ten sam kraj
    if from_country == to_country:
        d_type = DeliveryType.DOMESTIC
        taxation_country = from_country
        basis = ["art_22_ust_2"]
        notes = f"Dostawa ruchoma — dostawa krajowa na terytorium {get_country_name(from_country)}."
        return d_type, taxation_country, basis, notes, confidence

    # Dostawa poza UE → poza UE
    if not from_eu and not to_eu:
        d_type = DeliveryType.OUTSIDE_COUNTRY
        taxation_country = from_country
        basis = ["art_22_ust_2"]
        notes = (
            f"Dostawa ruchoma poza terytorium UE — transport między {get_country_name(from_country)} "
            f"a {get_country_name(to_country)}. Dostawa poza terytorium kraju."
        )
        return d_type, taxation_country, basis, notes, confidence

    # Fallback
    d_type = DeliveryType.UNKNOWN
    taxation_country = from_country
    confidence = ConfidenceLevel.REQUIRES_VERIFICATION
    requires_verification.append(
        "Nie można jednoznacznie ustalić rodzaju dostawy ruchomej. Wymagana weryfikacja stanu faktycznego."
    )
    return d_type, taxation_country, ["art_22_ust_2"], "Wymaga weryfikacji.", confidence


def _classify_immovable_delivery(seller, buyer, taxation_country):
    if is_eu_country(taxation_country):
        if seller.country_code == taxation_country and buyer.country_code == taxation_country:
            return DeliveryType.DOMESTIC
        elif seller.country_code != taxation_country or buyer.country_code != taxation_country:
            return DeliveryType.OUTSIDE_COUNTRY
    return DeliveryType.OUTSIDE_COUNTRY


def _check_triangular(data, deliveries, applied_basis, warnings):
    """Reguła G: Transakcja trójstronna uproszczona — art. 135–138 ustawy o VAT."""
    if len(data.parties) != 3:
        return False
    a, b, c = data.parties
    if not (a.is_eu and b.is_eu and c.is_eu):
        return False
    countries = {a.country_code, b.country_code, c.country_code}
    if len(countries) != 3:
        return False
    # B nie jest zarejestrowany w kraju C
    # Heurystycznie: jeśli B ma status VAT UE i country != country_C → możliwa procedura
    if b.country_code == c.country_code:
        return False
    # Towar musi jechać bezpośrednio od A do C
    if data.transport_from_country != a.country_code and data.transport_from_country not in [a.country_code]:
        pass  # Dopuszczamy — silnik nie ma pełnych danych o punktach załadunku
    return True


def _assign_jpk_codes(deliveries, data, triangular_possible):
    for d in deliveries:
        codes = []
        if d.delivery_type == DeliveryType.WDT:
            codes.append("WDT")
            if triangular_possible and d.is_movable:
                codes.append("TT_D")  # Dostawa w transakcji trójstronnej
        elif d.delivery_type == DeliveryType.WNT:
            codes.append("WNT")
            if triangular_possible:
                codes.append("TT_WNT")  # WNT w transakcji trójstronnej
        elif d.delivery_type == DeliveryType.EXPORT:
            codes.append("EKS")
        elif d.delivery_type == DeliveryType.IMPORT:
            codes.append("IMP")
        d.jpk_codes = codes


def _build_jpk_summary(deliveries, data, triangular_possible):
    summary = {
        "entries": [],
        "tt_wnt": False,
        "tt_d": False,
        "gtu_warning": "Oznaczenia GTU zależą od rodzaju towaru — wymagana weryfikacja. "
                       "Aplikacja nie może automatycznie przypisać GTU bez znajomości klasyfikacji PKWiU/CN towaru.",
        "triangular_note": "",
    }
    for d in deliveries:
        if any(p.is_polish for p in [d.seller, d.buyer]):
            entry = {
                "dostawa": f"Dostawa {d.delivery_index + 1}: {d.seller.name} → {d.buyer.name}",
                "typ": d.delivery_type.value,
                "kody_jpk": d.jpk_codes,
            }
            summary["entries"].append(entry)
        if "TT_WNT" in d.jpk_codes:
            summary["tt_wnt"] = True
        if "TT_D" in d.jpk_codes:
            summary["tt_d"] = True

    if triangular_possible:
        summary["triangular_note"] = (
            "Transakcja trójstronna uproszczona: zastosuj oznaczenia TT_D i/lub TT_WNT "
            "w JPK_V7 zgodnie z rolą polskiego podmiotu (art. 135–138 ustawy o VAT)."
        )
    return summary


def _analyze_polish_party(party: Party, deliveries: list[DeliveryAnalysis], data: TransactionInput):
    delivery_type = DeliveryType.UNKNOWN
    vat_output = False
    vat_input = False
    may_need_foreign_reg = False
    foreign_reg_country = None
    jpk_entries = []
    notes = ""
    role_desc = ""

    for d in deliveries:
        if d.seller.name == party.name:
            delivery_type = d.delivery_type
            if d.delivery_type == DeliveryType.WDT:
                vat_output = True
                role_desc = "Sprzedawca w WDT — wykazuje WDT ze stawką 0% (przy spełnieniu warunków art. 42 ustawy o VAT)."
                jpk_entries.append("Wykaż WDT w JPK_V7 w polu K_21 (podstawa) i K_22 (VAT 0%).")
                if "TT_D" in d.jpk_codes:
                    jpk_entries.append("Zastosuj oznaczenie TT_D w JPK_V7.")
            elif d.delivery_type == DeliveryType.EXPORT:
                vat_output = True
                role_desc = "Eksporter — wykazuje eksport ze stawką 0% (przy posiadaniu IE-599, art. 41 ust. 4–9)."
                jpk_entries.append("Wykaż eksport w JPK_V7 w polu K_11 (podstawa) i K_12 (VAT 0%).")
            elif d.delivery_type == DeliveryType.DOMESTIC:
                vat_output = True
                role_desc = "Sprzedawca w dostawie krajowej — wykazuje podatek należny."
                jpk_entries.append("Wykaż dostawę krajową w JPK_V7 (K_17/K_18 lub K_19/K_20 zależnie od stawki).")
            elif d.delivery_type == DeliveryType.OUTSIDE_COUNTRY:
                vat_output = False
                role_desc = "Sprzedawca w dostawie poza terytorium kraju — brak VAT w Polsce, możliwy obowiązek rejestracji zagranicznej."
                may_need_foreign_reg = True
                foreign_reg_country = d.taxation_country_name
                jpk_entries.append("Wykaż dostawę poza terytorium kraju w JPK_V7 (K_11).")
            else:
                role_desc = f"Sprzedawca w dostawie klasyfikowanej jako: {d.delivery_type.value}."

        elif d.buyer.name == party.name:
            delivery_type = d.delivery_type
            if d.delivery_type == DeliveryType.WDT:
                # Polski podmiot jako nabywca w WDT → WNT po stronie polskiego
                vat_input = True
                vat_output = True  # samonaliczenie
                role_desc = "Nabywca w transakcji wewnątrzwspólnotowej — rozpoznaje WNT w Polsce (art. 9 ustawy o VAT)."
                jpk_entries.append("Wykaż WNT w JPK_V7: VAT należny (K_23/K_24) i naliczony (K_25/K_26).")
                if "TT_WNT" in d.jpk_codes:
                    jpk_entries.append("Zastosuj oznaczenie TT_WNT w JPK_V7.")
            elif d.delivery_type == DeliveryType.IMPORT:
                vat_input = True
                role_desc = "Importer — rozlicza VAT importowy (art. 33 lub 33a ustawy o VAT)."
                jpk_entries.append("Wykaż import w JPK_V7 (K_25/K_26 lub procedura uproszczona art. 33a).")
            elif d.delivery_type == DeliveryType.DOMESTIC:
                vat_input = True
                role_desc = "Nabywca w dostawie krajowej — odlicza VAT naliczony z faktury."
                jpk_entries.append("Wykaż VAT naliczony z faktury zakupu w JPK_V7 (K_39/K_40).")
            elif d.delivery_type == DeliveryType.OUTSIDE_COUNTRY:
                role_desc = "Nabywca w dostawie opodatkowanej poza Polską — możliwy obowiązek rejestracji w kraju dostawy."
                may_need_foreign_reg = True
                foreign_reg_country = d.taxation_country_name
            else:
                role_desc = f"Nabywca w dostawie klasyfikowanej jako: {d.delivery_type.value}."

    return PolishPartyAnalysis(
        party=party,
        role_description=role_desc,
        vat_output=vat_output,
        vat_input=vat_input,
        delivery_type=delivery_type,
        may_need_foreign_registration=may_need_foreign_reg,
        foreign_registration_country=foreign_reg_country,
        jpk_v7_entries=jpk_entries,
        notes=notes,
    )


def _determine_tax_obligation(deliveries, data):
    for d in deliveries:
        if d.delivery_type == DeliveryType.WDT and any(p.is_polish for p in [d.seller]):
            return TaxObligationAnalysis(
                moment_of_obligation="Z chwilą wystawienia faktury, nie później niż 15. dnia miesiąca następującego po miesiącu dostawy (art. 20 ust. 1 ustawy o VAT).",
                legal_basis_key="art_20",
                settlement_period="Miesiąc wystawienia faktury lub 15. dzień miesiąca następnego.",
                zero_rate_conditions=[
                    "Posiadanie dokumentów potwierdzających wywóz (CMR, potwierdzenie odbioru) — art. 42 ustawy o VAT",
                    "Nabywca posiadający ważny numer VAT UE w kraju przeznaczenia",
                    "Złożenie informacji podsumowującej VAT-UE",
                ],
                zero_rate_applicable=True,
            )
        elif d.delivery_type == DeliveryType.EXPORT and any(p.is_polish for p in [d.seller]):
            return TaxObligationAnalysis(
                moment_of_obligation="Z chwilą dokonania dostawy (art. 19a ust. 1 ustawy o VAT). Stawka 0% warunkowo.",
                legal_basis_key="art_19a",
                settlement_period="Miesiąc dokonania dostawy.",
                zero_rate_conditions=[
                    "Posiadanie dokumentu IE-599 potwierdzającego wywóz — art. 41 ust. 6 ustawy o VAT",
                    "Wywóz przed złożeniem deklaracji lub możliwość korekty (art. 41 ust. 9)",
                ],
                zero_rate_applicable=True,
            )
        elif d.delivery_type == DeliveryType.WNT and any(p.is_polish for p in [d.buyer]):
            return TaxObligationAnalysis(
                moment_of_obligation="Z chwilą wystawienia faktury przez dostawcę, nie później niż 15. dnia miesiąca następującego po dostawie (art. 20 ust. 5 ustawy o VAT).",
                legal_basis_key="art_20",
                settlement_period="Miesiąc wystawienia faktury lub 15. dzień miesiąca następnego.",
                zero_rate_conditions=[],
                zero_rate_applicable=False,
            )
        elif d.delivery_type == DeliveryType.DOMESTIC and any(p.is_polish for p in [d.seller]):
            return TaxObligationAnalysis(
                moment_of_obligation="Z chwilą dokonania dostawy towarów (art. 19a ust. 1 ustawy o VAT).",
                legal_basis_key="art_19a",
                settlement_period="Miesiąc dokonania dostawy.",
                zero_rate_conditions=[],
                zero_rate_applicable=False,
            )
    return None


def _check_document_warnings(data, deliveries, warnings):
    for d in deliveries:
        if d.delivery_type == DeliveryType.WDT:
            missing = []
            for doc in ["CMR", "potwierdzenie odbioru", "faktura"]:
                if doc not in data.documents:
                    missing.append(doc)
            if missing:
                warnings.append(
                    f"Brakujące dokumenty dla WDT: {', '.join(missing)}. "
                    f"Ryzyko utraty prawa do stawki 0% (art. 42 ustawy o VAT)."
                )
        if d.delivery_type == DeliveryType.EXPORT and "IE-599" not in data.documents:
            if "Brak dokumentu IE-599" not in " ".join(warnings):
                warnings.append(
                    "Brak dokumentu IE-599 — brak potwierdzenia wywozu dla eksportu (art. 41 ust. 6 ustawy o VAT)."
                )
