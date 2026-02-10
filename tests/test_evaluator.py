from decimal import Decimal
from pathlib import Path

import pytest

from tariff_engine.domain.ast_schema import Contract
from tariff_engine.domain.shipment import Shipment
from tariff_engine.engine.evaluator import price

GOLDEN = Path(__file__).parent.parent / "sample_data" / "dhl_2026_ne.json"


def _contract() -> Contract:
    return Contract.model_validate_json(GOLDEN.read_text())


class TestPricing:
    def test_base_rate_zone_match(self):
        result = price(_contract(), Shipment(weight=1000, zone=5))
        assert result.total == Decimal("465.00")
        assert result.audit[0].applied is True
        assert result.audit[0].rule_type == "base_rate"

    def test_base_rate_zone_mismatch(self):
        result = price(_contract(), Shipment(weight=1000, zone=3))
        assert result.audit[0].applied is False
        assert result.total == Decimal("15.00")

    def test_overweight_surcharge(self):
        result = price(_contract(), Shipment(weight=2500, zone=5))
        surcharge = result.audit[1]
        assert surcharge.applied is True
        assert surcharge.amount_delta == Decimal("75.0")

    def test_no_surcharge_under_weight(self):
        result = price(_contract(), Shipment(weight=1500, zone=5))
        assert result.audit[1].applied is False

    def test_express_multiplier(self):
        result = price(
            _contract(),
            Shipment(weight=1000, zone=5, service_type="express"),
        )
        # rules apply in order: base=450, surcharge skipped, x1.25=562.50, +15=577.50
        assert result.total == Decimal("577.50")

    def test_full_scenario(self):
        result = price(
            _contract(),
            Shipment(weight=2500, zone=5, service_type="express"),
        )
        base = Decimal("450")
        surcharge = Decimal("75.0")
        subtotal = base + surcharge
        after_express = subtotal * Decimal("1.25")
        after_flat = after_express + Decimal("15")
        assert result.total == after_flat

    def test_audit_trail_completeness(self):
        result = price(_contract(), Shipment(weight=2500, zone=5))
        assert len(result.audit) == 4
        applied_count = sum(1 for e in result.audit if e.applied)
        assert applied_count == 3

    def test_breakdown_output(self):
        result = price(_contract(), Shipment(weight=1000, zone=5))
        text = result.breakdown
        assert "DHL_2026_NE" in text
        assert "APPLIED" in text
        assert "SKIPPED" in text
