from decimal import Decimal

from pydantic import BaseModel


class AuditEntry(BaseModel):
    rule_type: str
    applied: bool
    description: str
    amount_delta: Decimal = Decimal("0")


class PricingResult(BaseModel):
    contract_id: str
    total: Decimal
    currency: str
    audit: list[AuditEntry]

    @property
    def breakdown(self) -> str:
        lines = [f"Contract: {self.contract_id}"]
        for e in self.audit:
            tag = "APPLIED" if e.applied else "SKIPPED"
            lines.append(f"  [{tag}] {e.rule_type}: {e.description} ({e.amount_delta:+})")
        lines.append(f"  TOTAL: {self.currency} {self.total:.2f}")
        return "\n".join(lines)
