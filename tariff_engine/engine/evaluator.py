import operator as op
from decimal import Decimal

from tariff_engine.domain.ast_schema import (
    AddFlat, AddFormula, Contract, Condition, MultiplyRate, Operator, Rule, SetPrice,
)
from tariff_engine.domain.result import AuditEntry, PricingResult
from tariff_engine.domain.shipment import Shipment
from tariff_engine.engine.safe_math import eval_formula

_OPS: dict[Operator, callable] = {
    Operator.EQ:  op.eq,
    Operator.NEQ: op.ne,
    Operator.GT:  op.gt,
    Operator.GTE: op.ge,
    Operator.LT:  op.lt,
    Operator.LTE: op.le,
}


def _check(cond: Condition, ctx: dict) -> bool:
    actual = ctx.get(cond.field)
    if actual is None:
        return False
    return _OPS[cond.operator](actual, cond.value)


def _conditions_met(rule: Rule, ctx: dict) -> bool:
    return all(_check(c, ctx) for c in rule.conditions)


def price(contract: Contract, shipment: Shipment) -> PricingResult:
    ctx = shipment.model_dump()
    total = Decimal("0")
    currency = "USD"
    audit: list[AuditEntry] = []

    for rule in contract.rules:
        met = _conditions_met(rule, ctx)
        delta = Decimal("0")
        desc = ""

        match rule.action:
            case SetPrice(value=v, currency=c):
                desc = f"set base {v}"
                if met:
                    delta = v - total
                    total = v
                    currency = c.value
            case AddFlat(value=v):
                desc = f"flat +{v}"
                if met:
                    delta = v
                    total += v
            case AddFormula(formula=f):
                if met:
                    result = Decimal(str(eval_formula(f, ctx)))
                    delta = result
                    total += result
                desc = f"formula: {f}" + (f" = {delta}" if met else "")
            case MultiplyRate(factor=f):
                desc = f"multiply x{f}"
                if met:
                    delta = total * f - total
                    total *= f

        audit.append(AuditEntry(
            rule_type=rule.rule_type.value,
            applied=met,
            description=desc,
            amount_delta=delta if met else Decimal("0"),
        ))

    return PricingResult(
        contract_id=contract.contract_id,
        total=total,
        currency=currency,
        audit=audit,
    )
