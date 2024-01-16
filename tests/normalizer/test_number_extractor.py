# flake8: noqa
import pytest

from pynormalizenumexp.expression.base import NNumber, NotationType
from pynormalizenumexp.normalizer.number_extractor import NumberExtractor
from pynormalizenumexp.utility.dict_loader import DictLoader
from pynormalizenumexp.utility.digit_utility import DigitUtility


@pytest.fixture(scope="class")
def number_extractor():
    digit_utility = DigitUtility(DictLoader("ja"))
    digit_utility.init_kansuji()

    return NumberExtractor(digit_utility)


class TestNumberExtractor():
    def test_is_invalid_notation_type(self, number_extractor: NumberExtractor):
        res = number_extractor.is_invalid_notation_type([NotationType.ZENKAKU, NotationType.HANKAKU])
        assert res == True

        res = number_extractor.is_invalid_notation_type([NotationType.HANKAKU, NotationType.HANKAKU])
        assert res == False

    def test_split_number_by_kansuji_kurai(self, number_extractor: NumberExtractor):
        number = NNumber("一万五千七百億", 0, 7)
        number.notation_type = [NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_MAN, NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN,
                                NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_KURAI_MAN]
        res = number_extractor.split_number_by_kansuji_kurai(number)
        expect = [
            NNumber("一万五千七百", 0, 6),
            NNumber("億", 6, 7)
        ]
        expect[0].notation_type = [NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_MAN, NotationType.KANSUJI_09,
                                   NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN]
        expect[1].notation_type = [NotationType.KANSUJI_KURAI_MAN]
        assert res == expect

    def test_split_number_by_notation_type(self, number_extractor: NumberExtractor):
        number = NNumber("2000三十", 0, 6)
        number.notation_type = [NotationType.HANKAKU, NotationType.HANKAKU, NotationType.HANKAKU, NotationType.HANKAKU,
                                NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN]
        res = number_extractor.split_number_by_notation_type(number)
        expect = [
            NNumber("2000", 0, 4),
            NNumber("三十", 4, 6)
        ]
        expect[0].notation_type = [NotationType.HANKAKU, NotationType.HANKAKU, NotationType.HANKAKU, NotationType.HANKAKU]
        expect[1].notation_type = [NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN]
        assert res == expect

    def test_extract_number(self, number_extractor: NumberExtractor):
        res = number_extractor.extract_number("一万五千七百億と2000三十")
        expect = [
            NNumber("一万五千七百", 0, 6),
            NNumber("億", 6, 7),
            NNumber("2000", 8, 12),
            NNumber("三十", 12, 14)
        ]
        expect[0].notation_type = [NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_MAN, NotationType.KANSUJI_09,
                                   NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN]
        expect[1].notation_type = [NotationType.KANSUJI_KURAI_MAN]
        expect[2].notation_type = [NotationType.HANKAKU, NotationType.HANKAKU, NotationType.HANKAKU, NotationType.HANKAKU]
        expect[3].notation_type = [NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN]
        assert res == expect
