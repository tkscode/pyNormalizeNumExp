import pytest

from pynormalizenumexp.expression.base import INF
from pynormalizenumexp.expression.numerical import NumericalExpression
from pynormalizenumexp.normalizer.numerical_expr_normalizer import NumericalExpressionNormalizer
from pynormalizenumexp.utility.dict_loader import DictLoader


@pytest.fixture(scope="class")
def numerical_expr_normalizer():
    return NumericalExpressionNormalizer(DictLoader("ja"))


class TestNumericalExpressionNormalizer:
    def test_process(self, numerical_expr_normalizer: NumericalExpressionNormalizer):
        res = numerical_expr_normalizer.process("その三人が並んだ")
        expect = [NumericalExpression("三人", 2, 4, 3, 3)]
        expect[0].counter = "人"
        assert res == expect

        res = numerical_expr_normalizer.process("3kgの砂糖と、2USドルの車")
        expect = [NumericalExpression("3kg", 0, 3, 3000, 3000), NumericalExpression("2USドル", 8, 13, 2, 2)]
        expect[0].counter = "g"
        expect[1].counter = "ドル"
        assert res == expect

    def test_process_about(self, numerical_expr_normalizer: NumericalExpressionNormalizer):
        res = numerical_expr_normalizer.process("その約十人がぼぼぼぼ")
        expect = [NumericalExpression("約十人", 2, 5, 7, 13)]
        expect[0].counter = "人"
        assert res == expect

        res = numerical_expr_normalizer.process("そのおよそ十人がぼぼぼぼ")
        expect = [NumericalExpression("およそ十人", 2, 7, 7, 13)]
        expect[0].counter = "人"
        assert res == expect

    def test_process_over_less(self, numerical_expr_normalizer: NumericalExpressionNormalizer):
        res = numerical_expr_normalizer.process("その三人以上がぼぼぼぼ")
        expect = [NumericalExpression("三人以上", 2, 6, 3, INF)]
        expect[0].counter = "人"
        assert res == expect

        res = numerical_expr_normalizer.process("その約十人以上がぼぼぼぼ")
        expect = [NumericalExpression("約十人以上", 2, 7, 7, INF)]
        expect[0].counter = "人"
        assert res == expect

        res = numerical_expr_normalizer.process("その三人以下がぼぼぼぼ")
        expect = [NumericalExpression("三人以下", 2, 6, -INF, 3)]
        expect[0].counter = "人"
        assert res == expect

    def test_process_kyou_jaku(self, numerical_expr_normalizer: NumericalExpressionNormalizer):
        res = numerical_expr_normalizer.process("お茶を10本強飲んだ")
        expect = [NumericalExpression("10本強", 3, 7, 10, 16)]
        expect[0].counter = "本"
        assert res == expect

        res = numerical_expr_normalizer.process("お茶を10本弱飲んだ")
        expect = [NumericalExpression("10本弱", 3, 7, 5, 10)]
        expect[0].counter = "本"
        assert res == expect

    def test_process_ordinary(self, numerical_expr_normalizer: NumericalExpressionNormalizer):
        res = numerical_expr_normalizer.process("本日10本目のお茶")
        expect = [NumericalExpression("10本目", 2, 6, 10, 10)]
        expect[0].counter = "本"
        expect[0].ordinary = True
        assert res == expect

    def test_process_han(self, numerical_expr_normalizer: NumericalExpressionNormalizer):
        res = numerical_expr_normalizer.process("お茶を1本半飲んだ")
        expect = [NumericalExpression("1本半", 3, 6, 1.5, 1.5)]
        expect[0].counter = "本"
        assert res == expect

    def test_process_per(self, numerical_expr_normalizer: NumericalExpressionNormalizer):
        res = numerical_expr_normalizer.process("１キロメートル／時")
        expect = [NumericalExpression("１キロメートル／時", 0, 9, 1000, 1000)]
        expect[0].counter = "m/h"
        assert res == expect

    def test_process_prefix_counter(self, numerical_expr_normalizer: NumericalExpressionNormalizer):
        res = numerical_expr_normalizer.process("それは¥100だ")
        expect = [NumericalExpression("¥100", 3, 7, 100, 100)]
        expect[0].counter = "円"
        assert res == expect

        res = numerical_expr_normalizer.process("それは時速40キロメートルだ")
        expect = [NumericalExpression("時速40キロメートル", 3, 13, 40000, 40000)]
        expect[0].counter = "m/h"
        assert res == expect

    def test_process_range(self, numerical_expr_normalizer: NumericalExpressionNormalizer):
        res = numerical_expr_normalizer.process("このアトラクションは3人～の運用になります")
        expect = [NumericalExpression("3人～", 10, 13, 3, 3)]
        expect[0].counter = "人"
        expect[0].options = ["kara_suffix"]
        assert res == expect

        res = numerical_expr_normalizer.process("遊び方の欄には「～8人」と書いてある")
        expect = [NumericalExpression("～8人", 8, 11, 8, 8)]
        expect[0].counter = "人"
        expect[0].options = ["kara_prefix"]
        assert res == expect

        res = numerical_expr_normalizer.process("遊び方の欄には「5～8人」と書いてある")
        expect = [NumericalExpression("5～8人", 8, 12, 5, 8)]
        expect[0].counter = "人"
        assert res == expect

        res = numerical_expr_normalizer.process("遊び方の欄には「5人～8人」と書いてある")
        expect = [NumericalExpression("5人～8人", 8, 13, 5, 8)]
        expect[0].counter = "人"
        assert res == expect

        res = numerical_expr_normalizer.process("時速50km～60km")
        expect = [NumericalExpression("時速50km～60km", 0, 11, 50000, 60000)]
        expect[0].counter = "m/h"
        assert res == expect

        res = numerical_expr_normalizer.process("時速50kmから時速60km")
        expect = [NumericalExpression("時速50kmから時速60km", 0, 14, 50000, 60000)]
        expect[0].counter = "m/h"
        assert res == expect

        res = numerical_expr_normalizer.process("時速50～60km")
        expect = [NumericalExpression("時速50～60km", 0, 9, 50000, 60000)]
        expect[0].counter = "m/h"
        assert res == expect

        res = numerical_expr_normalizer.process("世界50カ国から3000人が出席予定だ")
        expect = [NumericalExpression("50カ国から", 2, 8, 50, 50), NumericalExpression("から3000人", 6, 13, 3000, 3000)]
        expect[0].counter = "カ国"
        expect[0].options = ["kara_suffix"]
        expect[1].counter = "人"
        expect[1].options = ["kara_prefix"]
        assert res == expect

        res = numerical_expr_normalizer.process("およそ時速50km～60kmくらい")
        expect = [NumericalExpression("およそ時速50km～60kmくらい", 0, 17, 35000, 78000)]
        expect[0].counter = "m/h"
        assert res == expect

    def test_process_real(self, numerical_expr_normalizer: NumericalExpressionNormalizer):
        res = numerical_expr_normalizer.process("外国から30匹の鳥がきた")
        expect = [NumericalExpression("から30匹", 2, 7, 30, 30)]
        expect[0].counter = "匹"
        expect[0].options = ["kara_prefix"]
        assert res == expect

        res = numerical_expr_normalizer.process("数十人が十数人と喧嘩して、百数十円落とした")
        expect = [NumericalExpression("数十人", 0, 3, 10, 90), NumericalExpression("十数人", 4, 7, 11, 19),
                  NumericalExpression("百数十円", 13, 17, 110, 190)]
        expect[0].counter = "人"
        expect[1].counter = "人"
        expect[2].counter = "円"
        assert res == expect
