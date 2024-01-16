# flake8: noqa
import math
import pytest

from pynormalizenumexp.expression.base import NNumber
from pynormalizenumexp.normalizer.symbol_fixer import SymbolFixer
from pynormalizenumexp.utility.dict_loader import DictLoader
from pynormalizenumexp.utility.digit_utility import DigitUtility


@pytest.fixture(scope="class")
def symbol_fixer():
    digit_utility = DigitUtility(DictLoader("ja"))
    digit_utility.init_kansuji()

    return SymbolFixer(digit_utility)


class TestSymbolFixer:
    def test_fix_numbers_by_symbol(self, symbol_fixer: SymbolFixer):
        numbers = [
            NNumber("1", 1, 2),
            NNumber("1", 3, 4)
        ]
        numbers[0].value_lower_bound = numbers[0].value_upper_bound = 1
        numbers[1].value_lower_bound = numbers[1].value_upper_bound = 1
        res = symbol_fixer.fix_numbers_by_symbol("-1～1の値を取る", numbers)
        expect = [
            NNumber("-1～1", 0, 4)
        ]
        expect[0].value_lower_bound = -1
        expect[0].value_upper_bound = 1
        assert res == expect

    def test_extract_plus(self, symbol_fixer: SymbolFixer):
        res = symbol_fixer.extract_plus("+1", -1)
        assert res is None

        res = symbol_fixer.extract_plus("+1", 0)
        assert res == "+"

        res = symbol_fixer.extract_plus("＋1", 0)
        assert res == "＋"

        res = symbol_fixer.extract_plus("+1", 1)
        assert res is None

        res = symbol_fixer.extract_plus("プラス2", 2)
        assert res == "プラス"

        res = symbol_fixer.extract_plus("マイナス2", 3)
        assert res is None

    def test_extract_minus(self, symbol_fixer: SymbolFixer):
        res = symbol_fixer.extract_minus("-1", -1)
        assert res is None

        res = symbol_fixer.extract_minus("-1", 0)
        assert res == "-"

        res = symbol_fixer.extract_minus("－1", 0)
        assert res == "－"

        res = symbol_fixer.extract_minus("ー1", 0)
        assert res == "ー"

        res = symbol_fixer.extract_minus("-1", 1)
        assert res is None

        res = symbol_fixer.extract_minus("マイナス2", 3)
        assert res == "マイナス"

        res = symbol_fixer.extract_minus("プラス2", 3)
        assert res is None

    def test_create_decimal_value(self, symbol_fixer: SymbolFixer):
        number = NNumber("14")
        number.value_lower_bound = 14
        res = symbol_fixer.create_decimal_value(number)
        # 誤差によりぴったり0.14にならないのでiscloseで近似値かどうか見る
        assert math.isclose(res, 0.14)

        number = NNumber("002")
        number.value_lower_bound = 2
        res = symbol_fixer.create_decimal_value(number)
        assert math.isclose(res, 0.002)

    def test_fix_decimal_point(self, symbol_fixer: SymbolFixer):
        number = NNumber("3", 1, 2)
        number.value_lower_bound = number.value_upper_bound = 3
        next_number = NNumber("14", 3, 5)
        next_number.value_lower_bound = next_number.value_upper_bound = 14
        res = symbol_fixer.fix_decimal_point(number, next_number, ".")
        expect = NNumber("3.14", 1, 5)
        expect.value_lower_bound = expect.value_upper_bound = 3.14
        assert res == expect

        number = NNumber("9", 1, 2)
        number.value_lower_bound = number.value_upper_bound = 9
        next_number = NNumber("3万", 3, 5)
        next_number.value_lower_bound = next_number.value_upper_bound = 3
        res = symbol_fixer.fix_decimal_point(number, next_number, ".")
        expect = NNumber("9.3万", 1, 5)
        expect.value_lower_bound = expect.value_upper_bound = 93000
        assert res == expect

    def test_fix_range_expression(self, symbol_fixer: SymbolFixer):
        number = NNumber("1", 1, 2)
        number.value_lower_bound = number.value_upper_bound = 1
        next_number = NNumber("3", 3, 4)
        next_number.value_lower_bound = next_number.value_upper_bound = 3
        res = symbol_fixer.fix_range_expression(number, next_number, "～")
        expect = NNumber("1～3", 1, 4)
        expect.value_lower_bound = 1
        expect.value_upper_bound = 3
        assert res == expect

    def test_fix_prefix_symbol(self, symbol_fixer: SymbolFixer):
        number = NNumber("1", 2, 3)
        number.value_lower_bound = number.value_upper_bound = 1
        res = symbol_fixer.fix_prefix_symbol("1+1=2", number)
        expect = NNumber("+1", 1, 3)
        expect.value_lower_bound = expect.value_upper_bound = 1
        assert res == expect

        number = NNumber("1", 2, 3)
        number.value_lower_bound = number.value_upper_bound = 1
        res = symbol_fixer.fix_prefix_symbol("1-1=0", number)
        expect = NNumber("-1", 1, 3)
        expect.value_lower_bound = expect.value_upper_bound = -1
        assert res == expect

    def test_fix_intermediate_symbol(self, symbol_fixer: SymbolFixer):
        number = NNumber("3", 0, 1)
        next_number = NNumber("14", 1, 3)
        res = symbol_fixer.fix_intermediate_symbol("314", next_number, number)
        assert res == next_number

        res = symbol_fixer.fix_intermediate_symbol("314", number, next_number)
        assert res == number

        next_number = NNumber("14", 2, 4)
        res = symbol_fixer.fix_intermediate_symbol("3.14", number, next_number)
        assert res == number

        number.value_lower_bound = number.value_upper_bound = 3
        next_number.value_lower_bound = next_number.value_upper_bound = 14

        res = symbol_fixer.fix_intermediate_symbol("3.14", number, next_number)
        expect = NNumber("3.14", 0, 4)
        expect.value_lower_bound = expect.value_upper_bound = 3.14
        assert res == expect

        res = symbol_fixer.fix_intermediate_symbol("3～14", number, next_number)
        expect = NNumber("3～14", 0, 4)
        expect.value_lower_bound = 3
        expect.value_upper_bound = 14
        assert res == expect

        number = NNumber("10", 0, 2)
        number.value_lower_bound = number.value_upper_bound = 10
        next_number = NNumber("11", 3, 5)
        next_number.value_lower_bound = next_number.value_upper_bound = 11
        res = symbol_fixer.fix_intermediate_symbol("10,11", number, next_number)
        expect = NNumber("10,11", 0, 5)
        expect.value_lower_bound = 10
        expect.value_upper_bound = 11
        assert res == expect
