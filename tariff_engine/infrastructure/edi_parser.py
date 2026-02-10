from tariff_engine.domain.ast_schema import Condition, Contract, Operator, Rule, RuleType

_RULE_TYPE_MAP = {"BR": RuleType.BASE_RATE, "SC": RuleType.SURCHARGE, "DC": RuleType.DISCOUNT, "MC": RuleType.MIN_CHARGE}


def _parse_value(raw: str) -> int | float | str:
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


def _build_action(elements: list[str]) -> dict:
    action_type = elements[1]
    if action_type == "set_price":
        return {"type": "set_price", "value": elements[2], "currency": elements[3] if len(elements) > 3 else "USD"}
    if action_type == "add_flat":
        return {"type": "add_flat", "value": elements[2], "currency": elements[3] if len(elements) > 3 else "USD"}
    if action_type == "add_formula":
        return {"type": "add_formula", "formula": "*".join(elements[2:])}
    if action_type == "multiply_rate":
        return {"type": "multiply_rate", "factor": elements[2]}
    raise ValueError(f"Unknown action type: {action_type}")


def parse_edi(raw: str) -> Contract:
    segments = [s.strip() for s in raw.split("~") if s.strip()]
    contract_id = ""
    carrier = ""
    rules: list[Rule] = []
    current_rule_type: RuleType | None = None
    current_conditions: list[Condition] = []
    current_action: dict | None = None

    def _flush():
        nonlocal current_rule_type, current_conditions, current_action
        if current_rule_type and current_action:
            rules.append(Rule(
                rule_type=current_rule_type,
                conditions=current_conditions,
                action=current_action,
            ))
        current_rule_type = None
        current_conditions = []
        current_action = None

    for seg in segments:
        elements = seg.split("*")
        seg_id = elements[0]

        if seg_id == "ISA":
            carrier = elements[6].strip()
        elif seg_id == "BCT":
            contract_id = elements[2]
        elif seg_id == "LIN":
            _flush()
            current_rule_type = _RULE_TYPE_MAP.get(elements[2])
        elif seg_id == "CND":
            current_conditions.append(Condition(
                field=elements[1],
                operator=Operator(elements[2]),
                value=_parse_value(elements[3]),
            ))
        elif seg_id == "ACT":
            current_action = _build_action(elements)

    _flush()

    return Contract(contract_id=contract_id, carrier=carrier, rules=rules)
