# flake8: noqa
import pytest

from pynormalizenumexp.expression.abstime import AbstimePattern
from pynormalizenumexp.expression.base import NumberModifier
from pynormalizenumexp.utility.dict_loader import ChineseCharacter, DictLoader


@pytest.fixture(scope="class")
def dict_loader():
    return DictLoader("ja")


class TestDictLoader:
    def test_load_chinese_character_dict(self, dict_loader: DictLoader):
        res = dict_loader.load_chinese_character_dict("chinese_character.json")
        expect = ChineseCharacter(character="〇", value=0, notation_type="09")

        # 1番目の情報だけ見る
        assert res[0] == expect

    def test_load_limited_abstime_expr_dict(self, dict_loader: DictLoader):
        # 一例としてabstime_expression.jsonを読み込む
        res = dict_loader.load_limited_abstime_expr_dict("abstime_expression.json")
        expect = AbstimePattern()
        expect.pattern = "世紀"
        expect.corresponding_time_position = ["seiki"]
        expect.process_type = []
        expect.ordinary = False
        expect.option = ""

        # 1番目の情報だけ見る
        assert res[0] == expect

    def test_load_number_modifier_dict(self, dict_loader: DictLoader):
        # 一例としてabstime_prefix.jsonを読み込む
        res = dict_loader.load_number_modifier_dict("abstime_prefix.json")
        expect = NumberModifier(pattern="だいたい", process_type="about")

        # 1番目の情報だけ見る
        assert res[0] == expect
