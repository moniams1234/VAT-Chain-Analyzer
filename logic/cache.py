# logic/cache.py
import hashlib
import json
import os
from pathlib import Path

CACHE_DIR = Path(".cache/ai")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_key(input_data_dict: dict, rule_result_dict: dict) -> str:
    payload = json.dumps(
        {"input": input_data_dict, "result": rule_result_dict},
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_cached_response(cache_key: str) -> str | None:
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("response")
        except Exception:
            return None
    return None


def save_cached_response(cache_key: str, response: str) -> None:
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"response": response}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
