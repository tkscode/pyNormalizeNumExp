import pytest

from pynormalizenumexp.expression.base import NotationType
from pynormalizenumexp.expression.limited_abstime import LimitedAbstimeExpression
from pynormalizenumexp.utility.dict_loader import DictLoader
from pynormalizenumexp.utility.digit_utility import DigitUtility


@pytest.fixture(scope="class")
def digit_utility():
    return DigitUtility(DictLoader("ja"))


class TestDigitUtility:
    def test_init_kansuji(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        # 位ごとに1つだけ確認する
        assert digit_utility.kansuji_09_to_value["〇"] == 0
        assert digit_utility.kansuji_kurai_to_power_val["十"] == 1
        assert digit_utility.kansuji_kurai_to_power_val["　"] == 0

        # notation_typeごとに1つだけ確認する
        assert digit_utility.str_to_notation_type["〇"] == NotationType.KANSUJI_09
        assert digit_utility.str_to_notation_type["十"] == NotationType.KANSUJI_KURAI_SEN
        assert digit_utility.str_to_notation_type["万"] == NotationType.KANSUJI_KURAI_MAN

    def test_is_hankakusuji(self, digit_utility: DigitUtility):
        assert digit_utility.is_hankakusuji("1") == True
        assert digit_utility.is_hankakusuji("１") == False
        assert digit_utility.is_hankakusuji("一") == False
        assert digit_utility.is_hankakusuji("あ") == False

    def test_is_zenkakusuji(self, digit_utility: DigitUtility):
        assert digit_utility.is_zenkakusuji("1") == False
        assert digit_utility.is_zenkakusuji("１") == True
        assert digit_utility.is_zenkakusuji("一") == False
        assert digit_utility.is_zenkakusuji("あ") == False

    def test_is_arabic(self, digit_utility: DigitUtility):
        assert digit_utility.is_arabic("1") == True
        assert digit_utility.is_arabic("１") == True
        assert digit_utility.is_arabic("一") == False
        assert digit_utility.is_arabic("あ") == False

    def test_is_notation_type(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        assert digit_utility.is_notation_type("〇", NotationType.KANSUJI_09) == True
        assert digit_utility.is_notation_type("〇", NotationType.KANSUJI_KURAI_MAN) == False
        assert digit_utility.is_notation_type("nothing", NotationType.KANSUJI_09) == False
        assert digit_utility.is_notation_type(None, NotationType.KANSUJI_09) == False

    def test_is_kansuji09(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        assert digit_utility.is_kansuji09("1") == False
        assert digit_utility.is_kansuji09("１") == False
        assert digit_utility.is_kansuji09("一") == True
        assert digit_utility.is_kansuji09("十") == False
        assert digit_utility.is_kansuji09("万") == False
        assert digit_utility.is_kansuji09("あ") == False

    def test_is_kansuji_kurai_sen(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        assert digit_utility.is_kansuji_kurai_sen("1") == False
        assert digit_utility.is_kansuji_kurai_sen("１") == False
        assert digit_utility.is_kansuji_kurai_sen("一") == False
        assert digit_utility.is_kansuji_kurai_sen("十") == True
        assert digit_utility.is_kansuji_kurai_sen("百") == True
        assert digit_utility.is_kansuji_kurai_sen("千") == True
        assert digit_utility.is_kansuji_kurai_sen("万") == False
        assert digit_utility.is_kansuji_kurai_sen("あ") == False

    def test_is_kansuji_kurai_man(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        assert digit_utility.is_kansuji_kurai_man("1") == False
        assert digit_utility.is_kansuji_kurai_man("１") == False
        assert digit_utility.is_kansuji_kurai_man("一") == False
        assert digit_utility.is_kansuji_kurai_man("十") == False
        assert digit_utility.is_kansuji_kurai_man("万") == True
        assert digit_utility.is_kansuji_kurai_man("億") == True
        assert digit_utility.is_kansuji_kurai_man("兆") == True
        assert digit_utility.is_kansuji_kurai_man("あ") == False

    def test_is_kansuji_kurai(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        assert digit_utility.is_kansuji_kurai("1") == False
        assert digit_utility.is_kansuji_kurai("１") == False
        assert digit_utility.is_kansuji_kurai("一") == False
        assert digit_utility.is_kansuji_kurai("十") == True
        assert digit_utility.is_kansuji_kurai("万") == True
        assert digit_utility.is_kansuji_kurai("あ") == False

    def test_is_kansuji(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        assert digit_utility.is_kansuji("1") == False
        assert digit_utility.is_kansuji("１") == False
        assert digit_utility.is_kansuji("一") == True
        assert digit_utility.is_kansuji("十") == True
        assert digit_utility.is_kansuji("万") == True
        assert digit_utility.is_kansuji("あ") == False

    def test_is_number(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        assert digit_utility.is_number("1") == True
        assert digit_utility.is_number("１") == True
        assert digit_utility.is_number("一") == True
        assert digit_utility.is_number("十") == True
        assert digit_utility.is_number("万") == True
        assert digit_utility.is_number("あ") == False

    def test_is_comma(self, digit_utility: DigitUtility):
        assert digit_utility.is_comma("、") == True
        assert digit_utility.is_comma(",") == True
        assert digit_utility.is_comma("，") == True
        assert digit_utility.is_comma("。") == False

    def test_is_decimal_point(self, digit_utility: DigitUtility):
        assert digit_utility.is_decimal_point(".") == True
        assert digit_utility.is_decimal_point("．") == True
        assert digit_utility.is_decimal_point("・") == True
        assert digit_utility.is_decimal_point("、") == False

    def test_is_range_expression(self, digit_utility: DigitUtility):
        assert digit_utility.is_range_expression("~") == True
        assert digit_utility.is_range_expression("～") == True
        assert digit_utility.is_range_expression("〜") == True
        assert digit_utility.is_range_expression("-") == True
        assert digit_utility.is_range_expression("−") == True
        assert digit_utility.is_range_expression("ー") == True
        assert digit_utility.is_range_expression("―") == True
        assert digit_utility.is_range_expression("から") == True
        assert digit_utility.is_range_expression("あ") == False

    def test_kansuji_kurai2power_value(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        assert digit_utility.kansuji_kurai2power_value("十") == 1

        with pytest.raises(ValueError):
            digit_utility.kansuji_kurai2power_value("一")

    def test_chars2notation_type(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        assert digit_utility.chars2notation_type("1") == NotationType.HANKAKU
        assert digit_utility.chars2notation_type("１") == NotationType.ZENKAKU
        assert digit_utility.chars2notation_type("一") == NotationType.KANSUJI
        assert digit_utility.chars2notation_type("あ") == NotationType.NOT_NUMBER

    def test_chars2full_notation_type(self, digit_utility: DigitUtility):
        digit_utility.init_kansuji()

        assert digit_utility.chars2full_notation_type("1") == NotationType.HANKAKU
        assert digit_utility.chars2full_notation_type("１") == NotationType.ZENKAKU
        assert digit_utility.chars2full_notation_type("一") == NotationType.KANSUJI_09
        assert digit_utility.chars2full_notation_type("十") == NotationType.KANSUJI_KURAI_SEN
        assert digit_utility.chars2full_notation_type("万") == NotationType.KANSUJI_KURAI_MAN
        assert digit_utility.chars2full_notation_type("あ") == NotationType.NOT_NUMBER
