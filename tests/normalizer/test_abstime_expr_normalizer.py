# flake8: noqa
import pytest

from pynormalizenumexp.expression.abstime import AbstimeExpression
from pynormalizenumexp.expression.base import INF, NNumber, NTime
from pynormalizenumexp.normalizer.abstime_expr_normalizer import AbstimeExpressionNormalizer
from pynormalizenumexp.utility.dict_loader import DictLoader


@pytest.fixture(scope="class")
def abstime_expr_normalizer():
    return AbstimeExpressionNormalizer(DictLoader("ja"))


class TestAbstimeExpressionNormalizer:
    def test_process(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("午後3時")
        number = NNumber("午後3時", 0, 4)
        number.value_lower_bound = number.value_upper_bound = 3
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = expect[0].value_upper_bound.hour = 15
        expect[0].options = [""]
        assert res == expect

        res = abstime_expr_normalizer.process("あの人は1989年7月21日午前3時に生まれた")
        numbers = [NNumber("1989年7月21日", 4, 14), NNumber("午前3時", 14, 18)]
        numbers[0].value_lower_bound = numbers[0].value_upper_bound = 1989
        numbers[1].value_lower_bound = numbers[1].value_upper_bound = 3
        expect = [AbstimeExpression(numbers[0]), AbstimeExpression(numbers[1])]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 1989
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 7
        expect[0].value_lower_bound.day = expect[0].value_upper_bound.day = 21
        expect[0].options = [""]
        expect[1].value_lower_bound = NTime(INF)
        expect[1].value_upper_bound = NTime(-INF)
        expect[1].value_lower_bound.hour = expect[1].value_upper_bound.hour = 3
        expect[1].options = [""]
        assert res == expect

        res = abstime_expr_normalizer.process("1989-7-21　1989.7.21　1989/7/21 １９８９．７．２１ 1989/07/21")
        numbers = [NNumber("1989-7-21", 0, 9), NNumber("1989.7.21", 10, 19),
                   NNumber("1989/7/21", 20, 29), NNumber("１９８９．７．２１", 30, 39),
                   NNumber("1989/07/21", 40, 50)]
        expect = []
        for number in numbers:
            number.value_lower_bound = number.value_upper_bound = 1989
            e = AbstimeExpression(number)
            e.value_lower_bound = NTime(INF)
            e.value_upper_bound = NTime(-INF)
            e.value_lower_bound.year = e.value_upper_bound.year = 1989
            e.value_lower_bound.month = e.value_upper_bound.month = 7
            e.value_lower_bound.day = e.value_upper_bound.day = 21
            e.options = [""]
            expect.append(e)
        assert res == expect

    def test_process_gogo(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("あの人は1989年7月21日午後3時に生まれた")
        numbers = [NNumber("1989年7月21日", 4, 14), NNumber("午後3時", 14, 18)]
        numbers[0].value_lower_bound = numbers[0].value_upper_bound = 1989
        numbers[1].value_lower_bound = numbers[1].value_upper_bound = 3
        expect = [AbstimeExpression(numbers[0]), AbstimeExpression(numbers[1])]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 1989
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 7
        expect[0].value_lower_bound.day = expect[0].value_upper_bound.day = 21
        expect[0].options = [""]
        expect[1].value_lower_bound = NTime(INF)
        expect[1].value_upper_bound = NTime(-INF)
        expect[1].value_lower_bound.hour = expect[1].value_upper_bound.hour = 15
        expect[1].options = [""]
        assert res == expect

    def test_process_gogo_han(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("あの人は午後3時半に生まれた")
        number = NNumber("午後3時半", 4, 9)
        number.value_lower_bound = number.value_upper_bound = 3
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = expect[0].value_upper_bound.hour = 15
        expect[0].value_lower_bound.minute = expect[0].value_upper_bound.minute = 30
        expect[0].options = [""]
        assert res == expect

    def test_process_seiki(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("あの人は18世紀に生まれた")
        number = NNumber("18世紀", 4, 8)
        number.value_lower_bound = number.value_upper_bound = 18
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = 1701
        expect[0].value_upper_bound.year = 1800
        expect[0].options = [""]
        assert res == expect

    def test_process_about(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("あの人は1989年7月21日ごろに生まれた")
        number = NNumber("1989年7月21日ごろ", 4, 16)
        number.value_lower_bound = number.value_upper_bound = 1989
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 1989
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 7
        expect[0].value_lower_bound.day = 20
        expect[0].value_upper_bound.day = 22
        expect[0].options = [""]
        assert res == expect

    def test_process_about(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("あの人は令和1年7月21日に生まれた")
        number = NNumber("令和1年7月21日", 4, 13)
        number.value_lower_bound = number.value_upper_bound = 1
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 2019
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 7
        expect[0].value_lower_bound.day = expect[0].value_upper_bound.day = 21
        expect[0].options = [""]
        assert res == expect

    def test_process_zenhan(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("あの人は18世紀前半に生まれた")
        number = NNumber("18世紀前半", 4, 10)
        number.value_lower_bound = number.value_upper_bound = 18
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = 1701
        expect[0].value_upper_bound.year = 1750
        expect[0].options = [""]
        assert res == expect

        res = abstime_expr_normalizer.process("あの人は7月3日朝に生まれた")
        number = NNumber("7月3日", 4, 8)
        number.value_lower_bound = number.value_upper_bound = 7
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 7
        expect[0].value_lower_bound.day = expect[0].value_upper_bound.day = 3
        expect[0].options = [""]
        assert res == expect

        res = abstime_expr_normalizer.process("あの人は７月上旬に生まれた")
        number = NNumber("７月上旬", 4, 8)
        number.value_lower_bound = number.value_upper_bound = 7
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 7
        expect[0].value_lower_bound.day = 1
        expect[0].value_upper_bound.day = 10
        expect[0].options = [""]
        assert res == expect

    def test_process_nakaba(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("あの人は18世紀半ばに生まれた")
        number = NNumber("18世紀半ば", 4, 10)
        number.value_lower_bound = number.value_upper_bound = 18
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = 1725
        expect[0].value_upper_bound.year = 1776
        expect[0].options = [""]
        assert res == expect

        res = abstime_expr_normalizer.process("あの人は７月中旬に生まれた")
        number = NNumber("７月中旬", 4, 8)
        number.value_lower_bound = number.value_upper_bound = 7
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 7
        expect[0].value_lower_bound.day = 11
        expect[0].value_upper_bound.day = 20
        expect[0].options = [""]
        assert res == expect

    def test_process_kouhan(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("あの人は18世紀後半に生まれた")
        number = NNumber("18世紀後半", 4, 10)
        number.value_lower_bound = number.value_upper_bound = 18
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = 1751
        expect[0].value_upper_bound.year = 1800
        expect[0].options = [""]
        assert res == expect

        res = abstime_expr_normalizer.process("あの人は７月下旬に生まれた")
        number = NNumber("７月下旬", 4, 8)
        number.value_lower_bound = number.value_upper_bound = 7
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 7
        expect[0].value_lower_bound.day = 21
        expect[0].value_upper_bound.day = 31
        expect[0].options = [""]
        assert res == expect

    def test_process_or_less(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("7月7日以前に、")
        number = NNumber("7月7日以前", 0, 6)
        number.value_lower_bound = number.value_upper_bound = 7
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_upper_bound.month = 7
        expect[0].value_upper_bound.day = 7
        expect[0].options = [""]
        assert res == expect

    def test_process_or_over(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("7月7日以降に、")
        number = NNumber("7月7日以降", 0, 6)
        number.value_lower_bound = number.value_upper_bound = 7
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.month = 7
        expect[0].value_lower_bound.day = 7
        expect[0].options = [""]
        assert res == expect

    def test_process_range(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("15時〜18時の間に、")
        number = NNumber("15時〜18時", 0, 7)
        number.value_lower_bound = number.value_upper_bound = 15
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = 15
        expect[0].value_upper_bound.hour = 18
        expect[0].options = ["", ""]
        assert res == expect

        res = abstime_expr_normalizer.process("15:00から18:00の間に、")
        number = NNumber("15:00から18:00", 0, 12)
        number.value_lower_bound = number.value_upper_bound = 15
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = 15
        expect[0].value_upper_bound.hour = 18
        expect[0].value_lower_bound.minute = expect[0].value_upper_bound.minute = 0
        expect[0].options = ["", ""]
        assert res == expect

        res = abstime_expr_normalizer.process("15~18時の間に、")
        number = NNumber("15~18時", 0, 6)
        number.value_lower_bound = number.value_upper_bound = 15
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = 15
        expect[0].value_upper_bound.hour = 18
        expect[0].options = [""]
        assert res == expect

        res = abstime_expr_normalizer.process("2012/3/8~3/10の間に、")
        number = NNumber("2012/3/8~3/10", 0, 13)
        number.value_lower_bound = number.value_upper_bound = 2012
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 2012
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 3
        expect[0].value_lower_bound.day = 8
        expect[0].value_upper_bound.day = 10
        expect[0].options = ["", ""]
        assert res == expect

    def test_process_ambiguous(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("2021.11")
        number = NNumber("2021.11", 0, 7)
        number.value_lower_bound = number.value_upper_bound = 2021
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 2021
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 11
        expect[0].options = [""]
        assert res == expect

        res = abstime_expr_normalizer.process("11.3")
        number = NNumber("11.3", 0, 4)
        number.value_lower_bound = number.value_upper_bound = 11
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 11
        expect[0].value_lower_bound.day = expect[0].value_upper_bound.day = 3
        expect[0].options = [""]
        assert res == expect
