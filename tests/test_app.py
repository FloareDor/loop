from decimal import Decimal
from pathlib import Path

from tariff_engine.app import price_from_json
from tariff_engine.domain.shipment import Shipment

GOLDEN = Path(__file__).parent.parent / "sample_data" / "dhl_2026_ne.json"


class TestIntegration:
    def test_json_to_price(self):
        shipment = Shipment(weight=2500, zone=5)
        result = price_from_json(GOLDEN, shipment)
        assert result.contract_id == "DHL_2026_NE"
        assert result.total > Decimal("0")
        assert len(result.audit) == 4

    def test_audit_sums_to_total(self):
        shipment = Shipment(weight=2500, zone=5)
        result = price_from_json(GOLDEN, shipment)
        delta_sum = sum(e.amount_delta for e in result.audit)
        assert delta_sum == result.total

    def test_cli_output(self):
        shipment = Shipment(weight=1000, zone=5)
        result = price_from_json(GOLDEN, shipment)
        text = result.breakdown
        assert "TOTAL" in text
        assert "USD" in text
