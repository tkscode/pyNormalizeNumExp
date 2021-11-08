import pytest

from pynormalizenumexp.expression.base import INF, NNumber, NTime
from pynormalizenumexp.expression.duration import DurationExpression
from pynormalizenumexp.normalizer.duration_expr_normalizer import DurationExpressionNormalizer
from pynormalizenumexp.utility.dict_loader import DictLoader


@pytest.fixture(scope="class")
def duration_expr_normalizer():
    return DurationExpressionNormalizer(DictLoader("ja"))


class TestDurationExpressionNormalizer:
    def test_process(self, duration_expr_normalizer: DurationExpressionNormalizer):
        res = duration_expr_normalizer.process("あの人は三時間も耐えた")
        expect = [DurationExpression(NNumber("三時間", 4, 7))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = expect[0].value_upper_bound.hour = 3
        assert res == expect

        res = duration_expr_normalizer.process("それは3年5ヶ月の間にも")
        expect = [DurationExpression(NNumber("3年5ヶ月", 3, 8))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 3
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 5
        assert res == expect

        res = duration_expr_normalizer.process("三年間と五ヶ月の間")
        expect = [DurationExpression(NNumber("三年間", 0, 3)), DurationExpression(NNumber("五ヶ月", 4, 7))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 3
        expect[1].org_value_lower_bound = expect[1].org_value_upper_bound = 5
        expect[1].value_lower_bound = NTime(INF)
        expect[1].value_upper_bound = NTime(-INF)
        expect[1].value_lower_bound.month = expect[1].value_upper_bound.month = 5
        assert res == expect

    def test_process_seiki(self, duration_expr_normalizer: DurationExpressionNormalizer):
        res = duration_expr_normalizer.process("あの人は三世紀も耐えた")
        expect = [DurationExpression(NNumber("三世紀", 4, 7))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 300
        assert res == expect

    def test_process_han(self, duration_expr_normalizer: DurationExpressionNormalizer):
        res = duration_expr_normalizer.process("あの人は三世紀半も耐えた")
        expect = [DurationExpression(NNumber("三世紀半", 4, 8))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 350
        assert res == expect

        res = duration_expr_normalizer.process("あの人は三時間半も耐えた")
        expect = [DurationExpression(NNumber("三時間半", 4, 8))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = expect[0].value_upper_bound.hour = 3.5
        assert res == expect

    def test_process_or_over(self, duration_expr_normalizer: DurationExpressionNormalizer):
        res = duration_expr_normalizer.process("あの人は三時間以上も耐えた")
        expect = [DurationExpression(NNumber("三時間以上", 4, 9))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = 3
        assert res == expect

    def test_process_about(self, duration_expr_normalizer: DurationExpressionNormalizer):
        res = duration_expr_normalizer.process("あの人は三時間くらいは耐えた")
        expect = [DurationExpression(NNumber("三時間くらい", 4, 10))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = 2
        expect[0].value_upper_bound.hour = 4
        assert res == expect

        res = duration_expr_normalizer.process("あの人はほぼ三時間は耐えた")
        expect = [DurationExpression(NNumber("ほぼ三時間", 4, 9))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = 2
        expect[0].value_upper_bound.hour = 4
        assert res == expect

    def test_process_kyou(self, duration_expr_normalizer: DurationExpressionNormalizer):
        res = duration_expr_normalizer.process("あの人は三時間強は耐えた")
        expect = [DurationExpression(NNumber("三時間強", 4, 8))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = 3
        expect[0].value_upper_bound.hour = 4
        assert res == expect

    def test_process_jaku(self, duration_expr_normalizer: DurationExpressionNormalizer):
        res = duration_expr_normalizer.process("あの人は三時間弱は耐えた")
        expect = [DurationExpression(NNumber("三時間弱", 4, 8))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.hour = 2
        expect[0].value_upper_bound.hour = 3
        assert res == expect
