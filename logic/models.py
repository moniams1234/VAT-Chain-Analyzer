# logic/models.py
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class VatStatus(str, Enum):
    ACTIVE_VAT = "podatnik VAT czynny"
    EU_VAT = "podatnik VAT UE"
    NON_EU = "podatnik spoza UE"
    CONSUMER = "konsument / niepodatnik"


class TransportType(str, Enum):
    ROAD = "drogowy"
    SEA = "morski"
    AIR = "lotniczy"
    RAIL = "kolejowy"
    MIXED = "mieszany"


class DeliveryType(str, Enum):
    DOMESTIC = "dostawa krajowa"
    WDT = "WDT (wewnątrzwspólnotowa dostawa towarów)"
    WNT = "WNT (wewnątrzwspólnotowe nabycie towarów)"
    EXPORT = "eksport towarów"
    IMPORT = "import towarów"
    OUTSIDE_COUNTRY = "dostawa poza terytorium kraju"
    TRIANGULAR = "transakcja trójstronna uproszczona"
    UNKNOWN = "wymaga weryfikacji"


class ConfidenceLevel(str, Enum):
    HIGH = "wysoki"
    MEDIUM = "średni"
    LOW = "niski"
    REQUIRES_VERIFICATION = "wymaga weryfikacji"


@dataclass
class Party:
    name: str
    country_code: str
    country_name: str
    vat_status: VatStatus
    is_polish: bool = False
    is_eu: bool = False
    index: int = 0


@dataclass
class TransactionInput:
    parties: list[Party]
    transport_organizer_index: int  # index of party
    transport_from_country: str
    transport_to_country: str
    transport_type: TransportType
    incoterms: str
    intermediary_provided_vat_of_origin: bool
    goods_leave_eu: bool
    goods_enter_eu: bool
    documents: list[str]
    use_ai: bool = False

    # Derived
    num_parties: int = 0
    has_polish_party: bool = False

    def __post_init__(self):
        self.num_parties = len(self.parties)
        self.has_polish_party = any(p.is_polish for p in self.parties)


@dataclass
class DeliveryAnalysis:
    delivery_index: int
    seller: Party
    buyer: Party
    is_movable: bool
    delivery_type: DeliveryType
    taxation_country: str
    taxation_country_name: str
    legal_basis_keys: list[str] = field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    notes: str = ""
    is_triangular_simplified: bool = False
    jpk_codes: list[str] = field(default_factory=list)


@dataclass
class PolishPartyAnalysis:
    party: Party
    role_description: str
    vat_output: bool  # VAT należny
    vat_input: bool   # VAT naliczony
    delivery_type: DeliveryType
    may_need_foreign_registration: bool
    foreign_registration_country: Optional[str]
    jpk_v7_entries: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class TaxObligationAnalysis:
    moment_of_obligation: str
    legal_basis_key: str
    settlement_period: str
    zero_rate_conditions: list[str] = field(default_factory=list)
    zero_rate_applicable: bool = False


@dataclass
class RuleEngineResult:
    is_chain_transaction: bool
    num_deliveries: int
    movable_delivery_index: Optional[int]
    deliveries: list[DeliveryAnalysis]
    polish_party_analyses: list[PolishPartyAnalysis]
    tax_obligation: Optional[TaxObligationAnalysis]
    triangular_simplified_possible: bool
    warnings: list[str] = field(default_factory=list)
    requires_verification: list[str] = field(default_factory=list)
    applied_legal_basis: list[str] = field(default_factory=list)
    jpk_summary: dict = field(default_factory=dict)
