class TariffError(Exception):
    pass


class UnsafeFormulaError(TariffError):
    def __init__(self, formula: str, reason: str):
        super().__init__(f"Unsafe formula '{formula}': {reason}")


class RuleEvalError(TariffError):
    pass
