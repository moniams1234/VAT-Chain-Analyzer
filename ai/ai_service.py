# ai/ai_service.py
import os
import json
from logic.cache import get_cache_key, load_cached_response, save_cached_response
from ai.prompts import SYSTEM_PROMPT, build_user_prompt


def _get_api_key() -> str | None:
    """Pobiera klucz API wyłącznie ze secrets lub zmiennej środowiskowej. Nigdy z kodu."""
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY")


def _serialize_for_cache(input_data, rule_result) -> tuple[dict, dict]:
    """Serializuje dane do cache bez wrażliwych info."""
    input_dict = {
        "parties": [
            {
                "name": p.name,
                "country": p.country_code,
                "vat_status": p.vat_status.value,
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
                "confidence": d.confidence.value,
            }
            for d in rule_result.deliveries
        ],
        "warnings": rule_result.warnings,
        "requires_verification": rule_result.requires_verification,
        "legal_basis": rule_result.applied_legal_basis,
    }
    return input_dict, result_dict


def generate_ai_commentary(input_data, rule_result) -> tuple[str, bool]:
    """
    Generuje komentarz ekspercki AI.
    Zwraca (tekst, from_cache).
    AI nie może zmienić klasyfikacji silnika regułowego.
    """
    api_key = _get_api_key()
    if not api_key:
        return "Brak klucza API — analiza AI jest niedostępna. Wynik silnika regułowego pozostaje w mocy.", False

    input_dict, result_dict = _serialize_for_cache(input_data, rule_result)
    cache_key = get_cache_key(input_dict, result_dict)

    # Sprawdź cache
    cached = load_cached_response(cache_key)
    if cached:
        return cached, True

    # Wywołaj API
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        user_prompt = build_user_prompt(input_dict, result_dict)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=2500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )

        commentary = response.choices[0].message.content or ""
        save_cached_response(cache_key, commentary)
        return commentary, False

    except Exception as e:
        return f"Błąd wywołania API AI: {str(e)}. Wynik silnika regułowego pozostaje w mocy.", False
