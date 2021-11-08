"""相対時間の抽出・正規化処理を定義するモジュール."""
from copy import deepcopy
from typing import List, Tuple

from pynormalizenumexp.expression.base import INF, NNumber, NTime, NumberModifier
from pynormalizenumexp.expression.reltime import ReltimeExpression, ReltimePattern
from pynormalizenumexp.utility.dict_loader import DictLoader

from .base import BaseNormalizer
from .number_normalizer import NumberNormalizer


class ReltimeExpressionNormalizer(BaseNormalizer):
    """相対時間の抽出・正規化を行うクラス."""

    limited_expressions: List[ReltimePattern]
    prefix_counters: List[ReltimePattern]

    def __init__(self, dict_loader: DictLoader) -> None:
        """コンストラクタ.

        Parameters
        ----------
        dict_loader : DictLoader
            辞書ファイルのローダー
        """
        super().__init__(dict_loader)

        self.number_normalizer = NumberNormalizer(dict_loader)

        self.load_dictionaries("reltime_expression.json", "reltime_prefix_counter.json",
                               "reltime_prefix.json", "reltime_suffix.json")

    def load_dictionaries(self, limited_expr_dict_file: str, prefix_counter_dict_file: str,
                          prefix_number_modifier_dict_file: str, suffix_number_modifier_dict_file: str) -> None:
        """辞書ファイルの読み込み.

        Parameters
        ----------
        limited_expr_dict_file : str
            相対時間のパターンを定義した辞書ファイル名
        prefix_counter_dict_file : str
            接頭表現（単位や年代など）を定義した辞書ファイル名
        prefix_number_modifier_dict_file : str
            接尾表現（範囲表現）を定義した辞書ファイル名
        suffix_number_modifier_dict_file : str
            接尾表現を定義した辞書ファイル名
        """
        self.limited_expressions = self.dict_loader.load_limited_reltime_expr_dict(limited_expr_dict_file)
        self.prefix_counters = self.dict_loader.load_limited_reltime_expr_dict(prefix_counter_dict_file)
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

    def numbers2expressions(self, numbers: List[NNumber]) -> List[ReltimeExpression]:  # type: ignore[override]
        """抽出した数値表現を相対時間表現のオブジェクトに変換する.

        Parameters
        ----------
        numbers : List[NNumber]
            抽出した数値表現

        Returns
        -------
        List[ReltimeExpression]
            相対時間表現のオブジェクト
        """
        return [ReltimeExpression(number) for number in numbers]

    def revise_reltime_expr_by_process_type(self, reltime_expr: ReltimeExpression,
                                            process_type: str,
                                            matching_reltime_expr: ReltimePattern) -> ReltimeExpression:
        """修飾語でないパターンに含まれるprocess_typeによる正規化表現の補正を行う.

        Parameters
        ----------
        reltime_expr : ReltimeExpression
            補正対象の相対時間表現
        process_type : str
            処理タイプ
        matching_reltime_expr : ReltimePattern
            マッチした相対時間表現パターン

        Returns
        -------
        ReltimeExpression
            補正後の相対時間表現
        """
        new_reltime_expr = deepcopy(reltime_expr)
        if process_type == "han":
            if len(matching_reltime_expr.corresponding_time_position) == 0:
                return new_reltime_expr

            new_reltime_expr.value_lower_bound_rel, new_reltime_expr.value_upper_bound_rel \
                = self.do_option_han(new_reltime_expr, matching_reltime_expr.corresponding_time_position[-1])
        elif process_type == "or_over":
            reltime_expr.value_upper_bound_abs = NTime(-INF)
        elif process_type == "or_less":
            reltime_expr.value_lower_bound_abs = NTime(INF)
        elif process_type == "over":
            reltime_expr.value_upper_bound_abs = NTime(-INF)
            reltime_expr.include_lower_bound = False
        elif process_type == "less":
            reltime_expr.value_lower_bound_abs = NTime(INF)
            reltime_expr.include_upper_bound = False
        elif process_type == "inai":
            reltime_expr.value_lower_bound_rel = NTime(0)
        elif process_type == "none":
            pass

        return new_reltime_expr

    def revise_expr_by_matching_limited_expression(self, exprs: List[ReltimeExpression],  # type: ignore[override]
                                                   expr_id: int,
                                                   matching_expr: ReltimePattern) -> List[ReltimeExpression]:
        """マッチした相対時間表現の補正を行う.

        Parameters
        ----------
        exprs : List[ReltimeExpression]
            抽出された相対時間表現
        expr_id : int
            どの相対時間表現に着目するかのID（インデックス）
        matching_expr : ReltimePattern
            マッチした表現辞書パターン

        Returns
        -------
        List[ReltimeExpression]
            補正済みの相対時間表現
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
            new_exprs[expr_id] = self.revise_reltime_expr_by_process_type(
                new_exprs[expr_id], process_type, matching_expr
            )
        new_exprs[expr_id].ordinary = matching_expr.ordinary

        min_id = expr_id + 1
        max_id = expr_id + matching_expr.total_number_of_place_holder
        return [x[1] for x in filter(lambda x: min_id > x[0] or x[0] > max_id, enumerate(new_exprs))]

    def revise_expr_by_matching_prefix_counter(self, expr: ReltimeExpression,  # type: ignore[override]
                                               matching_expr: ReltimePattern) -> ReltimeExpression:
        """マッチした単位表現から相対時間表現の補正を行う.

        Parameters
        ----------
        expr : ReltimeExpression
            抽出された相対時間表現
        matching_expr : ReltimePattern
            マッチした表現辞書パターン

        Returns
        -------
        ReltimeExpression
            補正済みの相対時間表現
        """
        new_expr = deepcopy(expr)
        if matching_expr.option == "add_relation":
            # 「去年3月」などの、「相対時間表現」＋「絶対時間表現」からなる処理
            if self.normalizer_utility.is_null_time(new_expr.value_lower_bound_abs) \
                    and self.normalizer_utility.is_null_time(new_expr.value_upper_bound_abs):
                # 絶対時間表現が抽出されていなければ、処理を行わない
                return new_expr

            relation_val = int(matching_expr.process_type[0])
            if matching_expr.corresponding_time_position[0] == "y":
                new_expr.value_lower_bound_rel.year = new_expr.value_upper_bound_rel.year = relation_val
            elif matching_expr.corresponding_time_position[0] == "m":
                new_expr.value_lower_bound_rel.month = new_expr.value_upper_bound_rel.month = relation_val
            elif matching_expr.corresponding_time_position[0] == "d":
                new_expr.value_lower_bound_rel.day = new_expr.value_upper_bound_rel.day = relation_val
            elif matching_expr.corresponding_time_position[0] == "h":
                new_expr.value_lower_bound_rel.hour = new_expr.value_upper_bound_rel.hour = relation_val
            elif matching_expr.corresponding_time_position[0] == "mn":
                new_expr.value_lower_bound_rel.minute = new_expr.value_upper_bound_rel.minute = relation_val
            elif matching_expr.corresponding_time_position[0] == "s":
                new_expr.value_lower_bound_rel.second = new_expr.value_upper_bound_rel.second = relation_val

        new_expr.position_start -= len(matching_expr.pattern)

        return new_expr

    def revise_expr_by_number_modifier(self, expr: ReltimeExpression,  # type: ignore[override] # noqa: C901
                                       number_modifier: NumberModifier) -> ReltimeExpression:
        """マッチした修飾表現から相対時間表現の補正を行う.

        Parameters
        ----------
        expr : ReltimeExpression
            抽出された相対時間表現
        number_modifier : NumberModifier
            マッチした修飾表現

        Returns
        -------
        ReltimeExpression
            補正後の相対時間表現
        """
        new_expr = deepcopy(expr)
        if number_modifier.process_type == "about":
            val_lb_rel, val_ub_rel = self.do_time_about(new_expr)
            new_expr.value_lower_bound_rel = val_lb_rel
            new_expr.value_upper_bound_rel = val_ub_rel
        elif number_modifier.process_type == "zenhan":
            val_lb_abs, val_ub_abs = self.do_time_zenhan(new_expr)
            new_expr.value_lower_bound_abs = val_lb_abs
            new_expr.value_upper_bound_abs = val_ub_abs
        elif number_modifier.process_type == "nakaba":
            val_lb_abs, val_ub_abs = self.do_time_nakaba(new_expr)
            new_expr.value_lower_bound_abs = val_lb_abs
            new_expr.value_upper_bound_abs = val_ub_abs
        elif number_modifier.process_type == "kouhan":
            val_lb_abs, val_ub_abs = self.do_time_kouhan(new_expr)
            new_expr.value_lower_bound_abs = val_lb_abs
            new_expr.value_upper_bound_abs = val_ub_abs
        elif number_modifier.process_type == "joujun":
            val_lb_abs, val_ub_abs = self.do_time_joujun(new_expr)
            new_expr.value_lower_bound_abs = val_lb_abs
            new_expr.value_upper_bound_abs = val_ub_abs
        elif number_modifier.process_type == "tyujun":
            val_lb_abs, val_ub_abs = self.do_time_tyujun(new_expr)
            new_expr.value_lower_bound_abs = val_lb_abs
            new_expr.value_upper_bound_abs = val_ub_abs
        elif number_modifier.process_type == "gejun":
            val_lb_abs, val_ub_abs = self.do_time_gejun(new_expr)
            new_expr.value_lower_bound_abs = val_lb_abs
            new_expr.value_upper_bound_abs = val_ub_abs
        else:
            new_expr.options.append(number_modifier.process_type)

        return new_expr

    def delete_not_expression(self,  # type: ignore[override]
                              exprs: List[ReltimeExpression]) -> List[ReltimeExpression]:
        """時間オブジェクトがNullの相対時間表現を削除する.

        Parameters
        ----------
        exprs : List[ReltimeExpression]
            抽出された相対時間表現

        Returns
        -------
        List[ReltimeExpression]
            削除後の相対時間表現
        """
        for i in range(len(exprs)):
            if self.normalizer_utility.is_null_time(exprs[i].value_lower_bound_rel) \
                    and self.normalizer_utility.is_null_time(exprs[i].value_upper_bound_rel):
                exprs[i] = None  # type: ignore

        return [expr for expr in exprs if expr]

    def fix_by_range_expression(self,  # type: ignore[override] # noqa: C901
                                text: str, exprs: List[ReltimeExpression]) -> List[ReltimeExpression]:
        """相対時間の範囲表現の修正を行う.

        Parameters
        ----------
        text : str
            元のテキスト
        exprs : List[ReltimeExpression]
            抽出された相対時間表現

        Returns
        -------
        List[ReltimeExpression]
            修正後の相対時間表現
        """
        def is_registered(number: NNumber, reltime_exprs: List[ReltimeExpression]) -> bool:
            for expr in reltime_exprs:
                if expr.position_start <= number.position_start and number.position_end <= expr.position_end:
                    return True

            return False

        for i in range(len(exprs) - 1):
            if exprs[i] is None \
                    or not self.have_kara_suffix(exprs[i].options) \
                    or not self.have_kara_prefix(exprs[i+1].options) \
                    or exprs[i].position_end + 2 < exprs[i+1].position_start:
                continue

            # 範囲表現として設定する
            exprs[i].value_upper_bound_rel = exprs[i+1].value_upper_bound_rel
            exprs[i].value_upper_bound_abs = exprs[i+1].value_upper_bound_abs
            exprs[i].position_end = exprs[i+1].position_end
            exprs[i].set_original_expr_from_position(text)
            exprs[i].options = self.merge_options(exprs[i].options, exprs[i+1].options)

            # i+1番目は使わないのでNoneにする -> あとでfilterでキレイにする
            exprs[i+1] = None  # type: ignore

        exprs = [expr for expr in exprs if expr]

        # 今日、明日、来年だけの表現を抽出する
        add_reltime_exprs: List[ReltimeExpression] = []
        for prefix_counter in self.prefix_counters:
            try:
                idx = text.index(prefix_counter.pattern)
                prefix_counter.set_len_of_after_final_place_holder()
                number = NNumber(prefix_counter.pattern, idx, idx+prefix_counter.len_of_after_final_place_holder)
                if is_registered(number, exprs):
                    continue

                reltime_expr = ReltimeExpression(number)
                relation_val = int(prefix_counter.process_type[0])
                if prefix_counter.corresponding_time_position[0] == "y":
                    reltime_expr.value_lower_bound_rel.year = reltime_expr.value_upper_bound_rel.year = relation_val
                elif prefix_counter.corresponding_time_position[0] == "m":
                    reltime_expr.value_lower_bound_rel.month = reltime_expr.value_upper_bound_rel.month = relation_val
                elif prefix_counter.corresponding_time_position[0] == "d":
                    reltime_expr.value_lower_bound_rel.day = reltime_expr.value_upper_bound_rel.day = relation_val

                add_reltime_exprs.append(reltime_expr)
            except ValueError:
                pass

        exprs += add_reltime_exprs

        return exprs

    def do_option_han(self, reltime_expr: ReltimeExpression,  # noqa: C901
                      corresponding_time_position: str) -> Tuple[NTime, NTime]:
        """「半」表現の場合の日付計算を行う.

        Parameters
        ----------
        reltime_expr : ReltimeExpression
            計算対象の相対時間表現
        corresponding_time_position : str
            時間表現の単位種別

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        # TODO 「週」、「世紀」に対応していない部分がある
        val_lb_rel = reltime_expr.value_lower_bound_rel
        val_ub_rel = reltime_expr.value_upper_bound_rel
        if corresponding_time_position == "+y":
            val_lb_rel.year += 0.5
            val_ub_rel.year += 0.5
        elif corresponding_time_position == "+m":
            val_lb_rel.month += 0.5
            val_ub_rel.month += 0.5
        elif corresponding_time_position == "+d":
            val_lb_rel.day += 0.5
            val_ub_rel.day += 0.5
        elif corresponding_time_position == "+h":
            val_lb_rel.hour += 0.5
            val_ub_rel.hour += 0.5
        elif corresponding_time_position == "+mn":
            val_lb_rel.minute += 0.5
            val_ub_rel.minute += 0.5
        elif corresponding_time_position == "+s":
            val_lb_rel.minute += 0.5
            val_ub_rel.minute += 0.5
        elif corresponding_time_position == "+seiki":
            val_lb_rel.year += 50
            val_ub_rel.year += 50
        elif corresponding_time_position == "-y":
            val_lb_rel.year -= 0.5
            val_ub_rel.year -= 0.5
        elif corresponding_time_position == "-m":
            val_lb_rel.month -= 0.5
            val_ub_rel.month -= 0.5
        elif corresponding_time_position == "-d":
            val_lb_rel.day -= 0.5
            val_ub_rel.day -= 0.5
        elif corresponding_time_position == "-h":
            val_lb_rel.hour -= 0.5
            val_ub_rel.hour -= 0.5
        elif corresponding_time_position == "-mn":
            val_lb_rel.minute -= 0.5
            val_ub_rel.minute -= 0.5
        elif corresponding_time_position == "-s":
            val_lb_rel.minute -= 0.5
            val_ub_rel.minute -= 0.5
        elif corresponding_time_position == "-seiki":
            val_lb_rel.year -= 50
            val_ub_rel.year -= 50

        return val_lb_rel, val_ub_rel

    def do_time_about(self, reltime_expr: ReltimeExpression) -> Tuple[NTime, NTime]:
        """about表現の場合の日付計算を行う.

        Parameters
        ----------
        reltime_expr : ReltimeExpression
            計算対象の相対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        # 「およそ1000年前」「2か月前頃」など
        val_lb_rel = reltime_expr.value_lower_bound_rel
        val_ub_rel = reltime_expr.value_upper_bound_rel
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb_rel)
        if target_time_position == "y":
            val_lb_rel.year -= 5
            val_ub_rel.year += 5
        elif target_time_position == "m":
            val_lb_rel.month -= 1
            val_ub_rel.month += 1
        elif target_time_position == "d":
            val_lb_rel.day -= 1
            val_ub_rel.day += 1
        elif target_time_position == "h":
            val_lb_rel.hour -= 1
            val_ub_rel.hour += 1
        elif target_time_position == "mn":
            val_lb_rel.minute -= 5
            val_ub_rel.minute += 5
        elif target_time_position == "s":
            val_lb_rel.second -= 5
            val_ub_rel.second += 5

        return val_lb_rel, val_ub_rel

    def do_time_zenhan(self, reltime_expr: ReltimeExpression) -> Tuple[NTime, NTime]:
        """前半表現の場合の日付計算を行う.

        Parameters
        ----------
        reltime_expr : ReltimeExpression
            計算対象の相対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb_abs = reltime_expr.value_lower_bound_abs
        val_ub_abs = reltime_expr.value_upper_bound_abs
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb_abs)
        if target_time_position == "y":
            if val_lb_abs.year != val_ub_abs.year:
                # 「18世紀前半」のような場合
                val_ub_abs.year = (val_lb_abs.year + val_ub_abs.year) / 2 - 0.5
            else:
                # 「1989年前半」のような場合
                val_lb_abs.month = 1
                val_ub_abs.month = 6
        elif target_time_position == "m":
            # 「7月前半」のような場合
            val_lb_abs.day = 1
            val_ub_abs.day = 15
        elif target_time_position == "d":
            # 「3日朝」のような場合
            val_lb_abs.hour = 5
            val_ub_abs.hour = 12
        else:
            pass

        return val_lb_abs, val_ub_abs

    def do_time_kouhan(self, reltime_expr: ReltimeExpression) -> Tuple[NTime, NTime]:
        """後半表現の場合の日付計算を行う.

        Parameters
        ----------
        reltime_expr : ReltimeExpression
            計算対象の相対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb_abs = reltime_expr.value_lower_bound_abs
        val_ub_abs = reltime_expr.value_upper_bound_abs
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb_abs)
        if target_time_position == "y":
            if val_lb_abs.year != val_ub_abs.year:
                # 「18世紀後半」のような場合
                val_lb_abs.year = (val_lb_abs.year + val_ub_abs.year) / 2 + 0.5
            else:
                # 「1989年後半」のような場合
                val_lb_abs.month = 7
                val_ub_abs.month = 12
        elif target_time_position == "m":
            # 「7月後半」のような場合
            val_lb_abs.day = 16
            val_ub_abs.day = 31
        elif target_time_position == "d":
            # 「3日夜」のような場合
            val_lb_abs.hour = 18
            val_ub_abs.hour = 24
        else:
            pass

        return val_lb_abs, val_ub_abs

    def do_time_nakaba(self, reltime_expr: ReltimeExpression) -> Tuple[NTime, NTime]:
        """半ば表現の場合の日付計算を行う.

        Parameters
        ----------
        reltime_expr : ReltimeExpression
            計算対象の相対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb_abs = reltime_expr.value_lower_bound_abs
        val_ub_abs = reltime_expr.value_upper_bound_abs
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb_abs)
        if target_time_position == "y":
            if val_lb_abs.year != val_ub_abs.year:
                # 「18世紀中盤」のような場合
                tmp = (val_ub_abs.year - val_lb_abs.year) // 4
                val_lb_abs.year += tmp
                val_ub_abs.year -= tmp
            else:
                # 「1989年中盤」のような場合
                val_lb_abs.month = 4
                val_ub_abs.month = 9
        elif target_time_position == "m":
            # 「7月半ば」のような場合
            val_lb_abs.day = 10
            val_ub_abs.day = 20
        elif target_time_position == "d":
            # 「3日昼」のような場合
            val_lb_abs.hour = 10
            val_ub_abs.hour = 15
        else:
            pass

        return val_lb_abs, val_ub_abs

    def do_time_joujun(self, reltime_expr: ReltimeExpression) -> Tuple[NTime, NTime]:
        """上旬表現の場合の日付計算を行う.

        Parameters
        ----------
        reltime_expr : ReltimeExpression
            計算対象の相対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb_abs = reltime_expr.value_lower_bound_abs
        val_ub_abs = reltime_expr.value_upper_bound_abs
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb_abs)
        if target_time_position == "m":
            val_lb_abs.day = 1
            val_ub_abs.day = 10

        return val_lb_abs, val_ub_abs

    def do_time_tyujun(self, reltime_expr: ReltimeExpression) -> Tuple[NTime, NTime]:
        """中旬表現の場合の日付計算を行う.

        Parameters
        ----------
        reltime_expr : ReltimeExpression
            計算対象の相対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb_abs = reltime_expr.value_lower_bound_abs
        val_ub_abs = reltime_expr.value_upper_bound_abs
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb_abs)
        if target_time_position == "m":
            val_lb_abs.day = 11
            val_ub_abs.day = 20

        return val_lb_abs, val_ub_abs

    def do_time_gejun(self, reltime_expr: ReltimeExpression) -> Tuple[NTime, NTime]:
        """下旬表現の場合の日付計算を行う.

        Parameters
        ----------
        reltime_expr : ReltimeExpression
            計算対象の相対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb_abs = reltime_expr.value_lower_bound_abs
        val_ub_abs = reltime_expr.value_upper_bound_abs
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb_abs)
        if target_time_position == "m":
            val_lb_abs.day = 21
            val_ub_abs.day = 31

        return val_lb_abs, val_ub_abs

    def set_time(self, reltime_expr: ReltimeExpression, time_position: str,  # noqa: C901
                 integrate_reltime_expr: ReltimeExpression) -> ReltimeExpression:
        """時間表記に応じて年月日時分秒をセットする.

        Parameters
        ----------
        reltime_expr : ReltimeExpression
            セット対象の相対時間表現
        corresponding_time_position : str
            時間表記
        final_reltime_expr : ReltimeExpression
            セット時に利用する相対時間表現

        Returns
        -------
        ReltimeExpression
            セット後の相対時間表現
        """
        new_reltime_expr = deepcopy(reltime_expr)
        if time_position == "y":
            new_reltime_expr.value_lower_bound_abs.year = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_abs.year = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "m":
            new_reltime_expr.value_lower_bound_abs.month = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_abs.month = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "d":
            new_reltime_expr.value_lower_bound_abs.day = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_abs.day = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "h":
            new_reltime_expr.value_lower_bound_abs.hour = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_abs.hour = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "mn":
            new_reltime_expr.value_lower_bound_abs.minute = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_abs.minute = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "s":
            new_reltime_expr.value_lower_bound_abs.second = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_abs.second = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "seiki":
            new_reltime_expr.value_lower_bound_abs.year = integrate_reltime_expr.org_value_lower_bound * 100 - 99
            new_reltime_expr.value_upper_bound_abs.year = integrate_reltime_expr.org_value_upper_bound * 100
        elif time_position == "w":
            new_reltime_expr.value_lower_bound_abs.day = integrate_reltime_expr.org_value_lower_bound * 7
            new_reltime_expr.value_upper_bound_abs.day = integrate_reltime_expr.org_value_upper_bound * 7
        elif time_position == "+y":
            new_reltime_expr.value_lower_bound_rel.year = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.year = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "+m":
            new_reltime_expr.value_lower_bound_rel.month = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.month = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "+d":
            new_reltime_expr.value_lower_bound_rel.day = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.day = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "+h":
            new_reltime_expr.value_lower_bound_rel.hour = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.hour = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "+mn":
            new_reltime_expr.value_lower_bound_rel.minute = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.minute = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "+s":
            new_reltime_expr.value_lower_bound_rel.second = integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.second = integrate_reltime_expr.org_value_upper_bound
        elif time_position == "+seiki":
            new_reltime_expr.value_lower_bound_rel.year = integrate_reltime_expr.org_value_lower_bound * 100
            new_reltime_expr.value_upper_bound_rel.year = integrate_reltime_expr.org_value_upper_bound * 100
        elif time_position == "+w":
            new_reltime_expr.value_lower_bound_rel.day = integrate_reltime_expr.org_value_lower_bound * 7
            new_reltime_expr.value_upper_bound_rel.day = integrate_reltime_expr.org_value_upper_bound * 7
        elif time_position == "-y":
            new_reltime_expr.value_lower_bound_rel.year = -integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.year = -integrate_reltime_expr.org_value_upper_bound
        elif time_position == "-m":
            new_reltime_expr.value_lower_bound_rel.month = -integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.month = -integrate_reltime_expr.org_value_upper_bound
        elif time_position == "-d":
            new_reltime_expr.value_lower_bound_rel.day = -integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.day = -integrate_reltime_expr.org_value_upper_bound
        elif time_position == "-h":
            new_reltime_expr.value_lower_bound_rel.hour = -integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.hour = -integrate_reltime_expr.org_value_upper_bound
        elif time_position == "-mn":
            new_reltime_expr.value_lower_bound_rel.minute = -integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.minute = -integrate_reltime_expr.org_value_upper_bound
        elif time_position == "-s":
            new_reltime_expr.value_lower_bound_rel.second = -integrate_reltime_expr.org_value_lower_bound
            new_reltime_expr.value_upper_bound_rel.second = -integrate_reltime_expr.org_value_upper_bound
        elif time_position == "-seiki":
            new_reltime_expr.value_lower_bound_rel.year = -integrate_reltime_expr.org_value_lower_bound * 100
            new_reltime_expr.value_upper_bound_rel.year = -integrate_reltime_expr.org_value_upper_bound * 100
        elif time_position == "-w":
            new_reltime_expr.value_lower_bound_rel.day = -integrate_reltime_expr.org_value_lower_bound * 7
            new_reltime_expr.value_upper_bound_rel.day = -integrate_reltime_expr.org_value_upper_bound * 7

        return new_reltime_expr
