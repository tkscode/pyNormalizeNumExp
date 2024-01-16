# flake8: noqa
import pytest

from pynormalizenumexp.normalizer.converter.number_converter import NumberConverter
from pynormalizenumexp.utility.dict_loader import DictLoader
from pynormalizenumexp.utility.digit_utility import DigitUtility


@pytest.fixture(scope="class")
def number_converter():
    digit_utility = DigitUtility(DictLoader("ja"))
    digit_utility.init_kansuji()

    return NumberConverter(digit_utility)


class TestNumberConverter:
    # convert_number関数はconvert_arabic_kansuji_mixed_of_4digits関数が必要なのでここでは見ない

    def test_delete_connma(self, number_converter: NumberConverter):
        res = number_converter.delete_connma("1,234，567、890")
        assert res == "1234567890"

    def test_split_by_kansuji_kurai(self, number_converter: NumberConverter):
        res = number_converter.split_by_kansuji_kurai("一億と二千年前からあいうえお")
        expect = [
            ("一", "億"),
            ("と二千年前からあいうえお", "　")
        ]
        assert res == expect

        res = number_converter.split_by_kansuji_kurai("百二十三万四千五百六十七")
        expect = [
            ("百二十三", "万"),
            ("四千五百六十七", "　")
        ]
        assert res == expect
