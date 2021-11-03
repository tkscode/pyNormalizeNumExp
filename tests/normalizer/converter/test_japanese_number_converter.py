import pytest

from pynormalizenumexp.normalizer.converter.japanese_number_converter import JapaneseNumberConverter
from pynormalizenumexp.utility.dict_loader import DictLoader
from pynormalizenumexp.utility.digit_utility import DigitUtility


@pytest.fixture(scope="class")
def japanese_number_converter():
    digit_utility = DigitUtility(DictLoader("ja"))
    digit_utility.init_kansuji()

    return JapaneseNumberConverter(digit_utility)


class TestJapaneseNumberConverter:
    def test_convert_arabic_kansuji_mixed_of_4digits(self, japanese_number_converter: JapaneseNumberConverter):
        res = japanese_number_converter.convert_arabic_kansuji_mixed_of_4digits("三千九百二十一")
        assert res == 3921

    def test_convert_number(self, japanese_number_converter: JapaneseNumberConverter):
        res = japanese_number_converter.convert_number("一億二千四百五十六万三千,九百二十一")
        assert res == 124563921
