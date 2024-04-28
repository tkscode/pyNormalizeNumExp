"""辞書ファイルの読み込み定義モジュール."""
import json
import os
from dataclasses import dataclass
from enum import Enum
from importlib.resources import files
from typing import Optional

import pynormalizenumexp
from pynormalizenumexp.expression.abstime import AbstimePattern
from pynormalizenumexp.expression.base import NumberModifier
from pynormalizenumexp.expression.duration import DurationPattern
from pynormalizenumexp.expression.numerical import NumericalPattern
from pynormalizenumexp.expression.reltime import ReltimePattern

from .custom_type import (AbstimePatternDict, ChineseCharacterDict, DurationPatternDict, InappropriateStringDict, NumberModifierDict,
                          NumericalPatternDict, ReltimePatternDict)

BASE_DICT_PKG = "resources.dict"


@dataclass
class ChineseCharacter:
    """漢数字用クラス."""

    character: str
    value: int
    notation_type: str


class EnumExprType(str, Enum):
    """数値表現タイプ用クラス."""

    CHINESE_CHARACTER = "chinese_character"
    NUMBER_LIMITED = "number:limited"
    NUMBER_COUNTER = "number:counter"
    NUMBER_PREFIX_MODIFIER = "number:prefix_modifier"
    NUMBER_SUFFIX_MODIFIER = "number:suffix_modifier"
    ABSTIME_LIMITED = "abstime:limited"
    ABSTIME_COUNTER = "abstime:counter"
    ABSTIME_PREFIX_MODIFIER = "abstime:prefix_modifier"
    ABSTIME_SUFFIX_MODIFIER = "abstime:suffix_modifier"
    RELTIME_LIMITED = "reltime:limited"
    RELTIME_COUNTER = "reltime:counter"
    RELTIME_PREFIX_MODIFIER = "reltime:prefix_modifier"
    RELTIME_SUFFIX_MODIFIER = "reltime:suffix_modifier"
    DURATION_LIMITED = "duration:limited"
    DURATION_COUNTER = "duration:counter"
    DURATION_PREFIX_MODIFIER = "duration:prefix_modifier"
    DURATION_SUFFIX_MODIFIER = "duration:suffix_modifier"
    INAPPROPRIATE_STRING = "inappropriate_string"


class DictLoader(object):
    """辞書ファイルの読み込み定義クラス."""

    def __init__(self, language: str, custom_dict_file: Optional[str] = None) -> None:
        """コンストラクタ.

        Parameters
        ----------
        language : str
            利用言語（ja）
        custom_dict_file : Optional[str]
            カスタム辞書のファイルパス, default None
        """
        # TODO ja以外はエラーになるようにする
        self.language = language
        self.resouce_dirpath = str(files(f'{pynormalizenumexp.__package__}.{BASE_DICT_PKG}.{self.language}'))

        # カスタム辞書の読み込み
        if custom_dict_file:
            with open(custom_dict_file) as fp:
                self.custom_patterns = json.load(fp)
        else:
            self.custom_patterns = []

    def make_chinese_char_pattern(self, pattern: ChineseCharacterDict) -> ChineseCharacter:
        """漢数字パターンオブジェクトの生成.

        Parameters
        ----------
        pattern : ChineseCharacterDict
            漢数字パターン辞書データ

        Returns
        -------
        ChineseCharacter
            漢数字パターンオブジェクト
        """
        return ChineseCharacter(character=pattern["character"], value=pattern["value"],
                                notation_type=pattern["notation_type"])

    def make_counter_pattern(self, pattern: NumericalPatternDict) -> NumericalPattern:
        """時間系以外のパターンオブジェクトの生成.

        Parameters
        ----------
        pattern : NumericalPatternDict
            時間系以外のパターン辞書データ

        Returns
        -------
        NumericalPattern
            時間系以外のパターンオブジェクト
        """
        expr = NumericalPattern()
        expr.pattern = pattern["pattern"]
        expr.counter = pattern["counter"]
        expr.si_prefix = pattern["SI_prefix"]
        expr.optional_power_of_ten = pattern["optional_power_of_ten"]
        expr.ordinary = pattern["ordinary"]
        expr.option = pattern["option"]

        return expr

    def make_abstime_pattern(self, pattern: AbstimePatternDict) -> AbstimePattern:
        """絶対時間パターンオブジェクトの生成.

        Parameters
        ----------
        pattern : AbstimePatternDict
            絶対時間パターン辞書データ

        Returns
        -------
        AbstimePattern
            絶対時間パターンオブジェクト
        """
        expr = AbstimePattern()
        expr.pattern = pattern["pattern"]
        expr.corresponding_time_position = pattern["corresponding_time_position"]
        expr.process_type = pattern["process_type"]
        expr.ordinary = pattern["ordinary"]
        expr.option = pattern["option"]

        return expr

    def make_reltime_pattern(self, pattern: ReltimePatternDict) -> ReltimePattern:
        """相対時間パターンオブジェクトの生成.

        Parameters
        ----------
        pattern : ReltimePatternDict
            相対時間パターン辞書データ

        Returns
        -------
        ReltimePattern
            相対時間パターンオブジェクト
        """
        expr = ReltimePattern()
        expr.pattern = pattern["pattern"]
        expr.corresponding_time_position = pattern["corresponding_time_position"]
        expr.process_type = pattern["process_type"]
        expr.ordinary = pattern["ordinary"]
        expr.option = pattern["option"]

        return expr

    def make_duration_pattern(self, pattern: DurationPatternDict) -> DurationPattern:
        """期間パターンオブジェクトの生成.

        Parameters
        ----------
        pattern : DurationPatternDict
            期間パターン辞書データ

        Returns
        -------
        DurationPattern
            期間パターンオブジェクト
        """
        expr = DurationPattern()
        expr.pattern = pattern["pattern"]
        expr.corresponding_time_position = pattern["corresponding_time_position"]
        expr.process_type = pattern["process_type"]
        expr.ordinary = pattern["ordinary"]
        expr.option = pattern["option"]

        return expr

    def make_number_pattern(self, pattern: NumberModifierDict) -> NumberModifier:
        """各種表現のprefix/suffixパターンオブジェクトの生成.

        Parameters
        ----------
        pattern : NumberModifierDict
            各種表現のprefix/suffixパターン辞書データ

        Returns
        -------
        NumberModifier
            各種表現のprefix/suffixパターンオブジェクト
        """
        return NumberModifier(pattern["pattern"], pattern["process_type"])

    def make_inappropriate_pattern(self, pattern: InappropriateStringDict) -> str:
        """不適切な数値表現パターンオブジェクトの生成.

        Parameters
        ----------
        pattern : InappropriateStringDict
            不適切な数値表現パターン辞書データ

        Returns
        -------
        str
            不適切な数値表現パターンオブジェクト
        """
        return pattern["str"]

    def load_chinese_character_dict(self, dict_file: str) -> list[ChineseCharacter]:
        """漢数字辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名

        Returns
        -------
        list[ChineseCharacter]
            漢数字情報のリスト

        Notes
        -----
        * 漢数字はカスタム要素がないのでカスタム辞書の適用は行わない
        """
        with open(os.path.join(self.resouce_dirpath, dict_file)) as fp:
            characters: list[ChineseCharacterDict] = json.load(fp)["characters"]
            load_target = [self.make_chinese_char_pattern(char) for char in characters]

        return load_target

    def load_counter_expr_dict(self, dict_file: str, custom_expr_type: str) -> list[NumericalPattern]:
        """時間系以外のパターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名
        custom_expr_type : str
            カスタム辞書から抽出する表現タイプ

        Returns
        -------
        list[NumericalPattern]
            時間系以外のパターン情報のリスト
        """
        with open(os.path.join(self.resouce_dirpath, dict_file)) as fp:
            patterns: list[NumericalPatternDict] = json.load(fp)["patterns"]
            load_target = [self.make_counter_pattern(pattern) for pattern in patterns]

        # カスタム辞書にあるパターンを追加
        load_target += [self.make_counter_pattern(pattern["value"])
                        for pattern in filter(lambda x: x["expr_type"] == custom_expr_type, self.custom_patterns)]

        return load_target

    def load_limited_abstime_expr_dict(self, dict_file: str, custom_expr_type: str) -> list[AbstimePattern]:
        """絶対時間のパターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名
        custom_expr_type : str
            カスタム辞書から抽出する表現タイプ

        Returns
        -------
        list[AbstimePattern]
            絶対時間のパターン情報のリスト
        """
        with open(os.path.join(self.resouce_dirpath, dict_file)) as fp:
            patterns: list[AbstimePatternDict] = json.load(fp)["patterns"]
            load_target = [self.make_abstime_pattern(pattern) for pattern in patterns]

        # カスタム辞書にあるパターンを追加
        load_target += [self.make_abstime_pattern(pattern["value"])
                        for pattern in filter(lambda x: x["expr_type"] == custom_expr_type, self.custom_patterns)]

        return load_target

    def load_limited_reltime_expr_dict(self, dict_file: str, custom_expr_type: str) -> list[ReltimePattern]:
        """相対時間のパターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名
        custom_expr_type : str
            カスタム辞書から抽出する表現タイプ

        Returns
        -------
        list[ReltimePattern]
            相対時間のパターン情報のリスト
        """
        with open(os.path.join(self.resouce_dirpath, dict_file)) as fp:
            patterns: list[AbstimePatternDict] = json.load(fp)["patterns"]
            load_target = [self.make_reltime_pattern(pattern) for pattern in patterns]

        # カスタム辞書にあるパターンを追加
        load_target += [self.make_reltime_pattern(pattern["value"])
                        for pattern in filter(lambda x: x["expr_type"] == custom_expr_type, self.custom_patterns)]

        return load_target

    def load_limited_duration_expr_dict(self, dict_file: str, custom_expr_type: str) -> list[DurationPattern]:
        """期間のパターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名
        custom_expr_type : str
            カスタム辞書から抽出する表現タイプ

        Returns
        -------
        list[DurationPattern]
            期間のパターン情報のリスト
        """
        with open(os.path.join(self.resouce_dirpath, dict_file)) as fp:
            patterns: list[AbstimePatternDict] = json.load(fp)["patterns"]
            load_target = [self.make_duration_pattern(pattern) for pattern in patterns]

        # カスタム辞書にあるパターンを追加
        load_target += [self.make_duration_pattern(pattern["value"])
                        for pattern in filter(lambda x: x["expr_type"] == custom_expr_type, self.custom_patterns)]

        return load_target

    def load_number_modifier_dict(self, dict_file: str, custom_expr_type: str) -> list[NumberModifier]:
        """各種表現のprefix/suffixパターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名
        custom_expr_type : str
            カスタム辞書から抽出する表現タイプ

        Returns
        -------
        list[NumberModifier]
            各種表現のprefix/suffixパターン情報のリスト
        """
        with open(os.path.join(self.resouce_dirpath, dict_file)) as fp:
            patterns: list[NumberModifierDict] = json.load(fp)["patterns"]
            load_target = [self.make_number_pattern(pattern) for pattern in patterns]

        load_target += [self.make_number_pattern(pattern["value"])
                        for pattern in filter(lambda x: x["expr_type"] == custom_expr_type, self.custom_patterns)]

        # カスタム辞書にあるパターンを追加
        return load_target

    def load_inappropriate_strings_dict(self, dict_file: str) -> list[str]:
        """不適切な数値表現パターン辞書の読み込み.

        Parameters
        ----------
        dict_file : str
            辞書ファイル名

        Returns
        -------
        list[str]
            不適切な数値表現の文字列
        """
        with open(os.path.join(self.resouce_dirpath, dict_file)) as fp:
            strings: list[InappropriateStringDict] = json.load(fp)["strings"]
            load_target = [self.make_inappropriate_pattern(string) for string in strings]

        # カスタム辞書にあるパターンを追加
        load_target += [self.make_inappropriate_pattern(pattern["value"])
                        for pattern in filter(lambda x: x["expr_type"] == EnumExprType.INAPPROPRIATE_STRING, self.custom_patterns)]

        return load_target
