import json
from pathlib import Path

import pytest

from tariff_engine.domain.ast_schema import (
    AddFlat, AddFormula, Contract, MultiplyRate, Operator, SetPrice,
)
from tariff_engine.domain.exceptions import UnsafeFormulaError

GOLDEN = Path(__file__).parent.parent / "sample_data" / "dhl_2026_ne.json"


class TestContractParsing:
    def test_golden_file_round_trip(self):
        raw = GOLDEN.read_text()
        contract = Contract.model_validate_json(raw)
        assert contract.contract_id == "DHL_2026_NE"
        assert len(contract.rules) == 4
        reserialized = json.loads(contract.model_dump_json())
        reparsed = Contract.model_validate(reserialized)
        assert reparsed == contract

    def test_discriminated_union_routing(self):
        contract = Contract.model_validate_json(GOLDEN.read_text())
        actions = [r.action for r in contract.rules]
        assert isinstance(actions[0], SetPrice)
        assert isinstance(actions[1], AddFormula)
        assert isinstance(actions[2], MultiplyRate)
        assert isinstance(actions[3], AddFlat)

    def test_operator_enum(self):
        contract = Contract.model_validate_json(GOLDEN.read_text())
        ops = [c.operator for r in contract.rules for c in r.conditions]
        assert Operator.EQ in ops
        assert Operator.GT in ops


class TestSchemaValidation:
    def test_empty_rules_rejected(self):
        with pytest.raises(Exception):
            Contract.model_validate({"contract_id": "X", "rules": []})

    def test_unsafe_formula_rejected(self):
        with pytest.raises(UnsafeFormulaError):
            Contract.model_validate({
                "contract_id": "X",
                "rules": [{
                    "rule_type": "surcharge",
                    "conditions": [],
                    "action": {
                        "type": "add_formula",
                        "formula": "__import__('os').system('rm -rf /')",
                    },
                }],
            })

    def test_invalid_action_type_rejected(self):
        with pytest.raises(Exception):
            Contract.model_validate({
                "contract_id": "X",
                "rules": [{
                    "rule_type": "base_rate",
                    "conditions": [],
                    "action": {"type": "unknown_action", "value": 100},
                }],
            })
