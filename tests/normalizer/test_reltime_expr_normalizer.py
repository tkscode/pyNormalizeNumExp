import pytest

from pynormalizenumexp.expression.base import INF, NNumber, NTime
from pynormalizenumexp.expression.reltime import ReltimeExpression
from pynormalizenumexp.normalizer.reltime_expr_normalizer import ReltimeExpressionNormalizer
from pynormalizenumexp.utility.dict_loader import DictLoader


@pytest.fixture(scope="class")
def reltime_expr_normalizer():
    return ReltimeExpressionNormalizer(DictLoader("ja"))


class TestReltimeExpressionNormalizer:
    def test_process(self, reltime_expr_normalizer: ReltimeExpressionNormalizer):
        res = reltime_expr_normalizer.process("あの人は三時間前に生まれた")
        expect = [ReltimeExpression(NNumber("三時間前", 4, 8))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.hour = expect[0].value_upper_bound_rel.hour = -3
        assert res == expect

        res = reltime_expr_normalizer.process("それは3年5ヶ月後の出来事")
        expect = [ReltimeExpression(NNumber("3年5ヶ月後", 3, 9))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.year = expect[0].value_upper_bound_rel.year = 3
        expect[0].value_lower_bound_rel.month = expect[0].value_upper_bound_rel.month = 5
        assert res == expect

        res = reltime_expr_normalizer.process("今から36万年前………いや、1万4000年前だった")
        expect = [ReltimeExpression(NNumber("から36万年前", 1, 8)), ReltimeExpression(NNumber("1万4000年前", 14, 22))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 360000
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.year = expect[0].value_upper_bound_rel.year = -360000
        expect[0].options = ["kara_prefix"]
        expect[1].org_value_lower_bound = expect[1].org_value_upper_bound = 14000
        expect[1].value_lower_bound_rel = NTime(INF)
        expect[1].value_lower_bound_abs = NTime(INF)
        expect[1].value_upper_bound_rel = NTime(-INF)
        expect[1].value_upper_bound_abs = NTime(-INF)
        expect[1].value_lower_bound_rel.year = expect[1].value_upper_bound_rel.year = -14000
        assert res == expect

    def test_process_range(self, reltime_expr_normalizer: ReltimeExpressionNormalizer):
        res = reltime_expr_normalizer.process("1万年と2千年前からああああ")
        expect = [ReltimeExpression(NNumber("2千年前から", 4, 10))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 2000
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.year = expect[0].value_upper_bound_rel.year = -2000
        expect[0].options = ["kara_suffix"]
        assert res == expect

        res = reltime_expr_normalizer.process("1万2千年前から1億2千年後までああああ")
        expect = [ReltimeExpression(NNumber("1万2千年前から1億2千年後まで", 0, 16))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 12000
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.year = -12000
        expect[0].value_upper_bound_rel.year = 100002000
        expect[0].options = ["made"]
        assert res == expect

    def test_process_seiki(self, reltime_expr_normalizer: ReltimeExpressionNormalizer):
        res = reltime_expr_normalizer.process("二世紀前に起こった悲劇")
        expect = [ReltimeExpression(NNumber("二世紀前", 0, 4))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 2
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.year = expect[0].value_upper_bound_rel.year = -200
        assert res == expect

    def test_process_han(self, reltime_expr_normalizer: ReltimeExpressionNormalizer):
        res = reltime_expr_normalizer.process("二世紀半前に起こった悲劇")
        expect = [ReltimeExpression(NNumber("二世紀半前", 0, 5))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 2
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.year = expect[0].value_upper_bound_rel.year = -250
        assert res == expect

        res = reltime_expr_normalizer.process("あの人は三時間半前に生まれた")
        expect = [ReltimeExpression(NNumber("三時間半前", 4, 9))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.hour = expect[0].value_upper_bound_rel.hour = -3.5
        assert res == expect

    def test_process_prefix_counter(self, reltime_expr_normalizer: ReltimeExpressionNormalizer):
        res = reltime_expr_normalizer.process("それは昨年4月の出来事")
        expect = [ReltimeExpression(NNumber("昨年4月", 3, 7))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 4
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.year = expect[0].value_upper_bound_rel.year = -1
        expect[0].value_lower_bound_abs.month = expect[0].value_upper_bound_abs.month = 4
        assert res == expect

        res = reltime_expr_normalizer.process("来月三日にはできます")
        expect = [ReltimeExpression(NNumber("来月三日", 0, 4))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.month = expect[0].value_upper_bound_rel.month = 1
        expect[0].value_lower_bound_abs.day = expect[0].value_upper_bound_abs.day = 3
        assert res == expect

    def test_process_about(self, reltime_expr_normalizer: ReltimeExpressionNormalizer):
        res = reltime_expr_normalizer.process("およそ1000年前")
        expect = [ReltimeExpression(NNumber("およそ1000年前", 0, 9))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 1000
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.year = -1005
        expect[0].value_upper_bound_rel.year = -995
        assert res == expect

        res = reltime_expr_normalizer.process("約3ヶ月後")
        expect = [ReltimeExpression(NNumber("約3ヶ月後", 0, 5))]
        expect[0].org_value_lower_bound = expect[0].org_value_upper_bound = 3
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.month = 2
        expect[0].value_upper_bound_rel.month = 4
        assert res == expect

    def test_process_other(self, reltime_expr_normalizer: ReltimeExpressionNormalizer):
        res = reltime_expr_normalizer.process("それは4月の出来事")
        assert res == []

        res = reltime_expr_normalizer.process("来年")
        expect = [ReltimeExpression(NNumber("来年", 0, 2))]
        expect[0].value_lower_bound_rel = NTime(INF)
        expect[0].value_lower_bound_abs = NTime(INF)
        expect[0].value_upper_bound_rel = NTime(-INF)
        expect[0].value_upper_bound_abs = NTime(-INF)
        expect[0].value_lower_bound_rel.year = expect[0].value_upper_bound_rel.year = 1
        assert res == expect
