# logic/jpk_classifier.py
"""
Klasyfikator JPK_V7 — przypisuje kody do transakcji na podstawie wyniku silnika regułowego.
"""
from logic.models import RuleEngineResult, DeliveryType


def get_jpk_v7_summary(result: RuleEngineResult, party_name: str) -> dict:
    """
    Zwraca słownik z podsumowaniem wpisów JPK_V7 dla wskazanego podmiotu.
    """
    entries = []
    tt_wnt = False
    tt_d = False

    for d in result.deliveries:
        is_seller = d.seller.name == party_name
        is_buyer = d.buyer.name == party_name

        if not (is_seller or is_buyer):
            continue

        if is_seller:
            if d.delivery_type == DeliveryType.WDT:
                entries.append({"pole": "K_21/K_22", "opis": "WDT — podstawa i VAT 0%"})
                if "TT_D" in d.jpk_codes:
                    entries.append({"pole": "TT_D", "opis": "Oznaczenie transakcji trójstronnej uproszczonej (dostawa)"})
                    tt_d = True
            elif d.delivery_type == DeliveryType.EXPORT:
                entries.append({"pole": "K_11/K_12", "opis": "Eksport towarów — podstawa i VAT 0%"})
            elif d.delivery_type == DeliveryType.DOMESTIC:
                entries.append({"pole": "K_17–K_20", "opis": "Dostawa krajowa — zależnie od stawki VAT"})
            elif d.delivery_type == DeliveryType.OUTSIDE_COUNTRY:
                entries.append({"pole": "K_11", "opis": "Dostawa poza terytorium kraju"})

        if is_buyer:
            if d.delivery_type in (DeliveryType.WDT,):
                # Nabywca w WDT → WNT
                entries.append({"pole": "K_23/K_24", "opis": "WNT — VAT należny"})
                entries.append({"pole": "K_25/K_26", "opis": "WNT — VAT naliczony (przy prawie do odliczenia)"})
                if "TT_WNT" in d.jpk_codes:
                    entries.append({"pole": "TT_WNT", "opis": "Oznaczenie WNT w transakcji trójstronnej uproszczonej"})
                    tt_wnt = True
            elif d.delivery_type == DeliveryType.IMPORT:
                entries.append({"pole": "K_25/K_26", "opis": "Import — VAT naliczony"})
            elif d.delivery_type == DeliveryType.DOMESTIC:
                entries.append({"pole": "K_39/K_40", "opis": "Zakup krajowy — VAT naliczony"})

    return {
        "entries": entries,
        "tt_wnt": tt_wnt,
        "tt_d": tt_d,
    }
