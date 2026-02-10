from decimal import Decimal
from pathlib import Path

import pytest

from tariff_engine.domain.ast_schema import AddFlat, AddFormula, Contract, MultiplyRate, SetPrice
from tariff_engine.domain.shipment import Shipment
from tariff_engine.engine.evaluator import price
from tariff_engine.infrastructure.edi_parser import parse_edi

GOLDEN_EDI = Path(__file__).parent.parent / "sample_data" / "dhl_2026_ne.edi"
GOLDEN_JSON = Path(__file__).parent.parent / "sample_data" / "dhl_2026_ne.json"


class TestEdiParsing:
    def test_parses_contract_id(self):
        contract = parse_edi(GOLDEN_EDI.read_text())
        assert contract.contract_id == "DHL_2026_NE"

    def test_parses_carrier(self):
        contract = parse_edi(GOLDEN_EDI.read_text())
        assert contract.carrier == "DHL"

    def test_parses_all_rules(self):
        contract = parse_edi(GOLDEN_EDI.read_text())
        assert len(contract.rules) == 4

    def test_action_types(self):
        contract = parse_edi(GOLDEN_EDI.read_text())
        actions = [r.action for r in contract.rules]
        assert isinstance(actions[0], SetPrice)
        assert isinstance(actions[1], AddFormula)
        assert isinstance(actions[2], MultiplyRate)
        assert isinstance(actions[3], AddFlat)

    def test_conditions_parsed(self):
        contract = parse_edi(GOLDEN_EDI.read_text())
        assert contract.rules[0].conditions[0].field == "zone"
        assert contract.rules[0].conditions[0].value == 5
        assert contract.rules[1].conditions[0].field == "weight"


class TestEdiJsonParity:
    def test_same_pricing_result(self):
        edi_contract = parse_edi(GOLDEN_EDI.read_text())
        json_contract = Contract.model_validate_json(GOLDEN_JSON.read_text())
        shipment = Shipment(weight=2500, zone=5)

        edi_result = price(edi_contract, shipment)
        json_result = price(json_contract, shipment)

        assert edi_result.total == json_result.total
        assert len(edi_result.audit) == len(json_result.audit)
        for e, j in zip(edi_result.audit, json_result.audit):
            assert e.applied == j.applied
            assert e.amount_delta == j.amount_delta

    def test_unconditional_rule(self):
        contract = parse_edi(GOLDEN_EDI.read_text())
        assert contract.rules[3].conditions == []
