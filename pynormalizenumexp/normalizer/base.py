"""各種ノーマライザの基底クラス定義モジュール."""
from copy import deepcopy
from typing import Dict, List, Optional, Tuple

from pynormalizenumexp.expression import (AbstimeExpression, LimitedExpression, NNumber,
                                          NumberModifier, NormalizedExpression)
from pynormalizenumexp.utility import DictLoader, NormalizerUtility


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

        self.limited_expressions: List[LimitedExpression] = []
        self.prefix_counters: List[LimitedExpression] = []
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

    def build_patterns(self, expressions: List[NormalizedExpression], reverse: bool = False) -> Dict[str, int]:
        """パターンオブジェクトからパターン文字列をパターンIDのマップを作成する.

        Parameters
        ----------
        expressions : List[NormalizedExpression]
            パターンオブジェクト
        reverse : bool, optional
            パターン文字列を逆さにするかどうかのフラグ, by default False

        Returns
        -------
        Dict[str, int]
            パターン文字列ごとのパターンIDのマップ
        """
        tmp_dict = dict()
        for i, expr in enumerate(expressions):
            if reverse:
                pattern = "".join(list(reversed(expr.pattern)))
            else:
                pattern = expr.pattern

            tmp_dict[pattern] = i

        return tmp_dict

    def process(self, text: str) -> List[NormalizedExpression]:
        # 数値表現を抽出
        numbers = self.normalize_number(text)

        # ベースとなるexpressionsを作成
        expressions = self.numbers2expressions(numbers)

        # 探索のためにテキスト中の数値文字列を * に置換する
        replaced_text = self.normalizer_utility.replace_numbers_in_text(text, numbers)

        # 単位の探索と正規化
        i = 0
        while i < len(expressions):
            normalized_id, new_expressions = self.normalize_limited_expression(replaced_text, expressions, i)
            if normalized_id == -1:
                # TODO 単位が存在しなかった場合の処理をどうするか要検討
                pass
            else:
                i = normalized_id
                expressions = new_expressions

            new_expression = self.normalize_prefix_counter(replaced_text, expressions[i])
            if new_expression is not None:
                expressions[i] = new_expression

    def normalize_number(self, text: str) -> List[NNumber]:
        """数値表現の抽出と正規化を行う."""
        raise NotImplementedError()

    def numbers2expressions(numbers: List[NNumber]) -> List[NormalizedExpression]:
        """数値表現を正規化済み表現に変換する."""
        raise NotImplementedError()

    def search_matching_limited_expression(self, replaced_text: str, expr: NormalizedExpression) -> int:
        after_text = replaced_text[expr.position_end:]
        matching_pattern_id = self.normalizer_utility.prefix_search(after_text, self.limited_expression_patterns)

        return matching_pattern_id

    def search_matching_prefix_counter(self, replaced_text: str, expr: NormalizedExpression) -> int:
        before_text = replaced_text[:expr.position_start]
        matching_pattern_id = self.normalizer_utility.suffix_search(before_text, self.prefix_counter_patterns)

        return matching_pattern_id

    def revise_expr_by_matching_limited_expression(self, exprs: List[NormalizedExpression],
                                                   expr_id: int,
                                                   matching_expr: NormalizedExpression) -> List[NormalizedExpression]:
        raise NotImplementedError()

    def revise_expr_by_matching_prefix_counter(self, expr: NormalizedExpression,
                                               matching_expr: LimitedExpression) -> NormalizedExpression:
        raise NotImplementedError()

    def revise_expr_by_number_modifier(self, expr: NormalizedExpression,
                                       number_modifier: NumberModifier) -> NormalizedExpression:
        raise NotImplementedError()

    def revise_expr_by_matching_prefix_number_modifier(self, expr: NormalizedExpression,
                                                       number_modifier: NumberModifier):
        new_expr = deepcopy(expr)
        new_expr.position_end -= len(number_modifier.pattern)

    def normalize_limited_expression(self, replaced_text: str,
                                     exprs: List[NormalizedExpression], expr_id: int) \
            -> Tuple[int, Optional[List[AbstimeExpression]]]:
        matching_pattern_id = self.search_matching_limited_expression(replaced_text, exprs[expr_id])
        if matching_pattern_id == -1:
            return -1, None

        new_exprs = self.revise_expr_by_matching_limited_expression(
            exprs, expr_id, self.limited_expressions[matching_pattern_id])

        return matching_pattern_id, new_exprs

    def normalize_prefix_counter(self, replaced_text: str, expr: NormalizedExpression) -> Optional[AbstimeExpression]:
        matching_pattern_id = self.search_matching_prefix_counter(replaced_text, expr)
        if matching_pattern_id == -1:
            return None

        new_expr = self.revise_expr_by_matching_prefix_counter(expr, self.prefix_counters[matching_pattern_id])

        return new_expr

    # def normalize_prefix_number_modifier(self, replaced_text: str, expr: NormalizedExpression):
    #     matching_pattern_id = self.normalizer_utility.search_prefix_number_modifier(
    #         replaced_text, expr.position_start, self.prefix_number_modifier_patterns)
