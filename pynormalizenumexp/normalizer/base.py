"""各種ノーマライザの基底クラス定義モジュール."""
from copy import deepcopy
from typing import Dict, List, Optional, Sequence, Tuple, Union

from pynormalizenumexp.expression.base import BasePattern, NNumber, NormalizedExpression, NumberModifier
from pynormalizenumexp.utility.dict_loader import DictLoader
from pynormalizenumexp.utility.normalizer_utility import NormalizerUtility


class BaseNormalizer(object):
    """各種ノーマライザの基底クラス."""

    def __init__(self, dict_loader: DictLoader) -> None:
        """コンストラクタ.

        Parameters
        ----------
        dict_loader : DictLoader
            辞書ファイルのローダー
        """
        self.dict_loader = dict_loader
        self.normalizer_utility = NormalizerUtility()

        self.limited_expressions: Sequence[BasePattern] = []
        self.prefix_counters: Sequence[BasePattern] = []
        self.prefix_number_modifier: List[NumberModifier] = []
        self.suffix_number_modifier: List[NumberModifier] = []

        self.limited_expression_patterns: Dict[str, int] = dict()
        self.prefix_counter_patterns: Dict[str, int] = dict()
        self.prefix_number_modifier_patterns: Dict[str, int] = dict()
        self.suffix_number_modifier_patterns: Dict[str, int] = dict()

    def load_dictionaries(self, limited_expr_dict_path: str, prefix_counter_dict_path: str,
                          prefix_number_modifier_dict_path: str, suffix_number_modifier_dict_path: str) -> None:
        """辞書ファイルの読み込み."""
        raise NotImplementedError()

    def build_patterns(self, expressions: Sequence[Union[BasePattern, NormalizedExpression]]) -> Dict[str, int]:
        """パターンオブジェクトからパターン文字列をパターンIDのマップを作成する.

        Parameters
        ----------
        expressions : Sequence[Union[BasePattern, NormalizedExpression]]
            パターンオブジェクト

        Returns
        -------
        Dict[str, int]
            パターン文字列ごとのパターンIDのマップ
        """
        return {expr.pattern: i for i, expr in enumerate(expressions)}

    def process(self, text: str) -> List[NormalizedExpression]:
        """数値表現の抽出を正規化を行う.

        Parameters
        ----------
        text : str
            抽出・正規化対象のテキスト

        Returns
        -------
        List[NormalizedExpression]
            正規化済みの数値表現
        """
        # 数値表現を抽出
        numbers = self.normalize_number(text)

        # 抽出した数値表現を適切な表現（絶対時間など）に変換
        expressions = self.numbers2expressions(numbers)

        # 探索のためにテキスト中の数値文字列を * に置換する
        replaced_text = self.normalizer_utility.replace_numbers_in_text(text, numbers)

        # 単位の探索と正規化
        i = 0
        while i < len(expressions):
            # 変換済みの数値表現を正規化する
            normalized_id, new_expressions = self.normalize_limited_expression(replaced_text, expressions, i)
            if new_expressions is None:
                # TODO 単位が存在しなかった場合の処理をどうするか要検討
                pass
            else:
                i = normalized_id
                expressions = new_expressions

            new_expression = self.normalize_prefix_counter(replaced_text, expressions[i])
            if new_expression:
                expressions[i] = new_expression

            new_expression = self.normalize_suffix_number_modifier(replaced_text, expressions[i])
            if new_expression:
                expressions[i] = new_expression

            new_expression = self.normalize_prefix_number_modifier(replaced_text, expressions[i])
            if new_expression:
                expressions[i] = new_expression
                new_expression = self.normalize_prefix_counter(replaced_text, expressions[i])
                if new_expression:
                    expressions[i] = new_expression

            expressions[i].set_original_expr_from_position(text)

            i += 1

        # 範囲表現の処理
        expressions = self.fix_by_range_expression(text, expressions)

        # 「から」表現の修正
        expressions = self.fix_kara_expression(expressions)

        # 規格化されなかったnumberを削除
        expressions = self.delete_not_expression(expressions)

        return expressions

    def normalize_number(self, text: str) -> List[NNumber]:
        """テキストから数値表現を抽出する."""
        raise NotImplementedError()

    def numbers2expressions(self, numbers: List[NNumber]) -> List[NormalizedExpression]:
        """数値表現を適切な表現（絶対時間など）に変換する."""
        raise NotImplementedError()

    def search_matching_limited_expression(self, replaced_text: str, expr: NormalizedExpression) -> int:
        """テキスト中にどの表現パターンが出現するか検索する.

        Parameters
        ----------
        replaced_text : str
            数値文字列がマスクされた元のテキスト
        expr : NormalizedExpression
            抽出された数値表現

        Returns
        -------
        int
            表現パターンのID

        Notes
        -----
            「2021年」の「2021」が数値表現として抽出されているので、それに続く「年」という表現が辞書中にあるか調べているイメージ
        """
        after_text = replaced_text[expr.position_end:]
        matching_pattern_id = self.normalizer_utility.search_pattern(after_text,
                                                                     self.limited_expression_patterns, "prefix")

        return matching_pattern_id

    def search_matching_prefix_counter(self, replaced_text: str, expr: NormalizedExpression) -> int:
        """数値表現の直前に出現する単位表現を検索する.

        Parameters
        ----------
        replaced_text : str
            数値文字列がマスクされた元のテキスト
        expr : NormalizedExpression
            抽出された数値表現

        Returns
        -------
        int
            見つかった単位表現パターンのID
        """
        before_text = replaced_text[:expr.position_start]
        matching_pattern_id = self.normalizer_utility.search_pattern(before_text,
                                                                     self.prefix_counter_patterns, "suffix")

        return matching_pattern_id

    def revise_expr_by_matching_limited_expression(self, exprs: Sequence[NormalizedExpression], expr_id: int,
                                                   matching_expr: BasePattern) \
            -> List[NormalizedExpression]:
        """マッチした数値表現の補正を行う."""
        raise NotImplementedError()

    def revise_expr_by_matching_prefix_counter(self, expr: NormalizedExpression,
                                               matching_expr: BasePattern) -> NormalizedExpression:
        """マッチした単位表現から数値表現の補正を行う."""
        raise NotImplementedError()

    def revise_expr_by_number_modifier(self, expr: NormalizedExpression,
                                       number_modifier: NumberModifier) -> NormalizedExpression:
        """マッチした修飾表現から数値表現の補正を行う."""
        raise NotImplementedError()

    def revise_expr_by_matching_prefix_number_modifier(self, expr: NormalizedExpression,
                                                       number_modifier: NumberModifier) -> NormalizedExpression:
        """数値表現の前にあるマッチした修飾表現から数値表現の補正を行う.

        Parameters
        ----------
        expr : NormalizedExpression
            抽出された数値表現
        number_modifier : NumberModifier
            マッチした修飾表現

        Returns
        -------
        NormalizedExpression
            補正後の数値表現
        """
        new_expr = deepcopy(expr)
        new_expr.position_start -= len(number_modifier.pattern)

        new_expr = self.revise_expr_by_number_modifier(new_expr, number_modifier)

        return new_expr

    def revise_expr_by_matching_suffix_number_modifier(self, expr: NormalizedExpression,
                                                       number_modifier: NumberModifier) -> NormalizedExpression:
        """数値表現の後にあるマッチした修飾表現から数値表現の補正を行う.

        Parameters
        ----------
        expr : NormalizedExpression
            抽出された数値表現
        number_modifier : NumberModifier
            マッチした修飾表現

        Returns
        -------
        NormalizedExpression
            補正後の数値表現
        """
        new_expr = deepcopy(expr)
        new_expr.position_end += len(number_modifier.pattern)

        new_expr = self.revise_expr_by_number_modifier(new_expr, number_modifier)

        return new_expr

    def normalize_limited_expression(self, replaced_text: str,
                                     exprs: Sequence[NormalizedExpression], expr_id: int) \
            -> Tuple[int, Optional[List[NormalizedExpression]]]:
        """抽出された数値表現の正規化.

        Parameters
        ----------
        replaced_text : str
            数値文字列がマスクされた元のテキスト
        exprs : List[NormalizedExpression]
            抽出された数値表現
        expr_id : int
            どの数値表現に着目するかのID（インデックス）

        Returns
        -------
        Tuple[int, Optional[List[NormalizedExpression]]]
            マッチしたパターン辞書のIDと正規化された数値表現（マッチするものがなければNoneを返す）
        """
        # どの表現パターンにマッチするか検索する
        matching_pattern_id = self.search_matching_limited_expression(replaced_text, exprs[expr_id])
        if matching_pattern_id == -1:
            # マッチするものがなければIDは-1、正規化済みの数値表現はNoneで返す
            return -1, None

        # マッチした表現パターンに応じて数値表現を補正する
        new_exprs = self.revise_expr_by_matching_limited_expression(
            exprs, expr_id, self.limited_expressions[matching_pattern_id])

        return expr_id, new_exprs

    def normalize_prefix_counter(self, replaced_text: str, expr: NormalizedExpression) \
            -> Optional[NormalizedExpression]:
        """数値表現の直前に出現する単位表現の正規化.

        Parameters
        ----------
        replaced_text : str
            数値文字列がマスクされた元のテキスト
        expr : NormalizedExpression
            抽出された数値表現

        Returns
        -------
        Optional[AbstimeExpression]
            正規化された単位表現（マッチする単位表現がない場合はNone）

        Notes
        -----
            単位表現：毎週や北緯、摂氏など
        """
        matching_pattern_id = self.search_matching_prefix_counter(replaced_text, expr)
        if matching_pattern_id == -1:
            return None

        return self.revise_expr_by_matching_prefix_counter(expr, self.prefix_counters[matching_pattern_id])

    def normalize_prefix_number_modifier(self, replaced_text: str, expr: NormalizedExpression) \
            -> Optional[NormalizedExpression]:
        """数値表現の直前に出現する修飾表現の正規化.

        Parameters
        ----------
        replaced_text : str
            数値文字列がマスクされた元のテキスト
        expr : NormalizedExpression
            抽出された数値表現

        Returns
        -------
        Optional[NormalizedExpression]
            正規化された修飾表現（マッチする修飾表現がなければNone）
        """
        matching_pattern_id = self.normalizer_utility.search_prefix_number_modifier(
            replaced_text, expr.position_start, self.prefix_number_modifier_patterns)
        if matching_pattern_id == -1:
            return None

        return self.revise_expr_by_matching_prefix_number_modifier(
            expr, self.prefix_number_modifier[matching_pattern_id])

    def normalize_suffix_number_modifier(self, replaced_text: str, expr: NormalizedExpression) \
            -> Optional[NormalizedExpression]:
        """数値表現の直後に出現する修飾表現の正規化.

        Parameters
        ----------
        replaced_text : str
            数値文字列がマスクされた元のテキスト
        expr : NormalizedExpression
            抽出された数値表現

        Returns
        -------
        Optional[NormalizedExpression]
            正規化された修飾表現（マッチする修飾表現がなければNone）
        """
        matching_pattern_id = self.normalizer_utility.search_suffix_number_modifier(
            replaced_text, expr.position_end, self.suffix_number_modifier_patterns)
        if matching_pattern_id == -1:
            return None

        return self.revise_expr_by_matching_suffix_number_modifier(
            expr, self.suffix_number_modifier[matching_pattern_id])

    def fix_by_range_expression(self, text: str, exprs: Sequence[NormalizedExpression]) \
            -> List[NormalizedExpression]:
        """範囲表現の修正を行う."""
        raise NotImplementedError()

    def delete_not_expression(self, exprs: Sequence[NormalizedExpression]) -> List[NormalizedExpression]:
        """特定条件下の数値表現を削除する."""
        raise NotImplementedError()

    def fix_kara_expression(self, exprs: List[NormalizedExpression]) -> List[NormalizedExpression]:
        """「から」表現のみがついてしまうのを修正する.

        Parameters
        ----------
        exprs : List[NormalizedExpression]
            抽出された数値表現

        Returns
        -------
        List[NormalizedExpression]
            修正後の数値表現
        """
        new_exprs = deepcopy(exprs)
        for i, expr in enumerate(new_exprs):
            if expr.original_expr.startswith("から"):
                expr.original_expr = expr.original_expr[2:]
                expr.position_start += 2
                # optionsに入っているkara_prefixを削除
                del(expr.options[0])
            elif expr.original_expr.endswith("から"):
                expr.original_expr = expr.original_expr[:-2]
                expr.position_end -= 2
                # optionsに入っているkara_suffixを削除
                del(expr.options[-1])

            new_exprs[i] = expr

        return new_exprs

    def have_kara_prefix(self, options: List[str]) -> bool:
        """抽出した数値表現のオプションに kara_prefix が含まれているかをチェックする.

        Parameters
        ----------
        options : List[str]
            チェック対象のオプション

        Returns
        -------
        bool
            True：含まれている、False：含まれていない
        """
        return "kara_prefix" in options

    def have_kara_suffix(self, options: List[str]) -> bool:
        """抽出した数値表現のオプションに kara_suffix が含まれているかをチェックする.

        Parameters
        ----------
        options : List[str]
            チェック対象のオプション

        Returns
        -------
        bool
            True：含まれている、False：含まれていない
        """
        return "kara_suffix" in options

    def merge_options(self, options1: List[str], options2: List[str]) -> List[str]:
        """範囲表現のオプションをマージする.

        Parameters
        ----------
        options1 : List[str]
            片方の範囲表現のオプション
        options2 : List[str]
            もう片方の範囲表現のオプション

        Returns
        -------
        List[str]
            マージしたオプション
        """
        # TODO kara_suffixを全部削除して良いかどうかは要検討
        new_options = list(filter(lambda x: x != "kara_suffix", options1))
        new_options += list(filter(lambda x: x != "kara_prefix", options2))

        return new_options
