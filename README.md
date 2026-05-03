# ⛓ VAT Chain Analyzer

Deterministyczna aplikacja Streamlit do analizy VAT transakcji łańcuchowych i trójstronnych.

## Zasada architektoniczna

**90% pracy wykonuje deterministyczny silnik regułowy.**  
AI jest opcjonalne i służy wyłącznie do opisowego uzasadnienia wyniku — **nie zmienia klasyfikacji VAT**.

```
Silnik regułowy (logic/rule_engine.py)
  ├── Transakcja łańcuchowa        art. 7 ust. 8 ustawy o VAT
  ├── Dostawa ruchoma              art. 22 ust. 2–2e ustawy o VAT
  ├── Dostawy nieruchome           art. 22 ust. 3 ustawy o VAT
  ├── WDT / WNT                   art. 13, art. 9 ustawy o VAT
  ├── Eksport / Import             art. 2 pkt 8 ustawy o VAT
  ├── Transakcja trójstronna       art. 135–138 ustawy o VAT
  └── JPK_V7                      TT_WNT, TT_D, GTU
```

## Struktura projektu

```
vat-chain-app/
├── app.py                  # Główny plik Streamlit
├── requirements.txt
├── data/
│   ├── countries.py        # Wykaz krajów GUS (kody ISO) + lista krajów UE
│   └── legal_basis.py      # Podstawy prawne z pełnymi tekstami
├── logic/
│   ├── models.py           # Modele danych (dataclasses)
│   ├── rule_engine.py      # Silnik regułowy — 90% logiki
│   ├── vat_classifier.py   # Wrapper silnika
│   ├── jpk_classifier.py   # Kody JPK_V7
│   └── cache.py            # Cache AI (SHA256)
├── ai/
│   ├── ai_service.py       # Serwis AI z kontrolą kosztów
│   └── prompts.py          # Kontrolowane prompty
└── ui/
    ├── components.py       # Komponenty UI (6 sekcji wynikowych)
    └── styles.py           # CSS — granat/fiolet/pomarańcz
```

## Instalacja i uruchomienie

```bash
# Klonuj lub wypakuj projekt
cd vat-chain-app

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom aplikację
streamlit run app.py
```

## Konfiguracja AI (opcjonalna)

Klucz API OpenAI pobierany jest **wyłącznie** z:

```bash
# Opcja 1: zmienna środowiskowa
export OPENAI_API_KEY="sk-..."
streamlit run app.py

# Opcja 2: Streamlit secrets
# Utwórz plik .streamlit/secrets.toml:
# OPENAI_API_KEY = "sk-..."
```

**Nigdy nie wpisuj klucza bezpośrednio w kod.**

## Podstawy prawne — silnik regułowy

| Przepis | Zastosowanie |
|---------|-------------|
| Art. 7 ust. 8 ustawy o VAT | Fikcja prawna transakcji łańcuchowej |
| Art. 22 ust. 2–2e ustawy o VAT | Przypisanie transportu do dostawy ruchomej |
| Art. 22 ust. 3 ustawy o VAT | Miejsce opodatkowania dostaw nieruchomych |
| Art. 13 ustawy o VAT | WDT |
| Art. 9 ustawy o VAT | WNT |
| Art. 2 pkt 8 ustawy o VAT | Eksport |
| Art. 19a, art. 20 ustawy o VAT | Obowiązek podatkowy |
| Art. 41 ust. 4–11, art. 42 | Stawka 0% WDT i eksport |
| Art. 135–138 ustawy o VAT | Transakcja trójstronna uproszczona |
| TSUE C-245/04 EMAG | Jedna dostawa ruchoma w łańcuchu |
| TSUE C-430/09 Euro Tyre | Przypisanie transportu — wiedza stron |
| TSUE C-386/16 Toridas | Dalszy nabywca znany przed transportem |
| TSUE C-401/18 Herst | Ryzyko transportowe |

## Zastrzeżenie

> Aplikacja ma charakter pomocniczy i edukacyjny. Nie stanowi porady podatkowej.  
> Wynik wymaga weryfikacji na podstawie dokumentów transakcyjnych, aktualnych przepisów,  
> interpretacji podatkowych i orzecznictwa. Skonsultuj się z doradcą podatkowym.
