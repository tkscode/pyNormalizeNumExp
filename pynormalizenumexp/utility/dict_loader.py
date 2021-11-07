"""辞書ファイルの読み込み定義モジュール."""
import json
from dataclasses import dataclass
from importlib.resources import open_text
from typing import List

import pynormalizenumexp
from pynormalizenumexp.expression.abstime import AbstimePattern
from pynormalizenumexp.expression.base import NumberModifier
from pynormalizenumexp.expression.duration import DurationPattern
from pynormalizenumexp.expression.numerical import NumericalPattern
from pynormalizenumexp.expression.reltime import ReltimePattern

from .custom_type import (AbstimePatternDict, ChineseCharacterDict, DurationPatternDict, InappropriateStringDict,
                          NumberModifierDict, NumericalPatternDict, ReltimePatternDict)

BASE_DICT_PKG = "resources.dict"


@dataclass
class ChineseCharacter:
    """漢数字用クラス."""

    character: str
    value: int
    notation_type: str


class DictLoader(object):
    """辞書ファイルの読み込み定義クラス."""

    def __init__(self, language: str) -> None:
        """コンストラクタ.

        Parameters
        ----------
        language : str
            利用言語（ja | en）
        """
        # TODO ja, en, zh以外はエラーになるようにする
        self.language = language

    def load_chinese_character_dict(self, dict_file: str) -> List[ChineseCharacter]:
        """漢数字辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名

        Returns
        -------
        List[ChineseCharacter]
            漢数字情報のリスト
        """
        with open_text(f'{pynormalizenumexp.__package__}.{BASE_DICT_PKG}.{self.language}', dict_file) as fp:
            characters: List[ChineseCharacterDict] = json.load(fp)["characters"]
            load_target = [ChineseCharacter(character=char["character"], value=char["value"],
                                            notation_type=char["notation_type"]) for char in characters]

        return load_target

    def load_counter_expr_dict(self, dict_file: str) -> List[NumericalPattern]:
        """時間系以外のパターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名

        Returns
        -------
        List[NumericalPattern]
            時間系以外のパターン情報のリスト
        """
        def make_expression(pattern: NumericalPatternDict) -> NumericalPattern:
            expr = NumericalPattern()
            expr.pattern = pattern["pattern"]
            expr.counter = pattern["counter"]
            expr.si_prefix = pattern["SI_prefix"]
            expr.optional_power_of_ten = pattern["optional_power_of_ten"]
            expr.ordinary = pattern["ordinary"]
            expr.option = pattern["option"]

            return expr

        with open_text(f'{pynormalizenumexp.__package__}.{BASE_DICT_PKG}.{self.language}', dict_file) as fp:
            patterns: List[NumericalPatternDict] = json.load(fp)["patterns"]
            load_target = [make_expression(pattern) for pattern in patterns]

        return load_target

    def load_limited_abstime_expr_dict(self, dict_file: str) -> List[AbstimePattern]:
        """絶対時間のパターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名

        Returns
        -------
        List[AbstimePattern]
            絶対時間のパターン情報のリスト
        """
        def make_expression(pattern: AbstimePatternDict) -> AbstimePattern:
            expr = AbstimePattern()
            expr.pattern = pattern["pattern"]
            expr.corresponding_time_position = pattern["corresponding_time_position"]
            expr.process_type = pattern["process_type"]
            expr.ordinary = pattern["ordinary"]
            expr.option = pattern["option"]

            return expr

        with open_text(f'{pynormalizenumexp.__package__}.{BASE_DICT_PKG}.{self.language}', dict_file) as fp:
            patterns: List[AbstimePatternDict] = json.load(fp)["patterns"]
            load_target = [make_expression(pattern) for pattern in patterns]

        return load_target

    def load_limited_reltime_expr_dict(self, dict_file: str) -> List[ReltimePattern]:
        """相対時間のパターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名

        Returns
        -------
        List[ReltimePattern]
            相対時間のパターン情報のリスト
        """
        def make_expression(pattern: ReltimePatternDict) -> ReltimePattern:
            expr = ReltimePattern()
            expr.pattern = pattern["pattern"]
            expr.corresponding_time_position = pattern["corresponding_time_position"]
            expr.process_type = pattern["process_type"]
            expr.ordinary = pattern["ordinary"]
            expr.option = pattern["option"]

            return expr

        with open_text(f'{pynormalizenumexp.__package__}.{BASE_DICT_PKG}.{self.language}', dict_file) as fp:
            patterns: List[AbstimePatternDict] = json.load(fp)["patterns"]
            load_target = [make_expression(pattern) for pattern in patterns]

        return load_target

    def load_limited_duration_expr_dict(self, dict_file: str) -> List[DurationPattern]:
        """期間のパターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名

        Returns
        -------
        List[DurationPattern]
            期間のパターン情報のリスト
        """
        def make_expression(pattern: DurationPatternDict) -> DurationPattern:
            expr = DurationPattern()
            expr.pattern = pattern["pattern"]
            expr.corresponding_time_position = pattern["corresponding_time_position"]
            expr.process_type = pattern["process_type"]
            expr.ordinary = pattern["ordinary"]
            expr.option = pattern["option"]

            return expr

        with open_text(f'{pynormalizenumexp.__package__}.{BASE_DICT_PKG}.{self.language}', dict_file) as fp:
            patterns: List[AbstimePatternDict] = json.load(fp)["patterns"]
            load_target = [make_expression(pattern) for pattern in patterns]

        return load_target

    def load_number_modifier_dict(self, dict_file: str) -> List[NumberModifier]:
        """各種表現のprefix/suffixパターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名

        Returns
        -------
        List[NumberModifier]
            各種表現のprefix/suffixパターン情報のリスト
        """
        with open_text(f'{pynormalizenumexp.__package__}.{BASE_DICT_PKG}.{self.language}', dict_file) as fp:
            patterns: List[NumberModifierDict] = json.load(fp)["patterns"]
            load_target = [NumberModifier(pattern["pattern"], pattern["process_type"]) for pattern in patterns]

        return load_target

    def load_inappropriate_strings_dict(self, dict_file: str) -> List[str]:
        """不適切な数値表現パターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名

        Returns
        -------
        List[str]
            不適切な数値表現の文字列
        """
        with open_text(f'{pynormalizenumexp.__package__}.{BASE_DICT_PKG}.{self.language}', dict_file) as fp:
            strings: List[InappropriateStringDict] = json.load(fp)["strings"]
            load_target = [string["str"] for string in strings]

        return load_target
