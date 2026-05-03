# ai/ai_service.py
import os
from logic.cache import get_cache_key, load_cached_response, save_cached_response
from ai.prompts import SYSTEM_PROMPT, build_user_prompt


MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2500"))


def _get_api_key() -> str | None:
    """Pobiera klucz API wyłącznie ze Streamlit secrets albo zmiennej środowiskowej."""
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return str(key).strip()
    except Exception:
        pass

    key = os.getenv("OPENAI_API_KEY")
    return key.strip() if key else None


def _serialize_for_cache(input_data, rule_result) -> tuple[dict, dict]:
    """Serializuje dane do cache. Nie zapisuje klucza API ani danych technicznych."""
    input_dict = {
        "parties": [
            {
                "name": p.name,
                "country": p.country_code,
                "country_name": p.country_name,
                "vat_status": p.vat_status.value,
                "is_polish": p.is_polish,
                "is_eu": p.is_eu,
            }
            for p in input_data.parties
        ],
        "transport_organizer_index": input_data.transport_organizer_index,
        "transport_from": input_data.transport_from_country,
        "transport_to": input_data.transport_to_country,
        "transport_type": input_data.transport_type.value,
        "incoterms": input_data.incoterms,
        "goods_leave_eu": input_data.goods_leave_eu,
        "goods_enter_eu": input_data.goods_enter_eu,
        "documents": input_data.documents,
        "intermediary_vat_of_origin": input_data.intermediary_provided_vat_of_origin,
    }

    result_dict = {
        "is_chain": rule_result.is_chain_transaction,
        "num_deliveries": rule_result.num_deliveries,
        "movable_index": rule_result.movable_delivery_index,
        "triangular_possible": rule_result.triangular_simplified_possible,
        "deliveries": [
            {
                "index": d.delivery_index,
                "seller": d.seller.name,
                "buyer": d.buyer.name,
                "is_movable": d.is_movable,
                "type": d.delivery_type.value,
                "taxation_country": d.taxation_country,
                "taxation_country_name": d.taxation_country_name,
                "confidence": d.confidence.value,
                "notes": d.notes,
                "legal_basis": d.legal_basis_keys,
                "jpk_codes": d.jpk_codes,
            }
            for d in rule_result.deliveries
        ],
        "polish_party_analyses": [
            {
                "party": a.party.name,
                "role": a.role_description,
                "vat_output": a.vat_output,
                "vat_input": a.vat_input,
                "delivery_type": a.delivery_type.value,
                "may_need_foreign_registration": a.may_need_foreign_registration,
                "foreign_registration_country": a.foreign_registration_country,
                "jpk_v7_entries": a.jpk_v7_entries,
                "notes": a.notes,
            }
            for a in rule_result.polish_party_analyses
        ],
        "tax_obligation": (
            {
                "moment": rule_result.tax_obligation.moment_of_obligation,
                "legal_basis": rule_result.tax_obligation.legal_basis_key,
                "settlement_period": rule_result.tax_obligation.settlement_period,
                "zero_rate_conditions": rule_result.tax_obligation.zero_rate_conditions,
                "zero_rate_applicable": rule_result.tax_obligation.zero_rate_applicable,
            }
            if rule_result.tax_obligation
            else None
        ),
        "warnings": rule_result.warnings,
        "requires_verification": rule_result.requires_verification,
        "legal_basis": rule_result.applied_legal_basis,
        "jpk_summary": rule_result.jpk_summary,
    }

    return input_dict, result_dict


def generate_ai_commentary(input_data, rule_result) -> tuple[str, bool]:
    """
    Generuje komentarz ekspercki AI.
    Zwraca: (tekst, from_cache).

    AI nie klasyfikuje transakcji — opisuje wyłącznie wynik silnika regułowego.
    """
    api_key = _get_api_key()
    if not api_key:
        return (
            "Brak klucza API — analiza AI jest niedostępna. "
            "Wynik silnika regułowego pozostaje w mocy.",
            False,
        )

    input_dict, result_dict = _serialize_for_cache(input_data, rule_result)
    cache_key = get_cache_key(input_dict, result_dict)

    cached = load_cached_response(cache_key)
    if cached:
        return cached, True

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        user_prompt = build_user_prompt(input_dict, result_dict)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.2,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        commentary = response.choices[0].message.content or ""

        if not commentary.strip():
            return (
                "AI nie zwróciło treści komentarza. "
                "Wynik silnika regułowego pozostaje w mocy.",
                False,
            )

        save_cached_response(cache_key, commentary)
        return commentary, False

    except Exception as e:
        return (
            f"Błąd wywołania API AI: {type(e).__name__}: {str(e)}. "
            "Wynik silnika regułowego pozostaje w mocy.",
            False,
        )