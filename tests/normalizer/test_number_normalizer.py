import pytest

from pynormalizenumexp.expression.base import NNumber, NotationType
from pynormalizenumexp.utility.dict_loader import DictLoader
from pynormalizenumexp.normalizer.number_normalizer import NumberNormalizer


@pytest.fixture(scope="class")
def number_normalizer():
    return NumberNormalizer(DictLoader("ja"))


class TestNumberNormalizer:
    def test_process_標準(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.process("その3,244人が３，４５６，７８９円で百二十三万四千五百六十七円")
        expect = [NNumber("3,244", 2, 7), NNumber("３，４５６，７８９", 9, 18), NNumber("百二十三万四千五百六十七", 20, 32)]
        expect[0].value_lower_bound = expect[0].value_upper_bound = 3244
        expect[0].notation_type = [NotationType.HANKAKU]
        expect[1].value_lower_bound = expect[1].value_upper_bound = 3456789
        expect[1].notation_type = [NotationType.ZENKAKU]
        expect[2].value_lower_bound = expect[2].value_upper_bound = 1234567
        expect[2].notation_type = [NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN,
                                   NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_MAN, NotationType.KANSUJI_09,
                                   NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN,
                                   NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09]
        assert res == expect

    def test_process_小数点あり(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.process("その3,244.15人が３，４５６，７８９．４５６円")
        expect = [NNumber("3,244.15", 2, 10), NNumber("３，４５６，７８９．４５６", 12, 25)]
        expect[0].value_lower_bound = expect[0].value_upper_bound = 3244.15
        expect[0].notation_type = [NotationType.HANKAKU]
        expect[1].value_lower_bound = expect[1].value_upper_bound = 3456789.456
        expect[1].notation_type = [NotationType.ZENKAKU]
        assert res == expect

        res = number_normalizer.process("131.1ポイントというスコアを叩き出した")
        expect = [NNumber("131.1", 0, 5)]
        expect[0].value_lower_bound = expect[0].value_upper_bound = 131.1
        expect[0].notation_type = [NotationType.HANKAKU, NotationType.HANKAKU, NotationType.HANKAKU]
        assert res == expect

        res = number_normalizer.process("9.3万円も損した")
        expect = [NNumber("9.3万", 0, 4)]
        expect[0].value_lower_bound = expect[0].value_upper_bound = 93000
        expect[0].notation_type = [NotationType.HANKAKU]
        assert res == expect

    def test_process_プラスあり(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.process("その+3,244人が＋３，４５６，７８９円でプラス百二十三万四千五百六十七円")
        expect = [NNumber("+3,244", 2, 8), NNumber("＋３，４５６，７８９", 10, 20), NNumber("プラス百二十三万四千五百六十七", 22, 37)]
        expect[0].value_lower_bound = expect[0].value_upper_bound = 3244
        expect[0].notation_type = [NotationType.HANKAKU]
        expect[1].value_lower_bound = expect[1].value_upper_bound = 3456789
        expect[1].notation_type = [NotationType.ZENKAKU]
        expect[2].value_lower_bound = expect[2].value_upper_bound = 1234567
        expect[2].notation_type = [NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN,
                                   NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_MAN, NotationType.KANSUJI_09,
                                   NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN,
                                   NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09]
        assert res == expect

    def test_process_マイナスあり(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.process("その-3,244人がー３，４５６，７８９円でマイナス百二十三万四千五百六十七円")
        expect = [NNumber("-3,244", 2, 8), NNumber("ー３，４５６，７８９", 10, 20), NNumber("マイナス百二十三万四千五百六十七", 22, 38)]
        expect[0].value_lower_bound = expect[0].value_upper_bound = -3244
        expect[0].notation_type = [NotationType.HANKAKU]
        expect[1].value_lower_bound = expect[1].value_upper_bound = -3456789
        expect[1].notation_type = [NotationType.ZENKAKU]
        expect[2].value_lower_bound = expect[2].value_upper_bound = -1234567
        expect[2].notation_type = [NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN,
                                   NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_MAN, NotationType.KANSUJI_09,
                                   NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN,
                                   NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN, NotationType.KANSUJI_09]
        assert res == expect

    def test_process_範囲あり(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.process("その10~20人が、１００〜２００円で")
        expect = [NNumber("10~20", 2, 7), NNumber("１００〜２００", 10, 17)]
        expect[0].value_lower_bound = 10
        expect[0].value_upper_bound = 20
        expect[0].notation_type = [NotationType.HANKAKU, NotationType.HANKAKU]
        expect[1].value_lower_bound = 100
        expect[1].value_upper_bound = 200
        expect[1].notation_type = [NotationType.ZENKAKU, NotationType.ZENKAKU, NotationType.ZENKAKU]
        assert res == expect

        res = number_normalizer.process("1,2個")
        expect = [NNumber("1,2", 0, 3)]
        expect[0].value_lower_bound = 1
        expect[0].value_upper_bound = 2
        expect[0].notation_type = [NotationType.HANKAKU]
        assert res == expect

    def test_process_数値なし(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.process("あいうえお")
        assert res == []

    def test_process_invalid_notation(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.process("1千1千1千")
        expect = [NNumber("1千1", 0, 3), NNumber("千1", 3, 5), NNumber("千", 5, 6)]
        expect[0].value_lower_bound = expect[0].value_upper_bound = 1001
        expect[0].notation_type = [NotationType.HANKAKU, NotationType.KANSUJI_KURAI_SEN, NotationType.HANKAKU]
        expect[1].value_lower_bound = expect[1].value_upper_bound = 1001
        expect[1].notation_type = [NotationType.KANSUJI_KURAI_SEN, NotationType.HANKAKU]
        expect[2].value_lower_bound = expect[2].value_upper_bound = 1000
        expect[2].notation_type = [NotationType.KANSUJI_KURAI_SEN]
        assert res == expect

        res = number_normalizer.process("２００７20人がきた")
        expect = [NNumber("２００７", 0, 4), NNumber("20", 4, 6)]
        expect[0].value_lower_bound = expect[0].value_upper_bound = 2007
        expect[0].notation_type = [NotationType.ZENKAKU, NotationType.ZENKAKU, NotationType.ZENKAKU, NotationType.ZENKAKU]
        expect[1].value_lower_bound = expect[1].value_upper_bound = 20
        expect[1].notation_type = [NotationType.HANKAKU, NotationType.HANKAKU]
        assert res == expect

        res = number_normalizer.process("２００７二十人がきた")
        expect = [NNumber("２００７", 0, 4), NNumber("二十", 4, 6)]
        expect[0].value_lower_bound = expect[0].value_upper_bound = 2007
        expect[0].notation_type = [NotationType.ZENKAKU, NotationType.ZENKAKU, NotationType.ZENKAKU, NotationType.ZENKAKU]
        expect[1].value_lower_bound = expect[1].value_upper_bound = 20
        expect[1].notation_type = [NotationType.KANSUJI_09, NotationType.KANSUJI_KURAI_SEN]
        assert res == expect

    # TODO https://github.com/cotogoto/normalize-numexp/blob/main/test/jp/livlog/numexp/numberNormalizer/NumberNormalizerTest.java#L349-L409

    def test_suffix_is_arabic(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.suffix_is_arabic("10")
        assert res == True

        res = number_normalizer.suffix_is_arabic("１０")
        assert res == True

        res = number_normalizer.suffix_is_arabic("10あ")
        assert res == False

        res = number_normalizer.suffix_is_arabic("")
        assert res == False

    def test_prefix_3digits_is_arabic(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.prefix_3digits_is_arabic("1000")
        assert res == True

        res = number_normalizer.prefix_3digits_is_arabic("１０００")
        assert res == True

        res = number_normalizer.prefix_3digits_is_arabic("100")
        assert res == True

        res = number_normalizer.prefix_3digits_is_arabic("10")
        assert res == False

        res = number_normalizer.prefix_3digits_is_arabic("あ1000")
        assert res == False

    def test_is_valid_comma_notation(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.is_valid_comma_notation("3", "000")
        assert res == True

        res = number_normalizer.is_valid_comma_notation("3", "000円")
        assert res == True

        res = number_normalizer.is_valid_comma_notation("3あ", "000")
        assert res == False

        res = number_normalizer.is_valid_comma_notation("3", "00")
        assert res == False

        res = number_normalizer.is_valid_comma_notation("29", "30")
        assert res == False

    def test_join_numbers_by_comma(self, number_normalizer: NumberNormalizer):
        numbers = [NNumber("3", 5, 6), NNumber("000", 7, 10)]
        res = number_normalizer.join_numbers_by_comma("この商品は3,000円だ", numbers)
        assert res == [NNumber("3,000", 5, 10)]

        numbers = [NNumber("29", 6, 8), NNumber("30", 9, 11)]
        res = number_normalizer.join_numbers_by_comma("当たり番号は29,30だ", numbers)
        assert res == numbers

    def test_convert_number(self, number_normalizer: NumberNormalizer):
        numbers = [
            NNumber("１，２３４"), NNumber("１，２３４，５６７"), NNumber("一二三四五六七"), NNumber("123万4567"),
            NNumber("百二十三万四千五百六十七"), NNumber("百2十3万4千5百6十7")
        ]
        res = number_normalizer.convert_number(numbers)
        expect = [
            NNumber("１，２３４"), NNumber("１，２３４，５６７"), NNumber("一二三四五六七"), NNumber("123万4567"),
            NNumber("百二十三万四千五百六十七"), NNumber("百2十3万4千5百6十7")
        ]
        expect[0].value_lower_bound = expect[0].value_upper_bound = 1234
        expect[1].value_lower_bound = expect[1].value_upper_bound = 1234567
        expect[2].value_lower_bound = expect[2].value_upper_bound = 1234567
        expect[3].value_lower_bound = expect[3].value_upper_bound = 1234567
        expect[4].value_lower_bound = expect[4].value_upper_bound = 1234567
        expect[5].value_lower_bound = expect[5].value_upper_bound = 1234567
        assert res == expect

    def test_fix_prefix_su(self, number_normalizer: NumberNormalizer):
        number = NNumber("十万", 0, 2)
        res = number_normalizer.fix_prefix_su("十万円", number)
        assert res == number

        number = NNumber("十万", 3, 5)
        res = number_normalizer.fix_prefix_su("これは十万円の価値がある", number)
        assert res == number

        number = NNumber("十万", 4, 6)
        number.value_lower_bound = number.value_upper_bound = 100000
        res = number_normalizer.fix_prefix_su("これは数十万円の価値がある", number)
        expect = NNumber("数十万", 3, 6)
        expect.value_lower_bound = 100000
        expect.value_upper_bound = 900000
        assert res == expect

    def test_fix_intermediate_su(self, number_normalizer: NumberNormalizer):
        cur_number = NNumber("十万", 0, 2)
        next_number = NNumber("二十万", 2, 5)
        res = number_normalizer.fix_intermediate_su("十万二十万", cur_number, next_number)
        assert res == cur_number

        cur_number = NNumber("十万", 0, 2)
        next_number = NNumber("二十万", 3, 6)
        res = number_normalizer.fix_intermediate_su("十万と二十万", cur_number, next_number)
        assert res == cur_number

        cur_number = NNumber("十", 3, 4)
        cur_number.value_lower_bound = cur_number.value_upper_bound = 10
        next_number = NNumber("万", 5, 6)
        next_number.value_lower_bound = next_number.value_upper_bound = 10000
        res = number_normalizer.fix_intermediate_su("これは十数万円の価値がある", cur_number, next_number)
        expect = NNumber("十数万", 3, 6)
        expect.value_lower_bound = 110000
        expect.value_upper_bound = 190000
        assert res == expect

    def test_fix_suffix_su(self, number_normalizer: NumberNormalizer):
        number = NNumber("十", 3, 4)
        res = number_normalizer.fix_suffix_su("これは十円の価値がある", number)
        assert res == number

        number = NNumber("十", 3, 4)
        number.value_lower_bound = number.value_upper_bound = 10
        res = number_normalizer.fix_suffix_su("これは十数円の価値がある", number)
        expect = NNumber("十数", 3, 5)
        expect.value_lower_bound = 11
        expect.value_upper_bound = 19
        assert res == expect

    def test_fix_numbers_by_su(self, number_normalizer: NumberNormalizer):
        numbers = [
            NNumber("十", 3, 4), NNumber("万", 8, 9), NNumber("十", 12, 13), NNumber("百", 17, 18), NNumber("十", 19, 20),
            NNumber("一万", 23, 25), NNumber("千", 26, 27), NNumber("十", 30, 31), NNumber("万", 32, 33)
        ]
        numbers[0].value_lower_bound = numbers[0].value_upper_bound = 10
        numbers[1].value_lower_bound = numbers[1].value_upper_bound = 10000
        numbers[2].value_lower_bound = numbers[2].value_upper_bound = 10
        numbers[3].value_lower_bound = numbers[3].value_upper_bound = 100
        numbers[4].value_lower_bound = numbers[4].value_upper_bound = 10
        numbers[5].value_lower_bound = numbers[5].value_upper_bound = 10000
        numbers[6].value_lower_bound = numbers[6].value_upper_bound = 1000
        numbers[7].value_lower_bound = numbers[7].value_upper_bound = 10
        numbers[8].value_lower_bound = numbers[8].value_upper_bound = 10000
        res = number_normalizer.fix_numbers_by_su("その数十人が、数万人で、十数人で、百数十人で、一万数千人で、十数万人で、", numbers)
        expect = [
            NNumber("数十", 2, 4), NNumber("数万", 7, 9), NNumber("十数", 12, 14),
            NNumber("百数十", 17, 20), NNumber("一万数千", 23, 27), NNumber("十数万", 30, 33)
        ]
        expect[0].value_lower_bound = 10
        expect[0].value_upper_bound = 90
        expect[1].value_lower_bound = 10000
        expect[1].value_upper_bound = 90000
        expect[2].value_lower_bound = 11
        expect[2].value_upper_bound = 19
        expect[3].value_lower_bound = 110
        expect[3].value_upper_bound = 190
        expect[4].value_lower_bound = 11000
        expect[4].value_upper_bound = 19000
        expect[5].value_lower_bound = 110000
        expect[5].value_upper_bound = 190000
        assert res == expect

    def test_is_only_kansuji_kurai_man(self, number_normalizer: NumberNormalizer):
        res = number_normalizer.is_only_kansuji_kurai_man("十二")
        assert res == False

        res = number_normalizer.is_only_kansuji_kurai_man("億")
        assert res == True

    def test_remove_only_kansuji_kurai_man(self, number_normalizer: NumberNormalizer):
        numbers = [NNumber("十二万"), NNumber("億"), NNumber("三万")]
        res = number_normalizer.remove_only_kansuji_kurai_man(numbers)
        expect = [NNumber("十二万"), NNumber("三万")]
        assert res == expect

    def test_remove_unnecessary_data(self, number_normalizer: NumberNormalizer):
        numbers = [NNumber("十二万"), NNumber("2億", 0, 2), NNumber("2億", 0, 2), NNumber("三万", 3, 5)]
        res = number_normalizer.remove_unnecessary_data(numbers)
        expect = [NNumber("2億", 0, 2), NNumber("三万", 3, 5)]
        assert res == expect
