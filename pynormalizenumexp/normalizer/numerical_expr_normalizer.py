"""時間系以外の数値表現の抽出・正規化処理を定義するモジュール."""
from copy import deepcopy
from typing import List

from pynormalizenumexp.expression.base import INF, NumberModifier
from pynormalizenumexp.expression.numerical import NumericalExpression, NumericalPattern
from pynormalizenumexp.utility.dict_loader import DictLoader

from .base import BaseNormalizer, NNumber
from .number_normalizer import NumberNormalizer


class NumericalExpressionNormalizer(BaseNormalizer):
    """時間系以外の数値表現の抽出・正規化を行うクラス."""

    def __init__(self, dict_loader: DictLoader) -> None:
        """コンストラクタ.

        Parameters
        ----------
        dict_loader : DictLoader
            辞書ファイルのローダー
        """
        super().__init__(dict_loader)

        self.number_normalizer = NumberNormalizer(dict_loader)

        self.load_dictionaries("num_counter.json", "num_prefix_counter.json",
                               "num_prefix.json", "num_suffix.json")

    def load_dictionaries(self, limited_expr_dict_file: str, prefix_counter_dict_file: str,
                          prefix_number_modifier_dict_file: str, suffix_number_modifier_dict_file: str) -> None:
        """辞書ファイルの読み込み.

        Parameters
        ----------
        limited_expr_dict_file : str
            時間系以外の数値表現パターンを定義した辞書ファイル名
        prefix_counter_dict_file : str
            接頭表現（単位や年代など）を定義した辞書ファイル名
        prefix_number_modifier_dict_file : str
            接尾表現（範囲表現）を定義した辞書ファイル名
        suffix_number_modifier_dict_file : str
            接尾表現を定義した辞書ファイル名
        """
        self.limited_expressions = self.dict_loader.load_counter_expr_dict(limited_expr_dict_file)
        self.prefix_counters = self.dict_loader.load_counter_expr_dict(prefix_counter_dict_file)
        self.prefix_number_modifier = self.dict_loader.load_number_modifier_dict(prefix_number_modifier_dict_file)
        self.suffix_number_modifier = self.dict_loader.load_number_modifier_dict(suffix_number_modifier_dict_file)

        self.limited_expression_patterns = self.build_patterns(self.limited_expressions)
        self.prefix_counter_patterns = self.build_patterns(self.prefix_counters)
        self.prefix_number_modifier_patterns = self.build_patterns(self.prefix_number_modifier)
        self.suffix_number_modifier_patterns = self.build_patterns(self.suffix_number_modifier)

        for expr in self.limited_expressions:
            expr.set_total_number_of_place_holder()
            expr.set_len_of_after_final_place_holder()

    def normalize_number(self, text: str) -> List[NNumber]:
        """テキストから数値表現を抽出する.

        Parameters
        ----------
        text : str
            抽出対象のテキスト

        Returns
        -------
        List[NNumber]
            抽出した数値表現
        """
        return self.number_normalizer.process(text)

    def numbers2expressions(self, numbers: List[NNumber]) -> List[NumericalExpression]:  # type: ignore[override]
        """抽出した数値表現を変換する.

        Parameters
        ----------
        numbers : List[NNumber]
            抽出した数値表現

        Returns
        -------
        List[NumericalExpression]
            変換後のオブジェクト
        """
        return [NumericalExpression(number) for number in numbers]

    def revise_expr_by_matching_limited_expression(self, exprs: List[NumericalExpression],  # type: ignore[override]
                                                   expr_id: int,
                                                   matching_expr: NumericalPattern) -> List[NumericalExpression]:
        """マッチした数値表現の補正を行う.

        Parameters
        ----------
        exprs : List[NumericalExpression]
            抽出された数値表現
        expr_id : int
            どの数値表現に着目するかのID（インデックス）
        matching_expr : NumericalPattern
            マッチした表現辞書パターン

        Returns
        -------
        List[NumericalExpression]
            補正済みの数値表現
        """
        # 特殊なタイプをここで例外処理
        if matching_expr.option == "wari":
            return self.do_option_wari(exprs, expr_id, matching_expr)

        # TODO : 今のところ特殊なタイプは分数しかないので、とりあえず保留

        new_exprs = deepcopy(exprs)
        new_exprs[expr_id].position_end += len(matching_expr.pattern)
        new_exprs[expr_id].counter = matching_expr.counter
        new_exprs[expr_id] = self.multiply_numexp_value(new_exprs[expr_id], 10 ** matching_expr.si_prefix)
        new_exprs[expr_id] = self.multiply_numexp_value(new_exprs[expr_id], 10 ** matching_expr.optional_power_of_ten)
        new_exprs[expr_id].ordinary = matching_expr.ordinary

        return new_exprs

    def do_option_wari(self, num_exprs: List[NumericalExpression], expr_id: int, matching_expr: NumericalPattern) \
            -> List[NumericalExpression]:
        """日本語の割合表記の補正を行う.

        Parameters
        ----------
        num_exprs : List[NumericalExpression]
            抽出された数値表現
        expr_id : int
            どの数値表現に着目するかのID（インデックス）
        matching_expr : NumericalPattern
            マッチした表現辞書パターン

        Returns
        -------
        List[NumericalExpression]
            補正済みの数値表現
        """
        new_num_exprs = deepcopy(num_exprs)
        new_num_exprs[expr_id].position_end += len(matching_expr.pattern)
        new_num_exprs[expr_id].counter = "%"
        new_num_exprs[expr_id].ordinary = False

        value = 0.0
        for i in range(0, len(matching_expr.pattern), 2):
            char = matching_expr.pattern[i]
            if char == "割":
                value += num_exprs[expr_id+i//2].value_lower_bound * 10
            elif char == "分":
                value += num_exprs[expr_id+i//2].value_lower_bound * 1
            elif char == "厘":
                value += num_exprs[expr_id+i//2].value_lower_bound * 0.1
            else:
                pass

        new_num_exprs[expr_id].value_lower_bound = new_num_exprs[expr_id].value_upper_bound = value

        # マージした表現を削除する
        for _ in range(2, len(matching_expr.pattern), 2):
            del(new_num_exprs[expr_id+1])

        return new_num_exprs

    def revise_expr_by_matching_prefix_counter(self, expr: NumericalExpression,  # type: ignore[override]
                                               matching_expr: NumericalPattern) -> NumericalExpression:
        """マッチした単位表現から数値表現の補正を行う.

        Parameters
        ----------
        expr : NumericalExpression
            抽出された数値表現
        matching_expr : NumericalPattern
            マッチした表現辞書パターン

        Returns
        -------
        NumericalExpression
            補正済みの数値表現
        """
        new_expr = deepcopy(expr)
        if matching_expr.option == "counter":
            new_expr.position_start -= len(matching_expr.pattern)
            new_expr.counter = matching_expr.counter
            new_expr = self.multiply_numexp_value(new_expr, 10 ** matching_expr.si_prefix)
            new_expr = self.multiply_numexp_value(new_expr, 10 ** matching_expr.optional_power_of_ten)
            new_expr.ordinary = matching_expr.ordinary
        elif matching_expr.option == "add_suffix_counter":
            if len(new_expr.counter) == 0:
                return new_expr

            new_expr.position_start -= len(matching_expr.pattern)
            new_expr.counter += matching_expr.counter

        return new_expr

    def revise_expr_by_number_modifier(self, expr: NumericalExpression,  # type: ignore[override] # noqa: C901
                                       number_modifier: NumberModifier) -> NumericalExpression:
        """マッチした修飾表現から数値表現の補正を行う.

        Parameters
        ----------
        expr : NumericalExpression
            抽出された数値表現
        number_modifier : NumberModifier
            マッチした修飾表現

        Returns
        -------
        NumericalExpression
            補正後の数値表現
        """
        new_expr = deepcopy(expr)
        if number_modifier.process_type == "or_over":
            new_expr.value_upper_bound = INF
        elif number_modifier.process_type == "or_less":
            new_expr.value_lower_bound = -INF
        elif number_modifier.process_type == "over":
            new_expr.value_upper_bound = INF
            new_expr.include_lower_bound = False
        elif number_modifier.process_type == "less":
            new_expr.value_lower_bound = -INF
            new_expr.include_upper_bound = False
        elif number_modifier.process_type == "ordinary":
            new_expr.ordinary = True
        elif number_modifier.process_type == "han":
            new_expr.value_lower_bound += 0.5
            new_expr.value_upper_bound += 0.5
        elif number_modifier.process_type[0] == "/":
            new_expr.counter += number_modifier.process_type
        elif number_modifier.process_type == "about":
            new_expr.value_lower_bound *= 0.7
            new_expr.value_upper_bound *= 1.3
        elif number_modifier.process_type == "kyou":
            new_expr.value_upper_bound *= 1.6
        elif number_modifier.process_type == "jaku":
            new_expr.value_lower_bound *= 0.5
        elif number_modifier.process_type == "made":
            if new_expr.value_upper_bound == new_expr.value_lower_bound:
                new_expr.value_lower_bound = -INF
            else:
                pass
        elif number_modifier.process_type == "dai":
            # TODO : どんな処理をするか未定。。 該当する事例は「30代」「9秒台」のみ？
            pass
        elif number_modifier.process_type == "per":
            # TODO : どんな処理をするか未定。 該当する事例は「1ページ毎」など。
            pass
        elif number_modifier.process_type == "none":
            pass
        else:
            new_expr.options.append(number_modifier.process_type)

        return new_expr

    def delete_not_expression(self,  # type: ignore[override]
                              exprs: List[NumericalExpression]) -> List[NumericalExpression]:
        """数値表現が空のものを削除する.

        Parameters
        ----------
        exprs : List[NumericalExpression]
            抽出された数値表現表現

        Returns
        -------
        List[NumericalExpression]
            削除後の数値表現表現
        """
        for i in range(len(exprs)):
            if len(exprs[i].counter) == 0:
                exprs[i] = None  # type: ignore

        return [expr for expr in exprs if expr]

    def fix_by_range_expression(self,  # type: ignore[override]
                                text: str, exprs: List[NumericalExpression]) -> List[NumericalExpression]:
        """数値の範囲表現の修正を行う.

        Parameters
        ----------
        text : str
            元のテキスト
        exprs : List[NumericalExpression]
            抽出された数値表現

        Returns
        -------
        List[NumericalExpression]
            修正後の数値表現
        """
        for i in range(len(exprs) - 1):
            if exprs[i] is None \
                    or not self.have_kara_suffix(exprs[i].options) \
                    or not self.have_kara_prefix(exprs[i+1].options) \
                    or exprs[i].position_end + 2 < exprs[i+1].position_start:
                continue

            if not self.match_counter_suffix(exprs[i].counter, exprs[i+1].counter):
                continue

            # 範囲表現として設定する
            exprs[i].value_upper_bound = exprs[i+1].value_upper_bound
            exprs[i].position_end = exprs[i+1].position_end
            exprs[i].set_original_expr_from_position(text)
            exprs[i].options = self.merge_options(exprs[i].options, exprs[i+1].options)

            # i+1番目は使わないのでNoneにする -> あとでfilterでキレイにする
            exprs[i+1] = None  # type: ignore

        return [expr for expr in exprs if expr]

    def multiply_numexp_value(self, expr: NumericalExpression, x: float) -> NumericalExpression:
        """抽出した表現の数値に対する倍数を計算する.

        Parameters
        ----------
        expr : NumericalExpression
            抽出した数値表現
        x : float
            倍数

        Returns
        -------
        NumericalExpression
            計算後の数値表現
        """
        new_expr = deepcopy(expr)
        new_expr.value_lower_bound *= x
        new_expr.value_upper_bound *= x

        return new_expr

    def match_counter_suffix(self, counter1: str, counter2: str) -> bool:
        """2つの数値表現文字列の単位が一致するか判定する.

        Parameters
        ----------
        counter1 : str
            比較する数値文字列
        counter2 : str
            比較する数値文字列

        Returns
        -------
        bool
            True：一致する、False：一致しない

        Notes
        -----
            「時速50km～60km」のような事例に対応する
        """
        def delete_after_slash(string: str) -> str:
            if "/" not in string:
                return string

            return string[:string.index("/")]

        # 50km/hと60kmのように規格化されており、完全一致ではマッチしないため、スラッシュより前の単位が一致するかどうかで判断する
        return delete_after_slash(counter1) == delete_after_slash(counter2)
