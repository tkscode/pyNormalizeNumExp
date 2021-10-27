from copy import deepcopy
from typing import List, Tuple

from pynormalizenumexp.expression import AbstimeExpression, LimitedAbstimeExpression, NNumber, NTime, NumberModifier
from pynormalizenumexp.expression.base import INF
from pynormalizenumexp.utility import DictLoader

from .base import BaseNormalizer
from .number_normalizer import NumberNormalizer


class AbstimeExpressionNormalizer(BaseNormalizer):
    def __init__(self, dict_loader: DictLoader) -> None:
        """コンストラクタ.

        Parameters
        ----------
        dict_loader : DictLoader
            辞書ファイルのローダー
        """
        super().__init__(dict_loader)

        self.number_normalizer = NumberNormalizer(dict_loader)

        self.load_dictionaries("abstime_expression.json", "abstime_prefix_counter.json",
                               "abstime_prefix.json", "abstime_suffix.json")

    def load_dictionaries(self, limited_expr_dict_file: str, prefix_counter_dict_file: str,
                          prefix_number_modifier_dict_file: str, suffix_number_modifier_dict_file: str) -> None:
        """辞書ファイルの読み込み.

        Parameters
        ----------
        limited_expr_dict_file : str
            狭義の表現を定義した辞書ファイル名
        prefix_counter_dict_file : str
            接頭表現（単位や年代など）を定義した辞書ファイル名
        prefix_number_modifier_dict_file : str
            接尾表現（範囲表現）を定義した辞書ファイル名
        suffix_number_modifier_dict_file : str
            接尾表現を定義した辞書ファイル名
        """
        self.limited_expressions = self.dict_loader.load_limited_abstime_expr_dict(limited_expr_dict_file)
        self.prefix_counters = self.dict_loader.load_limited_abstime_expr_dict(prefix_counter_dict_file)
        self.prefix_number_modifier = self.dict_loader.load_number_modifier_dict(prefix_number_modifier_dict_file)
        self.suffix_number_modifier = self.dict_loader.load_number_modifier_dict(suffix_number_modifier_dict_file)

        self.limited_expression_patterns = self.build_patterns(self.limited_expressions)
        self.prefix_counter_patterns = self.build_patterns(self.prefix_counters, reverse=True)
        self.prefix_number_modifier_patterns = self.build_patterns(self.prefix_number_modifier, reverse=True)
        self.suffix_number_modifier_patterns = self.build_patterns(self.suffix_number_modifier)

    def normalize_number(self, text: str) -> List[NNumber]:
        return self.number_normalizer.process(text, do_fix_symbol=False)

    def set_time(self, abstime_expr: AbstimeExpression, corresponding_time_position: str,
                 final_abstime_expr: AbstimeExpression) -> AbstimeExpression:
        """時間表記に応じて年月日時分秒をセットする.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            セット対象の絶対時間表現
        corresponding_time_position : str
            時間表記
        final_abstime_expr : AbstimeExpression
            セット時に利用する絶対時間表現

        Returns
        -------
        AbstimeExpression
            セット後の絶対時間表現

        Raises
        ------
        ValueError
            時間表記が不正な値の場合
        """
        new_abstime_expr = deepcopy(abstime_expr)
        if corresponding_time_position == "y":
            new_abstime_expr.value_lower_bound.year = final_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.year = final_abstime_expr.org_value_upper_bound
        elif corresponding_time_position == "m":
            new_abstime_expr.value_lower_bound.month = final_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.month = final_abstime_expr.org_value_upper_bound
        elif corresponding_time_position == "d":
            new_abstime_expr.value_lower_bound.day = final_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.day = final_abstime_expr.org_value_upper_bound
        elif corresponding_time_position == "h":
            new_abstime_expr.value_lower_bound.hour = final_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.hour = final_abstime_expr.org_value_upper_bound
        elif corresponding_time_position == "mn":
            new_abstime_expr.value_lower_bound.minute = final_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.minute = final_abstime_expr.org_value_upper_bound
        elif corresponding_time_position == "s":
            new_abstime_expr.value_lower_bound.second = final_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.second = final_abstime_expr.org_value_upper_bound
        elif corresponding_time_position == "seiki":
            new_abstime_expr.value_lower_bound.year = final_abstime_expr.org_value_lower_bound * 100 - 99
            new_abstime_expr.value_upper_bound.year = final_abstime_expr.org_value_upper_bound * 100
        else:
            raise ValueError(f'Not supported corresponding time position "{corresponding_time_position}"')

        return new_abstime_expr

    def revise_abstime_expr_by_process_type(self, abstime_expr: AbstimeExpression,
                                            process_type: str) -> AbstimeExpression:
        """修飾語でないパターンに含まれるprocess_typeによる規格化表現の補正.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            補正対象の絶対時間表現
        process_type : str
            処理タイプ

        Returns
        -------
        AbstimeExpression
            補正後の絶対時間表現

        Raises
        ------
        ValueError
            処理タイプが不正な値の場合
        """
        new_abstime_expr = deepcopy(abstime_expr)
        if process_type == "gozen":
            if new_abstime_expr.value_lower_bound.hour == INF:
                new_abstime_expr.value_lower_bound.hour = 0
                new_abstime_expr.value_upper_bound.hour = 12
            else:
                pass
        elif process_type == "gogo":
            if new_abstime_expr.value_lower_bound.hour == INF:
                new_abstime_expr.value_lower_bound.hour = 12
                new_abstime_expr.value_upper_bound.hour = 24
            else:
                new_abstime_expr.value_lower_bound.hour += 12
                new_abstime_expr.value_upper_bound.hour += 12
        elif process_type == "han":
            new_abstime_expr.value_lower_bound.minute = 30
            new_abstime_expr.value_upper_bound.minute = 30
        elif process_type == "unclear" and (1800 <= new_abstime_expr.value_lower_bound.month <= 2100):
            # 「2012/3」「3/10」の曖昧性を解消する
            # 最初はmonth/dayとして認識している。monthの値として変で、yearとして考えられる場合、これを変更する
            new_abstime_expr.value_lower_bound.year = abstime_expr.value_lower_bound.month
            new_abstime_expr.value_upper_bound.year = abstime_expr.value_upper_bound.month
            new_abstime_expr.value_lower_bound.month = abstime_expr.value_lower_bound.day
            new_abstime_expr.value_upper_bound.month = abstime_expr.value_upper_bound.day
            new_abstime_expr.value_lower_bound.day = INF
            new_abstime_expr.value_upper_bound = -INF
        else:
            raise ValueError(f'Not supported process type "{process_type}"')

        return new_abstime_expr

    def revise_expr_by_matching_limited_expression(self, abstime_exprs: List[AbstimeExpression],
                                                   abstime_expr_id: int,
                                                   matching_abstime_expr: LimitedAbstimeExpression) \
            -> List[AbstimeExpression]:
        new_abstime_exprs = deepcopy(abstime_exprs)
        final_abstime_expr_id = abstime_expr_id + matching_abstime_expr.total_number_of_place_holder
        new_abstime_exprs[abstime_expr_id].position_end = new_abstime_exprs[final_abstime_expr_id].position_end \
            + matching_abstime_expr.len_of_after_final_place_holder

        for i, time_position in enumerate(matching_abstime_expr.corresponding_time_position):
            new_abstime_exprs[abstime_expr_id] = self.set_time(new_abstime_exprs[abstime_expr_id],
                                                               time_position,
                                                               new_abstime_exprs[abstime_expr_id+i])
        for i, process_type in enumerate(matching_abstime_expr.process_type):
            new_abstime_exprs[abstime_expr_id] = self.revise_abstime_expr_by_process_type(
                new_abstime_exprs[abstime_expr_id], process_type
            )
        new_abstime_exprs[abstime_expr_id].ordinary = matching_abstime_expr.ordinary
        new_abstime_exprs[abstime_expr_id].options.append(matching_abstime_expr.option)

        min_id = abstime_expr_id + 1
        max_id = abstime_expr_id + matching_abstime_expr.total_number_of_place_holder
        return [x[1] for x in filter(lambda x: min_id <= x[0] <= max_id, enumerate(new_abstime_exprs))]

    def revise_expr_by_matching_prefix_counter(self, abstime_expr: AbstimeExpression,
                                               matching_expr: LimitedAbstimeExpression) -> AbstimeExpression:
        # 一致したパターンに応じて、規格化を行う（数字の前側に単位等が来る場合。絶対時間表現の場合「西暦」など）
        new_abstime_expr = deepcopy(abstime_expr)
        if matching_expr.option == "seireki":
            tmp = int(matching_expr.process_type[0])
            new_abstime_expr.value_lower_bound.year += tmp
            new_abstime_expr.value_upper_bound.year += tmp
        elif matching_expr.option == "gogo":
            new_abstime_expr.value_lower_bound += 12
            new_abstime_expr.value_upper_bound += 12
        elif matching_expr.option == "gozen":
            # 特に操作することはないのでpass
            pass
        else:
            new_abstime_expr.options.append(matching_expr.option)

        new_abstime_expr.position_start -= len(matching_expr.pattern)

        return new_abstime_expr

    def revise_expr_by_number_modifier(self, abstime_expr: AbstimeExpression,
                                       number_modifier: NumberModifier) -> AbstimeExpression:
        new_abstime_expr = deepcopy(abstime_expr)
        if number_modifier.process_type == "or_over":
            new_abstime_expr.value_upper_bound = NTime(value=-INF)
        elif number_modifier.process_type == "or_less":
            new_abstime_expr.value_lower_bound = NTime(value=INF)
        elif number_modifier.process_type == "over":
            new_abstime_expr.value_upper_bound = NTime(value=-INF)
            new_abstime_expr.include_lower_bound = False
        elif number_modifier.process_type == "less":
            new_abstime_expr.value_lower_bound = NTime(value=INF)
            new_abstime_expr.include_upper_bound = False
        elif number_modifier.process_type == "about":
            about_val = self.do_time_about(new_abstime_expr)
            new_abstime_expr.value_lower_bound = about_val[0]
            new_abstime_expr.value_upper_bound = about_val[1]
        elif number_modifier.process_type == "none":
            pass

    def delete_not_expr(self):
        pass

    def fix_by_range_expression(self):
        pass

    def do_time_about(self, abstime_expr: AbstimeExpression) -> Tuple[NTime, NTime]:
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(abstime_expr.value_lower_bound)
        if target_time_position == "y":
            val_lb.year -= 5
            val_ub.year += 5
        elif target_time_position == "m":
            # TODO 1月頃という表現だと0月～2月にならないか？
            val_lb.month -= 1
            val_ub.month += 1
        elif target_time_position == "d":
            val_lb.day -= 1
            val_ub.day += 1
        elif target_time_position == "H":
            val_lb.hour -= 1
            val_ub.hour += 1
        elif target_time_position == "M":
            val_lb.minute -= 5
            val_ub.minute += 5
        elif target_time_position == "S":
            val_lb.second -= 5
            val_ub.second += 5

        return val_lb, val_ub

    def do_time_zenhan(self, abstime_expr: AbstimeExpression) -> Tuple[NTime, NTime]:
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(abstime_expr.value_lower_bound)
        if target_time_position == "y":
            if val_lb.year != val_ub.year:
                # 「18世紀前半」のような場合
                val_ub.year = (val_lb.year + val_ub.year) / 2 - 0.5
            else:
                # 「1989年前半」のような場合
                val_lb.month = 1
                val_ub.month = 6
        elif target_time_position == "m":
            # 「7月前半」のような場合
            val_lb.day = 1
            val_ub.day = 15
        elif target_time_position == "d":
            # 「3日朝」のような場合
            val_lb.hour = 5
            val_ub.hour = 12
        else:
            pass

        return val_lb, val_ub

    def do_time_kouhan(self, abstime_expr: AbstimeExpression) -> Tuple[NTime, NTime]:
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(abstime_expr.value_lower_bound)
        if target_time_position == "y":
            if val_lb.year != val_ub.year:
                # 「18世紀後半」のような場合
                val_lb.year = (val_lb.year + val_ub.year) / 2 + 0.5
            else:
                # 「1989年後半」のような場合
                val_lb.month = 7
                val_ub.month = 12
        elif target_time_position == "m":
            # 「7月後半」のような場合
            val_lb.day = 16
            val_ub.day = 31
        elif target_time_position == "d":
            # 「3日夜」のような場合
            val_lb.hour = 18
            val_ub.hour = 24
        else:
            pass

        return val_lb, val_ub

    def do_time_nakaba(self, abstime_expr: AbstimeExpression) -> Tuple[NTime, NTime]:
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(abstime_expr.value_lower_bound)
        if target_time_position == "y":
            if val_lb.year != val_ub.year:
                # 「18世紀中盤」のような場合
                tmp = (val_ub - val_lb) // 4
                val_lb.year += tmp
                val_ub.year -= tmp
            else:
                # 「1989年中盤」のような場合
                val_lb.month = 4
                val_ub.month = 9
        elif target_time_position == "m":
            # 「7月半ば」のような場合
            val_lb.day = 10
            val_ub.day = 20
        elif target_time_position == "d":
            # 「3日昼」のような場合
            val_lb.hour = 10
            val_ub.hour = 15
        else:
            pass

        return val_lb, val_ub
