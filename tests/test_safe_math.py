import pytest

from tariff_engine.domain.exceptions import UnsafeFormulaError
from tariff_engine.engine.safe_math import eval_formula, validate_formula


class TestValidateFormula:
    def test_arithmetic(self):
        validate_formula("0.15 * (weight - 2000)")

    def test_ternary(self):
        validate_formula("10 if weight > 100 else 0")

    def test_builtins_blocked(self):
        with pytest.raises(UnsafeFormulaError, match="disallowed"):
            validate_formula("__import__('os').system('echo hi')")

    def test_lambda_blocked(self):
        with pytest.raises(UnsafeFormulaError, match="disallowed"):
            validate_formula("(lambda: 1)()")

    def test_list_comp_blocked(self):
        with pytest.raises(UnsafeFormulaError, match="disallowed"):
            validate_formula("[x for x in range(10)]")

    def test_allowed_functions(self):
        validate_formula("max(weight, 100)")
        validate_formula("min(10, abs(x))")
        validate_formula("round(x, 2)")

    def test_disallowed_function(self):
        with pytest.raises(UnsafeFormulaError, match="disallowed function"):
            validate_formula("eval('1+1')")

    def test_syntax_error(self):
        with pytest.raises(UnsafeFormulaError, match="syntax error"):
            validate_formula("1 +* 2")


class TestEvalFormula:
    def test_simple_arithmetic(self):
        assert eval_formula("0.15 * (weight - 2000)", {"weight": 2500}) == pytest.approx(75.0)

    def test_ternary(self):
        assert eval_formula("10 if weight > 100 else 0", {"weight": 50}) == 0
        assert eval_formula("10 if weight > 100 else 0", {"weight": 200}) == 10

    def test_max(self):
        assert eval_formula("max(weight * 0.1, 50)", {"weight": 300}) == pytest.approx(50)

    def test_missing_var_raises(self):
        with pytest.raises(NameError):
            eval_formula("weight * 2", {})
