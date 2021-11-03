import pytest

from pynormalizenumexp.expression.abstime import AbstimeExpression
from pynormalizenumexp.expression.base import INF, NNumber, NTime
from pynormalizenumexp.normalizer.abstime_expr_normalizer import AbstimeExpressionNormalizer
from pynormalizenumexp.utility.dict_loader import DictLoader


@pytest.fixture(scope="class")
def abstime_expr_normalizer():
    return AbstimeExpressionNormalizer(DictLoader("ja"))


class TestAbstimeExpressionNormalizer:
    def test_normalize_number(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        # NumberNormalizerの単体テストでカバーできているので特に何もしない
        pass

    def test_process(self, abstime_expr_normalizer: AbstimeExpressionNormalizer):
        res = abstime_expr_normalizer.process("午後3時")
        number = NNumber("午後3時", 0, 4)
        number.value_lower_bound = number.value_upper_bound = 3
        expect = [AbstimeExpression(number)]
        expect[0].value_lower_bound = NTime(value=INF)
        expect[0].value_lower_bound.hour = 15
        expect[0].value_upper_bound = NTime(value=-INF)
        expect[0].value_upper_bound.hour = 15
        expect[0].options = [""]
        assert res == expect

        res = abstime_expr_normalizer.process("あの人は1989年7月21日午前3時に生まれた")

        res = abstime_expr_normalizer.process("1989-7-21　1989.7.21　1989/7/21 １９８９．７．２１")
