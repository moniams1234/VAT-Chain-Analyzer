# logic/vat_classifier.py
from logic.models import TransactionInput, RuleEngineResult
from logic.rule_engine import analyze_transaction


def classify_vat_transaction(input_data: TransactionInput) -> RuleEngineResult:
    """
    Główna funkcja klasyfikacji VAT.
    Wywołuje deterministyczny silnik regułowy.
    AI NIE może modyfikować wyników tej funkcji.
    """
    return analyze_transaction(input_data)
