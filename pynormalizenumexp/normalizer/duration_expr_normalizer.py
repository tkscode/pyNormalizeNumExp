"""期間の抽出・正規化処理を定義するモジュール."""
from copy import deepcopy
from typing import List, Tuple

from pynormalizenumexp.expression.base import INF, NNumber, NTime, NumberModifier
from pynormalizenumexp.expression.duration import DurationExpression, DurationPattern
from pynormalizenumexp.utility.dict_loader import DictLoader

from .base import BaseNormalizer
from .number_normalizer import NumberNormalizer


class DurationExpressionNormalizer(BaseNormalizer):
    """期間の抽出・正規化を行うクラス."""

    limited_expressions: List[DurationPattern]
    prefix_counters: List[DurationPattern]

    def __init__(self, dict_loader: DictLoader) -> None:
        """コンストラクタ.

        Parameters
        ----------
        dict_loader : DictLoader
            辞書ファイルのローダー
        """
        super().__init__(dict_loader)

        self.number_normalizer = NumberNormalizer(dict_loader)

        self.load_dictionaries("duration_expression.json", "duration_prefix_counter.json",
                               "duration_prefix.json", "duration_suffix.json")

    def load_dictionaries(self, limited_expr_dict_file: str, prefix_counter_dict_file: str,
                          prefix_number_modifier_dict_file: str, suffix_number_modifier_dict_file: str) -> None:
        """辞書ファイルの読み込み.

        Parameters
        ----------
        limited_expr_dict_file : str
            期間のパターンを定義した辞書ファイル名
        prefix_counter_dict_file : str
            接頭表現（単位や年代など）を定義した辞書ファイル名
        prefix_number_modifier_dict_file : str
            接尾表現（範囲表現）を定義した辞書ファイル名
        suffix_number_modifier_dict_file : str
            接尾表現を定義した辞書ファイル名
        """
        self.limited_expressions = self.dict_loader.load_limited_duration_expr_dict(limited_expr_dict_file)
        self.prefix_counters = self.dict_loader.load_limited_duration_expr_dict(prefix_counter_dict_file)
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

    def numbers2expressions(self, numbers: List[NNumber]) -> List[DurationExpression]:  # type: ignore[override]
        """抽出した数値表現を期間表現のオブジェクトに変換する.

        Parameters
        ----------
        numbers : List[NNumber]
            抽出した数値表現

        Returns
        -------
        List[DurationExpression]
            期間表現のオブジェクト
        """
        return [DurationExpression(number) for number in numbers]

    def revise_duration_expr_by_process_type(self, duration_expr: DurationExpression,
                                             process_type: str,
                                             matching_duration_expr: DurationPattern) -> DurationExpression:
        """修飾語でないパターンに含まれるprocess_typeによる正規化表現の補正を行う.

        Parameters
        ----------
        duration_expr : DurationExpression
            補正対象の期間表現
        process_type : str
            処理タイプ
        matching_duration_expr : DurationPattern
            マッチした期間表現パターン

        Returns
        -------
        DurationExpression
            補正後の期間表現
        """
        new_duration_expr = deepcopy(duration_expr)
        if process_type == "han":
            if len(matching_duration_expr.corresponding_time_position) == 0:
                return new_duration_expr

            new_duration_expr.value_lower_bound, new_duration_expr.value_upper_bound \
                = self.do_option_han(new_duration_expr, matching_duration_expr.corresponding_time_position[-1])

        return new_duration_expr

    def revise_expr_by_matching_limited_expression(self, exprs: List[DurationExpression],  # type: ignore[override]
                                                   expr_id: int, matching_expr: DurationPattern) \
            -> List[DurationExpression]:
        """マッチした期間表現の補正を行う.

        Parameters
        ----------
        exprs : List[DurationExpression]
            抽出された期間表現
        expr_id : int
            どの期間表現に着目するかのID（インデックス）
        matching_expr : DurationPattern
            マッチした表現辞書パターン

        Returns
        -------
        List[DurationExpression]
            補正済みの期間表現
        """
        new_exprs = deepcopy(exprs)
        final_expr_id = expr_id + matching_expr.total_number_of_place_holder
        new_exprs[expr_id].position_end = new_exprs[final_expr_id].position_end \
            + matching_expr.len_of_after_final_place_holder

        for i, time_position in enumerate(matching_expr.corresponding_time_position):
            new_exprs[expr_id] = self.set_time(new_exprs[expr_id],
                                               time_position,
                                               new_exprs[expr_id+i])
        for i, process_type in enumerate(matching_expr.process_type):
            new_exprs[expr_id] = self.revise_duration_expr_by_process_type(
                new_exprs[expr_id], process_type, matching_expr
            )
        new_exprs[expr_id].ordinary = matching_expr.ordinary

        min_id = expr_id + 1
        max_id = expr_id + matching_expr.total_number_of_place_holder
        return [x[1] for x in filter(lambda x: min_id > x[0] or x[0] > max_id, enumerate(new_exprs))]

    def revise_expr_by_matching_prefix_counter(self, expr: DurationExpression,  # type: ignore[override]
                                               matching_expr: DurationPattern) -> DurationExpression:
        """マッチした単位表現から期間表現の補正を行う.

        Parameters
        ----------
        expr : DurationExpression
            抽出された期間表現
        matching_expr : DurationPattern
            マッチした表現辞書パターン

        Returns
        -------
        DurationExpression
            補正済みの期間表現
        """
        # 期間表現にprefix_counterは存在しないので何もしない
        return deepcopy(expr)

    def revise_expr_by_number_modifier(self, expr: DurationExpression,  # type: ignore[override] # noqa: C901
                                       number_modifier: NumberModifier) -> DurationExpression:
        """マッチした修飾表現から期間表現の補正を行う.

        Parameters
        ----------
        expr : DurationExpression
            抽出された期間表現
        number_modifier : NumberModifier
            マッチした修飾表現

        Returns
        -------
        DurationExpression
            補正後の期間表現
        """
        new_expr = deepcopy(expr)
        if number_modifier.process_type == "or_over":
            new_expr.value_upper_bound = NTime(-INF)
        elif number_modifier.process_type == "or_less":
            new_expr.value_lower_bound = NTime(INF)
        elif number_modifier.process_type == "over":
            new_expr.value_upper_bound = NTime(-INF)
            new_expr.include_lower_bound = False
        elif number_modifier.process_type == "less":
            new_expr.value_lower_bound = NTime(INF)
            new_expr.include_upper_bound = False
        elif number_modifier.process_type == "ordinary":
            # TODO 序数は絶対時間として扱うか期間として扱うか
            new_expr.ordinary = True
        elif number_modifier.process_type == "per":
            # TODO 「1日毎」などどんな処理をするか未定
            pass
        elif number_modifier.process_type == "dai":
            # TODO 「1秒台」などどんな処理をするか未定
            pass
        elif number_modifier.process_type == "about":
            val_lb, val_ub = self.do_time_about(new_expr)
            new_expr.value_lower_bound = val_lb
            new_expr.value_upper_bound = val_ub
        elif number_modifier.process_type == "kyou":
            val_lb, val_ub = self.do_time_kyou(new_expr)
            new_expr.value_lower_bound = val_lb
            new_expr.value_upper_bound = val_ub
        elif number_modifier.process_type == "jaku":
            val_lb, val_ub = self.do_time_jaku(new_expr)
            new_expr.value_lower_bound = val_lb
            new_expr.value_upper_bound = val_ub
        elif number_modifier.process_type == "made":
            if new_expr.value_upper_bound == new_expr.value_lower_bound:
                new_expr.value_lower_bound = NTime(INF)
            else:
                pass
        elif number_modifier.process_type == "none":
            pass
        else:
            new_expr.options.append(number_modifier.process_type)

        return new_expr

    def delete_not_expression(self,  # type: ignore[override]
                              exprs: List[DurationExpression]) -> List[DurationExpression]:
        """時間オブジェクトがNullの期間表現を削除する.

        Parameters
        ----------
        exprs : List[DurationExpression]
            抽出された期間表現

        Returns
        -------
        List[DurationExpression]
            削除後の期間表現
        """
        for i in range(len(exprs)):
            if self.normalizer_utility.is_null_time(exprs[i].value_lower_bound) \
                    and self.normalizer_utility.is_null_time(exprs[i].value_upper_bound):
                exprs[i] = None  # type: ignore

        return [expr for expr in exprs if expr]

    def fix_by_range_expression(self,  # type: ignore[override]
                                text: str, exprs: List[DurationExpression]) -> List[DurationExpression]:
        """期間の範囲表現の修正を行う.

        Parameters
        ----------
        text : str
            元のテキスト
        exprs : List[DurationExpression]
            抽出された期間表現

        Returns
        -------
        List[DurationExpression]
            修正後の期間表現
        """
        for i in range(len(exprs) - 1):
            if exprs[i] is None \
                    or not self.have_kara_suffix(exprs[i].options) \
                    or not self.have_kara_prefix(exprs[i+1].options) \
                    or exprs[i].position_end + 2 < exprs[i+1].position_start:
                continue

            # 範囲表現として設定する
            exprs[i].value_upper_bound = exprs[i+1].value_upper_bound
            exprs[i].position_end = exprs[i+1].position_end
            exprs[i].set_original_expr_from_position(text)
            exprs[i].options = self.merge_options(exprs[i].options, exprs[i+1].options)

            # i+1番目は使わないのでNoneにする -> あとでfilterでキレイにする
            exprs[i+1] = None  # type: ignore

        return [expr for expr in exprs if expr]

    def do_option_han(self, duration_expr: DurationExpression,  # noqa: C901
                      corresponding_time_position: str) -> Tuple[NTime, NTime]:
        """「半」表現の場合の日付計算を行う.

        Parameters
        ----------
        duration_expr : DurationExpression
            計算対象の期間表現
        corresponding_time_position : str
            時間表現の単位種別

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = duration_expr.value_lower_bound
        val_ub = duration_expr.value_upper_bound
        if corresponding_time_position == "y":
            val_lb.year += 0.5
            val_ub.year += 0.5
        elif corresponding_time_position == "m":
            val_lb.month += 0.5
            val_ub.month += 0.5
        elif corresponding_time_position == "d":
            val_lb.day += 0.5
            val_ub.day += 0.5
        elif corresponding_time_position == "h":
            val_lb.hour += 0.5
            val_ub.hour += 0.5
        elif corresponding_time_position == "mn":
            val_lb.minute += 0.5
            val_ub.minute += 0.5
        elif corresponding_time_position == "s":
            val_lb.minute += 0.5
            val_ub.minute += 0.5
        elif corresponding_time_position == "seiki":
            val_lb.year += 50
            val_ub.year += 50

        return val_lb, val_ub

    def do_time_about(self, duration_expr: DurationExpression) -> Tuple[NTime, NTime]:
        """about表現の場合の日付計算を行う.

        Parameters
        ----------
        duration_expr : DurationExpression
            計算対象の期間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = duration_expr.value_lower_bound
        val_ub = duration_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb)
        if target_time_position == "y":
            val_lb.year -= 5
            val_ub.year += 5
        elif target_time_position == "m":
            val_lb.month -= 1
            val_ub.month += 1
        elif target_time_position == "d":
            val_lb.day -= 1
            val_ub.day += 1
        elif target_time_position == "h":
            val_lb.hour -= 1
            val_ub.hour += 1
        elif target_time_position == "mn":
            val_lb.minute -= 5
            val_ub.minute += 5
        elif target_time_position == "s":
            val_lb.second -= 5
            val_ub.second += 5

        return val_lb, val_ub

    def do_time_kyou(self, duration_expr: DurationExpression) -> Tuple[NTime, NTime]:
        """「強」表現の場合の日付計算を行う.

        Parameters
        ----------
        duration_expr : DurationExpression
            計算対象の期間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = duration_expr.value_lower_bound
        val_ub = duration_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb)
        if target_time_position == "y":
            val_ub.year += 5
        elif target_time_position == "m":
            val_ub.month += 1
        elif target_time_position == "d":
            val_ub.day += 1
        elif target_time_position == "h":
            val_ub.hour += 1
        elif target_time_position == "mn":
            val_ub.minute += 5
        elif target_time_position == "s":
            val_ub.second += 5
        else:
            pass

        return val_lb, val_ub

    def do_time_jaku(self, duration_expr: DurationExpression) -> Tuple[NTime, NTime]:
        """「弱」表現の場合の日付計算を行う.

        Parameters
        ----------
        duration_expr : DurationExpression
            計算対象の期間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = duration_expr.value_lower_bound
        val_ub = duration_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb)
        if target_time_position == "y":
            val_lb.year -= 5
        elif target_time_position == "m":
            val_lb.month -= 1
        elif target_time_position == "d":
            val_lb.day -= 1
        elif target_time_position == "h":
            val_lb.hour -= 1
        elif target_time_position == "mn":
            val_lb.minute -= 5
        elif target_time_position == "s":
            val_lb.second -= 5
        else:
            pass

        return val_lb, val_ub

    def set_time(self, duration_expr: DurationExpression, time_position: str,
                 integrate_duration_expr: DurationExpression) -> DurationExpression:
        """時間表記に応じて年月日時分秒をセットする.

        Parameters
        ----------
        duration_expr : DurationExpression
            セット対象の期間表現
        corresponding_time_position : str
            時間表記
        final_duration_expr : DurationExpression
            セット時に利用する期間表現

        Returns
        -------
        DurationExpression
            セット後の期間表現
        """
        new_duration_expr = deepcopy(duration_expr)
        if time_position == "y":
            new_duration_expr.value_lower_bound.year = integrate_duration_expr.org_value_lower_bound
            new_duration_expr.value_upper_bound.year = integrate_duration_expr.org_value_upper_bound
        elif time_position == "m":
            new_duration_expr.value_lower_bound.month = integrate_duration_expr.org_value_lower_bound
            new_duration_expr.value_upper_bound.month = integrate_duration_expr.org_value_upper_bound
        elif time_position == "d":
            new_duration_expr.value_lower_bound.day = integrate_duration_expr.org_value_lower_bound
            new_duration_expr.value_upper_bound.day = integrate_duration_expr.org_value_upper_bound
        elif time_position == "h":
            new_duration_expr.value_lower_bound.hour = integrate_duration_expr.org_value_lower_bound
            new_duration_expr.value_upper_bound.hour = integrate_duration_expr.org_value_upper_bound
        elif time_position == "mn":
            new_duration_expr.value_lower_bound.minute = integrate_duration_expr.org_value_lower_bound
            new_duration_expr.value_upper_bound.minute = integrate_duration_expr.org_value_upper_bound
        elif time_position == "s":
            new_duration_expr.value_lower_bound.second = integrate_duration_expr.org_value_lower_bound
            new_duration_expr.value_upper_bound.second = integrate_duration_expr.org_value_upper_bound
        elif time_position == "seiki":
            new_duration_expr.value_lower_bound.year = integrate_duration_expr.org_value_lower_bound * 100
            new_duration_expr.value_upper_bound.year = integrate_duration_expr.org_value_upper_bound * 100
        elif time_position == "w":
            new_duration_expr.value_lower_bound.day = integrate_duration_expr.org_value_lower_bound * 7
            new_duration_expr.value_upper_bound.day = integrate_duration_expr.org_value_upper_bound * 7

        return new_duration_expr
