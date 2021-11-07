"""絶対時間の抽出・正規化処理を定義するモジュール."""
from copy import deepcopy
from typing import List, Tuple

from pynormalizenumexp.expression.abstime import AbstimeExpression, AbstimePattern
from pynormalizenumexp.expression.base import INF, NNumber, NTime, NumberModifier
from pynormalizenumexp.utility.dict_loader import DictLoader

from .base import BaseNormalizer
from .number_normalizer import NumberNormalizer


class AbstimeExpressionNormalizer(BaseNormalizer):
    """絶対時間の抽出・正規化を行うクラス."""

    limited_expressions: List[AbstimePattern]
    prefix_counters: List[AbstimePattern]

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
            絶対時間のパターンを定義した辞書ファイル名
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
        return self.number_normalizer.process(text, do_fix_symbol=False)

    def numbers2expressions(self, numbers: List[NNumber]) -> List[AbstimeExpression]:  # type: ignore[override]
        """抽出した数値表現を絶対時間表現のオブジェクトに変換する.

        Parameters
        ----------
        numbers : List[NNumber]
            抽出した数値表現

        Returns
        -------
        List[AbstimeExpression]
            絶対時間表現のオブジェクト
        """
        return [AbstimeExpression(number) for number in numbers]

    def revise_abstime_expr_by_process_type(self, abstime_expr: AbstimeExpression,
                                            process_type: str) -> AbstimeExpression:
        """修飾語でないパターンに含まれるprocess_typeによる正規化表現の補正を行う.

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
            new_abstime_expr.value_upper_bound.day = -INF
        else:
            pass

        return new_abstime_expr

    def revise_expr_by_matching_limited_expression(self, exprs: List[AbstimeExpression],  # type: ignore[override]
                                                   expr_id: int,
                                                   matching_expr: AbstimePattern) -> List[AbstimeExpression]:
        """マッチした絶対時間表現の補正を行う.

        Parameters
        ----------
        exprs : List[AbstimeExpression]
            抽出された絶対時間表現
        expr_id : int
            どの絶対時間表現に着目するかのID（インデックス）
        matching_expr : AbstimePattern
            マッチした表現辞書パターン

        Returns
        -------
        List[AbstimeExpression]
            補正済みの絶対時間表現
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
            new_exprs[expr_id] = self.revise_abstime_expr_by_process_type(
                new_exprs[expr_id], process_type
            )
        new_exprs[expr_id].ordinary = matching_expr.ordinary
        new_exprs[expr_id].options.append(matching_expr.option)

        min_id = expr_id + 1
        max_id = expr_id + matching_expr.total_number_of_place_holder
        return [x[1] for x in filter(lambda x: min_id > x[0] or x[0] > max_id, enumerate(new_exprs))]

    def revise_expr_by_matching_prefix_counter(self, expr: AbstimeExpression,  # type: ignore[override]
                                               matching_expr: AbstimePattern) -> AbstimeExpression:
        """マッチした単位表現から絶対時間表現の補正を行う.

        Parameters
        ----------
        expr : AbstimeExpression
            抽出された絶対時間表現
        matching_expr : AbstimePattern
            マッチした表現辞書パターン

        Returns
        -------
        AbstimeExpression
            補正済みの絶対時間表現
        """
        # 一致したパターンに応じて、規格化を行う（数字の前側に単位等が来る場合。絶対時間表現の場合「西暦」など）
        new_expr = deepcopy(expr)
        if matching_expr.option == "seireki":
            tmp = int(matching_expr.process_type[0])
            new_expr.value_lower_bound.year += tmp
            new_expr.value_upper_bound.year += tmp
        elif matching_expr.option == "gogo":
            new_expr.value_lower_bound.hour += 12
            new_expr.value_upper_bound.hour += 12
        elif matching_expr.option == "gozen":
            # 特に操作することはないのでpass
            pass
        else:
            new_expr.options.append(matching_expr.option)

        new_expr.position_start -= len(matching_expr.pattern)

        return new_expr

    def revise_expr_by_number_modifier(self, expr: AbstimeExpression,  # type: ignore[override] # noqa: C901
                                       number_modifier: NumberModifier) -> AbstimeExpression:
        """マッチした修飾表現から絶対時間表現の補正を行う.

        Parameters
        ----------
        expr : AbstimeExpression
            抽出された絶対時間表現
        number_modifier : NumberModifier
            マッチした修飾表現

        Returns
        -------
        AbstimeExpression
            補正後の絶対時間表現
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
        elif number_modifier.process_type == "about":
            val_lb, val_ub = self.do_time_about(new_expr)
            new_expr.value_lower_bound = val_lb
            new_expr.value_upper_bound = val_ub
        elif number_modifier.process_type == "zenhan":
            val_lb, val_ub = self.do_time_zenhan(new_expr)
            new_expr.value_lower_bound = val_lb
            new_expr.value_upper_bound = val_ub
        elif number_modifier.process_type == "nakaba":
            val_lb, val_ub = self.do_time_nakaba(new_expr)
            new_expr.value_lower_bound = val_lb
            new_expr.value_upper_bound = val_ub
        elif number_modifier.process_type == "kouhan":
            val_lb, val_ub = self.do_time_kouhan(new_expr)
            new_expr.value_lower_bound = val_lb
            new_expr.value_upper_bound = val_ub
        elif number_modifier.process_type == "joujun":
            val_lb, val_ub = self.do_time_joujun(new_expr)
            new_expr.value_lower_bound = val_lb
            new_expr.value_upper_bound = val_ub
        elif number_modifier.process_type == "tyujun":
            val_lb, val_ub = self.do_time_tyujun(new_expr)
            new_expr.value_lower_bound = val_lb
            new_expr.value_upper_bound = val_ub
        elif number_modifier.process_type == "gejun":
            val_lb, val_ub = self.do_time_gejun(new_expr)
            new_expr.value_lower_bound = val_lb
            new_expr.value_upper_bound = val_ub
        elif number_modifier.process_type == "made":
            if new_expr.value_upper_bound == new_expr.value_lower_bound:
                # 「3時までに来てください」のような場合
                new_expr.value_lower_bound = NTime(INF)
            else:
                # 「2時～3時までに来てくださいの場合 -> 何もしない
                pass
        elif number_modifier.process_type == "none":
            pass
        else:
            new_expr.options.append(number_modifier.process_type)

        return new_expr

    def delete_not_expression(self,  # type: ignore[override]
                              exprs: List[AbstimeExpression]) -> List[AbstimeExpression]:
        """時間オブジェクトがNullの絶対時間表現を削除する.

        Parameters
        ----------
        exprs : List[AbstimeExpression]
            抽出された絶対時間表現

        Returns
        -------
        List[AbstimeExpression]
            削除後の絶対時間表現
        """
        for i in range(len(exprs)):
            if self.normalizer_utility.is_null_time(exprs[i].value_lower_bound) \
                    and self.normalizer_utility.is_null_time(exprs[i].value_upper_bound):
                exprs[i] = None  # type: ignore

        return [expr for expr in exprs if expr]

    def fix_by_range_expression(self,  # type: ignore[override]
                                text: str, exprs: List[AbstimeExpression]) -> List[AbstimeExpression]:
        """絶対時間の範囲表現の修正を行う.

        Parameters
        ----------
        text : str
            元のテキスト
        exprs : List[AbstimeExpression]
            抽出された絶対時間表現

        Returns
        -------
        List[AbstimeExpression]
            修正後の絶対時間表現
        """
        for i in range(len(exprs) - 1):
            if exprs[i] is None \
                    or not self.have_kara_suffix(exprs[i].options) \
                    or not self.have_kara_prefix(exprs[i+1].options) \
                    or exprs[i].position_end + 2 < exprs[i+1].position_start:
                continue

            # 「4~12月」「4月3~4日」の場合、前者（後者）がそもそも時間表現として認識されてないので、時間表現として設定する
            exprs[i], exprs[i+1] = self.abstime_info2null_abstime(exprs[i], exprs[i+1])

            # 「2012/4/3~4/5」のような場合、どちらも時間表現として認識されているが、後者で情報が欠落しているので、これを埋める
            exprs[i], exprs[i+1] = self.supplement_abstime_info(exprs[i], exprs[i+1])

            # 範囲表現として設定する
            exprs[i].value_upper_bound = exprs[i+1].value_upper_bound
            exprs[i].position_end = exprs[i+1].position_end
            exprs[i].set_original_expr_from_position(text)
            exprs[i].options = self.merge_options(exprs[i].options, exprs[i+1].options)

            # i+1番目は使わないのでNoneにする -> あとでfilterでキレイにする
            exprs[i+1] = None  # type: ignore

        return [expr for expr in exprs if expr]

    def do_time_about(self, abstime_expr: AbstimeExpression) -> Tuple[NTime, NTime]:
        """about表現の場合の日付計算を行う.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            計算対象の絶対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
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

    def do_time_zenhan(self, abstime_expr: AbstimeExpression) -> Tuple[NTime, NTime]:
        """前半表現の場合の日付計算を行う.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            計算対象の絶対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb)
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
        """後半表現の場合の日付計算を行う.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            計算対象の絶対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb)
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
        """半ば表現の場合の日付計算を行う.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            計算対象の絶対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb)
        if target_time_position == "y":
            if val_lb.year != val_ub.year:
                # 「18世紀中盤」のような場合
                tmp = (val_ub.year - val_lb.year) // 4
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

    def do_time_joujun(self, abstime_expr: AbstimeExpression) -> Tuple[NTime, NTime]:
        """上旬表現の場合の日付計算を行う.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            計算対象の絶対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb)
        if target_time_position == "m":
            val_lb.day = 1
            val_ub.day = 10

        return val_lb, val_ub

    def do_time_tyujun(self, abstime_expr: AbstimeExpression) -> Tuple[NTime, NTime]:
        """中旬表現の場合の日付計算を行う.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            計算対象の絶対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb)
        if target_time_position == "m":
            val_lb.day = 11
            val_ub.day = 20

        return val_lb, val_ub

    def do_time_gejun(self, abstime_expr: AbstimeExpression) -> Tuple[NTime, NTime]:
        """下旬表現の場合の日付計算を行う.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            計算対象の絶対時間表現

        Returns
        -------
        Tuple[NTime, NTime]
            計算後の日付情報
        """
        val_lb = abstime_expr.value_lower_bound
        val_ub = abstime_expr.value_upper_bound
        target_time_position = self.normalizer_utility.identify_time_detail(val_lb)
        if target_time_position == "m":
            val_lb.day = 21
            val_ub.day = 31

        return val_lb, val_ub

    def abstime_info2null_abstime(self, abstime1: AbstimeExpression, abstime2: AbstimeExpression) \
            -> Tuple[AbstimeExpression, AbstimeExpression]:
        """連続する時間表現から時間表現として認識されていない部分を時間表現として修正する.

        Parameters
        ----------
        abstime1 : AbstimeExpression
            i番目の絶対時間表現
        abstime2 : AbstimeExpression
            i+1番目の絶対時間表現

        Returns
        -------
        Tuple[AbstimeExpression, AbstimeExpression]
            修正後のi番目とi+1番目の絶対時間表現
        """
        if abstime1.value_lower_bound == NTime(INF):
            # lower_boundが空 = 時間として認識されていない場合（例：「4~12月」の「4~」）、lower_boundを設定
            # TODO 本当は、[i+1]の最上位時間単位を指定したいので、最下位時間単位を返すidentify_time_detailを用いるのは誤り
            # -> このパターンのとき、2つ以上の時間単位がでてくることは考えられないので、とりあえずこの実装でOK
            target_time_position = self.normalizer_utility.identify_time_detail(abstime2.value_upper_bound)
            abstime1 = self.set_time(abstime1, target_time_position, deepcopy(abstime1))
        elif abstime2.value_upper_bound == NTime(-INF):
            # upper_boundが空 = 時間として認識されていない場合（例：「2012/4/3~6」の「~6」）、upper_boundを設定
            abstime2.value_upper_bound = abstime1.value_upper_bound
            target_time_position = self.normalizer_utility.identify_time_detail(abstime1.value_upper_bound)
            abstime2 = self.set_time(abstime2, target_time_position, deepcopy(abstime2))

        return abstime1, abstime2

    def set_time(self, abstime_expr: AbstimeExpression, time_position: str,
                 integrate_abstime_expr: AbstimeExpression) -> AbstimeExpression:
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
        """
        new_abstime_expr = deepcopy(abstime_expr)
        if time_position == "y":
            new_abstime_expr.value_lower_bound.year = integrate_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.year = integrate_abstime_expr.org_value_upper_bound
        elif time_position == "m":
            new_abstime_expr.value_lower_bound.month = integrate_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.month = integrate_abstime_expr.org_value_upper_bound
        elif time_position == "d":
            new_abstime_expr.value_lower_bound.day = integrate_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.day = integrate_abstime_expr.org_value_upper_bound
        elif time_position == "h":
            new_abstime_expr.value_lower_bound.hour = integrate_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.hour = integrate_abstime_expr.org_value_upper_bound
        elif time_position == "mn":
            new_abstime_expr.value_lower_bound.minute = integrate_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.minute = integrate_abstime_expr.org_value_upper_bound
        elif time_position == "s":
            new_abstime_expr.value_lower_bound.second = integrate_abstime_expr.org_value_lower_bound
            new_abstime_expr.value_upper_bound.second = integrate_abstime_expr.org_value_upper_bound
        elif time_position == "seiki":
            new_abstime_expr.value_lower_bound.year = integrate_abstime_expr.org_value_lower_bound * 100 - 99
            new_abstime_expr.value_upper_bound.year = integrate_abstime_expr.org_value_upper_bound * 100

        return new_abstime_expr

    def supplement_abstime_info(self, abstime1: AbstimeExpression,  # noqa: C901
                                abstime2: AbstimeExpression) -> Tuple[AbstimeExpression, AbstimeExpression]:
        """連続する時間表現で欠落している情報を補完する.

        Parameters
        ----------
        abstime1 : AbstimeExpression
            i番目の絶対時間表現
        abstime2 : AbstimeExpression
            i+1番目の絶対時間表現

        Returns
        -------
        Tuple[AbstimeExpression, AbstimeExpression]
            補完後のi番目とi+1番目の絶対時間表現
        """
        new_abstime1 = deepcopy(abstime1)
        new_abstime2 = deepcopy(abstime2)

        if self.is_abstime_val_inf(abstime1.value_lower_bound.year, abstime1.value_upper_bound.year):
            new_abstime1.value_lower_bound.year = abstime2.value_lower_bound.year
            new_abstime1.value_upper_bound.year = abstime2.value_upper_bound.year
        if self.is_abstime_val_inf(abstime2.value_lower_bound.year, abstime2.value_upper_bound.year):
            new_abstime2.value_lower_bound.year = abstime1.value_lower_bound.year
            new_abstime2.value_upper_bound.year = abstime1.value_upper_bound.year
        if self.is_abstime_val_inf(abstime1.value_lower_bound.month, abstime1.value_upper_bound.month):
            new_abstime1.value_lower_bound.month = abstime2.value_lower_bound.month
            new_abstime1.value_upper_bound.month = abstime2.value_upper_bound.month
        if self.is_abstime_val_inf(abstime2.value_lower_bound.month, abstime2.value_upper_bound.month):
            new_abstime2.value_lower_bound.month = abstime1.value_lower_bound.month
            new_abstime2.value_upper_bound.month = abstime1.value_upper_bound.month
        if self.is_abstime_val_inf(abstime1.value_lower_bound.day, abstime1.value_upper_bound.day):
            new_abstime1.value_lower_bound.day = abstime2.value_lower_bound.day
            new_abstime1.value_upper_bound.day = abstime2.value_upper_bound.day
        if self.is_abstime_val_inf(abstime2.value_lower_bound.day, abstime2.value_upper_bound.day):
            new_abstime2.value_lower_bound.day = abstime1.value_lower_bound.day
            new_abstime2.value_upper_bound.day = abstime1.value_upper_bound.day
        if self.is_abstime_val_inf(abstime1.value_lower_bound.hour, abstime1.value_upper_bound.hour):
            new_abstime1.value_lower_bound.hour = abstime2.value_lower_bound.hour
            new_abstime1.value_upper_bound.hour = abstime2.value_upper_bound.hour
        if self.is_abstime_val_inf(abstime2.value_lower_bound.hour, abstime2.value_upper_bound.hour):
            new_abstime2.value_lower_bound.hour = abstime1.value_lower_bound.hour
            new_abstime2.value_upper_bound.hour = abstime1.value_upper_bound.hour
        if self.is_abstime_val_inf(abstime1.value_lower_bound.minute, abstime1.value_upper_bound.minute):
            new_abstime1.value_lower_bound.minute = abstime2.value_lower_bound.minute
            new_abstime1.value_upper_bound.minute = abstime2.value_upper_bound.minute
        if self.is_abstime_val_inf(abstime2.value_lower_bound.minute, abstime2.value_upper_bound.minute):
            new_abstime2.value_lower_bound.minute = abstime1.value_lower_bound.minute
            new_abstime2.value_upper_bound.minute = abstime1.value_upper_bound.minute
        if self.is_abstime_val_inf(abstime1.value_lower_bound.second, abstime1.value_upper_bound.second):
            new_abstime1.value_lower_bound.second = abstime2.value_lower_bound.second
            new_abstime1.value_upper_bound.second = abstime2.value_upper_bound.second
        if self.is_abstime_val_inf(abstime2.value_lower_bound.second, abstime2.value_upper_bound.second):
            new_abstime2.value_lower_bound.second = abstime1.value_lower_bound.second
            new_abstime2.value_upper_bound.second = abstime1.value_upper_bound.second

        return new_abstime1, new_abstime2

    def is_abstime_val_inf(self, time_elem_lower_bound: float,
                           time_elem_upper_bound: float) -> bool:
        """絶対時間表現の特定の値が無限がどうかを判定する.

        Parameters
        ----------
        time_elem_lower_bound : float
            絶対時間表現の下限の値
        time_elem_upper_bound : float
            絶対時間表現の上限の値

        Returns
        -------
        bool
            True：無限、False：無限でない
        """
        return time_elem_lower_bound == INF and time_elem_upper_bound == -INF
