"""抽出・正規化した数値表現から不適切なものを除去する処理の定義モジュール."""
import re
import typing
from copy import deepcopy
from typing import Optional, Union
from unicodedata import normalize

from pynormalizenumexp.expression.abstime import AbstimeExpression
from pynormalizenumexp.expression.base import INF, NormalizedExpression, NTime
from pynormalizenumexp.expression.duration import DurationExpression
from pynormalizenumexp.expression.numerical import NumericalExpression
from pynormalizenumexp.expression.reltime import ReltimeExpression
from pynormalizenumexp.utility.dict_loader import DictLoader

INAPPROPRIATE_PREFIX_LIST = ["ver", "ｖｅｒ"]
URL_REG = re.compile(r"https?://[\w!\?/\+\-_~=;\.,\*&@#\$%\(\)'\[\]]+", flags=re.DOTALL)


class InappropriateExpressionRemover(object):
    """抽出・正規化した数値表現から不適切なものを除去するクラス."""

    def __init__(self, dict_loader: DictLoader) -> None:
        """コンストラクタ.

        Parameters
        ----------
        dict_loader : DictLoader
            辞書ファイルのローダー
        """
        self.dict_loader = dict_loader

        self.init_inappropriate_strings()

    def init_inappropriate_strings(self) -> None:
        """不適切な文字列情報の読み込み."""
        inappropriate_strings = self.dict_loader.load_inappropriate_strings_dict("inappropriate_strings.json")
        self.inappropriate_strings: dict[str, bool] = dict()
        for string in inappropriate_strings:
            self.inappropriate_strings[string] = True

    @typing.no_type_check
    def remove_inappropriate_extraction(self, text: str,
                                        numerical_exprs: list[NumericalExpression],
                                        abstime_exprs: list[AbstimeExpression],
                                        reltime_exprs: list[ReltimeExpression],
                                        duration_exprs: list[DurationExpression]) \
            -> tuple[list[NumericalExpression], list[AbstimeExpression], list[ReltimeExpression],
                     list[DurationExpression]]:
        """不適切な数値表現を削除する.

        Parameters
        ----------
        numerical_exprs : list[NumericalExpression]
            時間系以外の数値表現
        abstime_exprs : list[AbstimeExpression]
            絶対時間表現
        reltime_exprs : list[ReltimeExpression]
            相対時間表現
        duration_exprs : list[DurationExpression]
            期間表現

        Returns
        -------
        tuple[list[NumericalExpression], list[AbstimeExpression], list[ReltimeExpression], list[DurationExpression]]
            不適切なものを取り除いた各数値表現
        """
        abstime_exprs = self.delete_inappropriate_abstime_exprs(abstime_exprs)

        numerical_exprs = self.delete_duplicate_extraction(numerical_exprs,
                                                           abstime_exprs+reltime_exprs+duration_exprs)
        reltime_exprs = self.delete_duplicate_extraction(reltime_exprs,
                                                         abstime_exprs+numerical_exprs+duration_exprs)
        duration_exprs = self.delete_duplicate_extraction(duration_exprs,
                                                          abstime_exprs+reltime_exprs+numerical_exprs)
        abstime_exprs = self.delete_duplicate_extraction(abstime_exprs,
                                                         numerical_exprs+reltime_exprs+duration_exprs)

        numerical_exprs = self.delete_inappropriate_extraction_using_dict(text, numerical_exprs)
        abstime_exprs = self.delete_inappropriate_extraction_using_dict(text, abstime_exprs)
        reltime_exprs = self.delete_inappropriate_extraction_using_dict(text, reltime_exprs)
        duration_exprs = self.delete_inappropriate_extraction_using_dict(text, duration_exprs)

        return numerical_exprs, abstime_exprs, reltime_exprs, duration_exprs

    def delete_inappropriate_abstime_exprs(self, abstime_exprs: list[AbstimeExpression]) -> list[AbstimeExpression]:
        """不適切な絶対時間表現を削除する.

        Parameters
        ----------
        abstime_exprs : list[AbstimeExpression]
            抽出した絶対時間表現

        Returns
        -------
        list[AbstimeExpression]
            削除後の絶対時間表現
        """
        new_abstime_exprs = deepcopy(abstime_exprs)
        for i, expr in enumerate(new_abstime_exprs):
            new_abstime_exprs[i] = self.revise_abstime_expr(expr)  # type: ignore

        return [expr for expr in new_abstime_exprs if expr]

    def delete_duplicate_extraction(self, target_exprs: list[NormalizedExpression],
                                    other_exprs: list[NormalizedExpression]) -> list[NormalizedExpression]:
        """重複する数値表現を削除する.

        Parameters
        ----------
        target_exprs : list[NormalizedExpression]
            削除対象を含む数値表現
        other_exprs : list[NormalizedExpression]
            比較する数値表現

        Returns
        -------
        list[NormalizedExpression]
            削除後の数値表現
        """
        for i, target_expr in enumerate(target_exprs):
            # 重複するものは削除対象にする
            if self.is_converted_by_other_type_expressions(target_expr, other_exprs):
                target_exprs[i] = None  # type: ignore

        return [expr for expr in target_exprs if expr]

    def delete_inappropriate_extraction_using_dict(self, text: str,  # noqa: C901
                                                   exprs: list[NormalizedExpression]) -> list[NormalizedExpression]:
        """辞書情報などを使った数値表現の削除.

        Parameters
        ----------
        text : str
            元テキスト
        exprs : list[NormalizedExpression]
            削除対象を含む数値表現

        Returns
        -------
        list[NormalizedExpression]
            削除後の数値表現
        """
        new_exprs = deepcopy(exprs)
        for i, expr in enumerate(new_exprs):
            # 指定した表現文字列のものは削除する
            if expr.original_expr in self.inappropriate_strings:
                new_exprs[i] = None  # type: ignore
                continue

            # 指定したPrefixが付いている表現を削除する
            is_break = False
            for prefix in INAPPROPRIATE_PREFIX_LIST:
                if text[:expr.position_start].endswith(prefix):
                    new_exprs[i] = None  # type: ignore
                    is_break = True
                    break
            if is_break:
                continue

            # URLの一部に表現がある場合は削除する
            url_match = URL_REG.search(normalize("NFKC", text))
            if url_match and (url_match.start() <= expr.position_start and expr.position_end <= url_match.end()):
                new_exprs[i] = None  # type: ignore
                continue

        return [expr for expr in new_exprs if expr]

    def revise_abstime_expr(self, abstime_expr: AbstimeExpression) -> Optional[AbstimeExpression]:
        """絶対時間表現の補正を行う.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            抽出した絶対時間表現

        Returns
        -------
        Optional[AbstimeExpression]
            補正後の絶対時間表現
        """
        new_abstime_expr = self.revise_year(abstime_expr)
        # 「1.2.3」のような表現の場合や時間の範囲がおかしい場合は削除対象になる
        # TODO 1番目を見るだけで良いのか？
        if (len(new_abstime_expr.original_expr) > 1
            and new_abstime_expr.original_expr[1] in ['.', '・', '．', '-', '−', 'ー', '―']) \
            or (self.is_inappropriate_time_value(abstime_expr.value_lower_bound)
                or self.is_inappropriate_time_value(abstime_expr.value_upper_bound)):
            return None

        return new_abstime_expr

    def revise_year(self, abstime_expr: AbstimeExpression) -> AbstimeExpression:
        """絶対時間表現の年の補正を行う.

        Parameters
        ----------
        abstime_expr : AbstimeExpression
            抽出した絶対時間表現

        Returns
        -------
        AbstimeExpression
            補正後の絶対時間表現
        """
        new_abstime_expr = deepcopy(abstime_expr)
        # 「西暦」とついてたら処理を行わない
        if "西" in new_abstime_expr.original_expr:
            return new_abstime_expr

        # 「98年7月21日」などの表記のとき（21 < year < 100 のとき）は、1900を加算する
        # 「01年7月21日」などの表記のとき（0 <= year <= 21 のとき）は、2000を加算する
        # TODO 20という数字は2020年の20から来ているので、年を超すごとに更新する必要あり
        if 21 < new_abstime_expr.value_lower_bound.year < 100:
            new_abstime_expr.value_lower_bound.year += 1900
        elif 0 <= new_abstime_expr.value_lower_bound.year <= 21:
            new_abstime_expr.value_lower_bound.year += 2000

        if 21 < new_abstime_expr.value_upper_bound.year < 100:
            new_abstime_expr.value_upper_bound.year += 1900
        elif 0 <= new_abstime_expr.value_upper_bound.year <= 21:
            new_abstime_expr.value_upper_bound.year += 2000

        return new_abstime_expr

    def is_inappropriate_time_value(self, t: NTime) -> bool:
        """不適切な時間表現か判定する.

        Parameters
        ----------
        t : NTime
            判定対象の時間表現

        Returns
        -------
        bool
            True：不適切、False：不適切でない
        """
        # 年月日時分秒が適切な値の範囲内か調べる
        # 時については「25時」などと表現することがあるため、0～30の範囲か調べている
        def is_out_of_range(x: Union[int, float], a: Union[int, float], b: Union[int, float]) -> bool:
            if x == INF or x == -INF:
                return False

            return x < a or b < x

        return is_out_of_range(t.year, 1, 3000) or is_out_of_range(t.month, 1, 12) or is_out_of_range(t.day, 1, 31) \
            or is_out_of_range(t.hour, 0, 30) or is_out_of_range(t.minute, 0, 59) or is_out_of_range(t.second, 0, 59)

    def is_converted_by_other_type_expressions(self, any_type_expression1: NormalizedExpression,
                                               any_type_expressions2: list[NormalizedExpression]) -> bool:
        """2つの数値表現が重複するかどうか判定する.

        Parameters
        ----------
        any_type_expression1 : NormalizedExpression
            判定対象の数値表現
        any_type_expressions2 : list[NormalizedExpression]
            もう片方の数値表現

        Returns
        -------
        bool
            True：重複する、False：重複しない
        """
        # any_type_expression1の開始位置と終了位置がany_type_expression2の中に含まれる場合は重複するとみなす
        for any_type_expression2 in any_type_expressions2:
            if any_type_expression2.position_start <= any_type_expression1.position_start \
                    and any_type_expression1.position_end <= any_type_expression2.position_end:
                return True

        return False
