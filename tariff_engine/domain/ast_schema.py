from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, field_validator


class Operator(StrEnum):
    EQ  = "=="
    NEQ = "!="
    GT  = ">"
    GTE = ">="
    LT  = "<"
    LTE = "<="


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    CAD = "CAD"


class RuleType(StrEnum):
    BASE_RATE  = "base_rate"
    SURCHARGE  = "surcharge"
    DISCOUNT   = "discount"
    MIN_CHARGE = "min_charge"


class Condition(BaseModel):
    field: str
    operator: Operator
    value: int | float | str


class SetPrice(BaseModel):
    type: Literal["set_price"]
    value: Decimal
    currency: Currency = Currency.USD


class AddFlat(BaseModel):
    type: Literal["add_flat"]
    value: Decimal
    currency: Currency = Currency.USD


class AddFormula(BaseModel):
    type: Literal["add_formula"]
    formula: str

    @field_validator("formula")
    @classmethod
    def _safe_formula(cls, v: str) -> str:
        from tariff_engine.engine.safe_math import validate_formula
        validate_formula(v)
        return v


class MultiplyRate(BaseModel):
    type: Literal["multiply_rate"]
    factor: Decimal


Action = Annotated[
    Union[SetPrice, AddFlat, AddFormula, MultiplyRate],
    Field(discriminator="type"),
]


class Rule(BaseModel):
    rule_type: RuleType
    conditions: list[Condition] = Field(default_factory=list)
    action: Action


class Contract(BaseModel):
    contract_id: str
    carrier: str = ""
    effective_date: str = ""
    rules: list[Rule] = Field(min_length=1)
