# flake8: noqa
import pytest

from pynormalizenumexp.expression.abstime import AbstimeExpression
from pynormalizenumexp.expression.base import INF, NNumber, NormalizedExpression, NTime
from pynormalizenumexp.normalizer.inappropriate_expr_remover import InappropriateExpressionRemover
from pynormalizenumexp.utility.dict_loader import DictLoader


@pytest.fixture(scope="class")
def inappropriate_expr_remover():
    return InappropriateExpressionRemover(DictLoader("ja"))


class TestInappropriateExpressionRemover:
    def test_delete_inappropriate_abstime_exprs(self, inappropriate_expr_remover: InappropriateExpressionRemover):
        exprs = [AbstimeExpression(NNumber("98年7月7日", 0, 7)), AbstimeExpression(NNumber("1.2.3", 0, 5))]
        exprs[0].value_lower_bound = NTime(INF)
        exprs[0].value_upper_bound = NTime(-INF)
        exprs[0].value_lower_bound.year = exprs[0].value_upper_bound.year = 98
        exprs[0].value_lower_bound.month = exprs[0].value_upper_bound.month = 7
        exprs[0].value_lower_bound.day = exprs[0].value_upper_bound.day = 7
        exprs[1].value_lower_bound = NTime(INF)
        exprs[1].value_upper_bound = NTime(-INF)
        exprs[1].value_lower_bound.year = exprs[1].value_upper_bound.year = 1
        exprs[1].value_lower_bound.month = exprs[1].value_upper_bound.month = 2
        exprs[1].value_lower_bound.day = exprs[1].value_upper_bound.day = 3
        res = inappropriate_expr_remover.delete_inappropriate_abstime_exprs(exprs)
        expect = [AbstimeExpression(NNumber("98年7月7日", 0, 7))]
        expect[0].value_lower_bound = NTime(INF)
        expect[0].value_upper_bound = NTime(-INF)
        expect[0].value_lower_bound.year = expect[0].value_upper_bound.year = 1998
        expect[0].value_lower_bound.month = expect[0].value_upper_bound.month = 7
        expect[0].value_lower_bound.day = expect[0].value_upper_bound.day = 7
        assert res == expect

    def test_delete_duplicate_extraction(self, inappropriate_expr_remover: InappropriateExpressionRemover):
        expr1 = [NormalizedExpression("", 2, 4), NormalizedExpression("", 6, 10)]
        expr2 = [NormalizedExpression("", 0, 2)]
        res = inappropriate_expr_remover.delete_duplicate_extraction(expr1, expr2)
        assert res == [NormalizedExpression("", 2, 4), NormalizedExpression("", 6, 10)]

        expr2 = [NormalizedExpression("", 0, 5)]
        res = inappropriate_expr_remover.delete_duplicate_extraction(expr1, expr2)
        assert res == [NormalizedExpression("", 6, 10)]

    def test_delete_inappropriate_extraction_using_dict(self, inappropriate_expr_remover: InappropriateExpressionRemover):
        exprs = [NormalizedExpression("九州", 0, 2)]
        res = inappropriate_expr_remover.delete_inappropriate_extraction_using_dict("九州に行く", exprs)
        assert res == []

        exprs = [NormalizedExpression("2.2", 3, 6)]
        res = inappropriate_expr_remover.delete_inappropriate_extraction_using_dict("ver2.2", exprs)
        assert res == []

        exprs = [NormalizedExpression("3g", 17, 19)]
        res = inappropriate_expr_remover.delete_inappropriate_extraction_using_dict("http://www.iphone3g.com", exprs)
        assert res == []

    def test_revise_abstime_expr(self, inappropriate_expr_remover: InappropriateExpressionRemover):
        expr = AbstimeExpression(NNumber("98年7月7日", 0, 7))
        expr.value_lower_bound = NTime(INF)
        expr.value_upper_bound = NTime(-INF)
        expr.value_lower_bound.year = expr.value_upper_bound.year = 98
        expr.value_lower_bound.month = expr.value_upper_bound.month = 7
        expr.value_lower_bound.day = expr.value_upper_bound.day = 7
        res = inappropriate_expr_remover.revise_abstime_expr(expr)
        assert res.value_lower_bound.year == 1998
        assert res.value_upper_bound.year == 1998

        expr = AbstimeExpression(NNumber("1.2.3", 0, 5))
        expr.value_lower_bound = NTime(INF)
        expr.value_upper_bound = NTime(-INF)
        expr.value_lower_bound.year = expr.value_upper_bound.year = 1
        expr.value_lower_bound.month = expr.value_upper_bound.month = 2
        expr.value_lower_bound.day = expr.value_upper_bound.day = 3
        res = inappropriate_expr_remover.revise_abstime_expr(expr)
        assert res is None

    def test_revise_year(self, inappropriate_expr_remover: InappropriateExpressionRemover):
        res = inappropriate_expr_remover.revise_year(AbstimeExpression(NNumber("西暦2021年", 0, 7)))
        assert res == AbstimeExpression(NNumber("西暦2021年", 0, 7))

        expr = AbstimeExpression(NNumber("98年7月7日", 0, 7))
        expr.value_lower_bound = NTime(INF)
        expr.value_upper_bound = NTime(-INF)
        expr.value_lower_bound.year = expr.value_upper_bound.year = 98
        expr.value_lower_bound.month = expr.value_upper_bound.month = 7
        expr.value_lower_bound.day = expr.value_upper_bound.day = 7
        res = inappropriate_expr_remover.revise_year(expr)
        assert res.value_lower_bound.year == 1998
        assert res.value_upper_bound.year == 1998

        expr = AbstimeExpression(NNumber("21年7月7日", 0, 7))
        expr.value_lower_bound = NTime(INF)
        expr.value_upper_bound = NTime(-INF)
        expr.value_lower_bound.year = expr.value_upper_bound.year = 21
        expr.value_lower_bound.month = expr.value_upper_bound.month = 7
        expr.value_lower_bound.day = expr.value_upper_bound.day = 7
        res = inappropriate_expr_remover.revise_year(expr)
        assert res.value_lower_bound.year == 2021
        assert res.value_upper_bound.year == 2021

    def test_is_inappropriate_time_value(self, inappropriate_expr_remover: InappropriateExpressionRemover):
        res = inappropriate_expr_remover.is_inappropriate_time_value(NTime(INF))
        assert res == False

        res = inappropriate_expr_remover.is_inappropriate_time_value(NTime(2021, 13, 1, 1, 0, 0))
        assert res == True

    def test_is_converted_by_other_type_expressions(self, inappropriate_expr_remover: InappropriateExpressionRemover):
        expr1 = NormalizedExpression("", 2, 4)
        expr2 = [NormalizedExpression("", 0, 2)]
        res = inappropriate_expr_remover.is_converted_by_other_type_expressions(expr1, expr2)
        assert res == False

        expr2 = [NormalizedExpression("", 1, 5)]
        res = inappropriate_expr_remover.is_converted_by_other_type_expressions(expr1, expr2)
        assert res == True
