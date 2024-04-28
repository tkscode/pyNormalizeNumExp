"""各種数値表現の抽出・正規化を行う処理の定義モジュール."""
from dataclasses import asdict, dataclass, field
from typing import Optional, Union, cast

from .expression.abstime import AbstimeExpression
from .expression.base import NormalizedExpression, NTime
from .expression.duration import DurationExpression
from .expression.numerical import NumericalExpression
from .expression.reltime import ReltimeExpression
from .normalizer.abstime_expr_normalizer import AbstimeExpressionNormalizer
from .normalizer.duration_expr_normalizer import DurationExpressionNormalizer
from .normalizer.inappropriate_expr_remover import InappropriateExpressionRemover
from .normalizer.numerical_expr_normalizer import NumericalExpressionNormalizer
from .normalizer.reltime_expr_normalizer import ReltimeExpressionNormalizer
from .utility.custom_type import ReturnExpressionDict
from .utility.dict_loader import DictLoader


@dataclass
class Time:
    """時間保持用クラス."""

    year: Union[int, float]
    month: Union[int, float]
    day: Union[int, float]
    hour: Union[int, float]
    minute: Union[int, float]
    second: Union[int, float]


@dataclass
class Expression:
    """抽出・正規化済みの数値表現クラス.

    Parameters
    ----------
    type : str
        表現種別
    original_expr : str
        表現の文字列
    position_start : int
        開始位置
    position_end : int
        終了位置
    counter : str
        単位
    value_lower_bound : Union[int, float, Time]
        数量・絶対時間・期間の下限
    value_upper_bound : Union[int, float, Time]
        数量・絶対時間・期間の上限
    value_lower_bound_abs : Time
        相対時間表現における絶対時間の下限
    value_upper_bound_abs : Time
        相対時間表現における絶対時間の上限
    value_lower_bound_rel : Time
        相対時間表現における相対時間の下限
    value_upper_bound_rel : Time
        相対時間表現における相対時間の上限
    options : List[str]
        オプション
    """

    type: str = ""
    original_expr: str = ""
    position_start: int = -1
    position_end: int = -1
    counter: str = ""
    value_lower_bound: Optional[Union[int, float, Time]] = None
    value_upper_bound: Optional[Union[int, float, Time]] = None
    value_lower_bound_abs: Optional[Time] = None
    value_upper_bound_abs: Optional[Time] = None
    value_lower_bound_rel: Optional[Time] = None
    value_upper_bound_rel: Optional[Time] = None
    options: list[str] = field(default_factory=list)


class NormalizeNumexp(object):
    """各種数値表現の抽出・正規化を行うクラス."""

    def __init__(self, language: str, custom_dict_file: Optional[str] = None) -> None:
        """コンストラクタ.

        Parameters
        ----------
        language : str
            利用する言語（ja）
        custom_dict_file : Optional[str]
            カスタム辞書のファイルパス, default None
        """
        dict_loader = DictLoader(language, custom_dict_file)

        self.numerical_expr_normalizer = NumericalExpressionNormalizer(dict_loader)
        self.abstime_expr_normalizer = AbstimeExpressionNormalizer(dict_loader)
        self.reltime_expr_normalizer = ReltimeExpressionNormalizer(dict_loader)
        self.duration_expr_normalizer = DurationExpressionNormalizer(dict_loader)
        self.inappropriate_expr_remover = InappropriateExpressionRemover(dict_loader)

    def normalize(self, text: str, as_dict: bool = False) -> Union[list[Expression], list[ReturnExpressionDict]]:
        """各種数値表現の抽出・正規化を行う.

        Parameters
        ----------
        text : str
            抽出対象のテキスト
        as_dict : bool, optional
            dict型で結果を返すかどうか（デフォルト：False＝dict型にしない）

        Returns
        -------
        Union[list[Expression], list[ReturnExpressionDict]]
            抽出・正規化した数値表現
        """
        # 各normalizerで数値表現の抽出・正規化を行う
        numerical_exprs = cast(list[NumericalExpression], self.numerical_expr_normalizer.process(text))
        abstime_exprs = cast(list[AbstimeExpression], self.abstime_expr_normalizer.process(text))
        reltime_exprs = cast(list[ReltimeExpression], self.reltime_expr_normalizer.process(text))
        duration_exprs = cast(list[DurationExpression], self.duration_expr_normalizer.process(text))

        # 不適切な数値表現を削除する
        numerical_exprs, abstime_exprs, reltime_exprs, duration_exprs \
            = self.inappropriate_expr_remover.remove_inappropriate_extraction(
                text, numerical_exprs, abstime_exprs, reltime_exprs, duration_exprs)

        # 統一的な数値表現オブジェクトに変換する
        exprs = self.merge_expressions(numerical_exprs, abstime_exprs, reltime_exprs, duration_exprs)

        if as_dict:
            # asdictでdataclassオブジェクトをdict型に変換する
            return [cast(ReturnExpressionDict, asdict(expr)) for expr in exprs]

        return exprs

    def merge_expressions(self, numerical_exprs: list[NumericalExpression], abstime_exprs: list[AbstimeExpression],
                          reltime_exprs: list[ReltimeExpression], duration_exprs: list[DurationExpression]) \
            -> list[Expression]:
        """抽出した各種数値表現を統一的な数値表現オブジェクトに変換する.

        Parameters
        ----------
        numerical_exprs : list[NumericalExpression]
            数量表現
        abstime_exprs : list[AbstimeExpression]
            絶対時間表現
        reltime_exprs : list[ReltimeExpression]
            相対時間表現
        duration_exprs : list[DurationExpression]
            期間表現

        Returns
        -------
        list[Expression]
            変換後の数値表現
        """
        def conv_time_obj(bound: Optional[NTime]) -> Optional[Time]:
            if bound is None:
                return None

            return Time(year=bound.year, month=bound.month, day=bound.day,
                        hour=bound.hour, minute=bound.minute, second=bound.second)

        total_exprs: list[Expression] = []

        for numerical_expr in numerical_exprs:
            expr = Expression()
            expr.type = "numerical"
            expr.original_expr = numerical_expr.original_expr
            expr.position_start = numerical_expr.position_start
            expr.position_end = numerical_expr.position_end
            expr.counter = numerical_expr.counter
            expr.value_lower_bound = numerical_expr.value_lower_bound
            expr.value_upper_bound = numerical_expr.value_upper_bound
            expr.options = self.show_options(numerical_expr)

            total_exprs.append(expr)

        for abstime_expr in abstime_exprs:
            expr = Expression()
            expr.type = "abstime"
            expr.original_expr = abstime_expr.original_expr
            expr.position_start = abstime_expr.position_start
            expr.position_end = abstime_expr.position_end
            expr.counter = "none"
            expr.value_lower_bound = conv_time_obj(abstime_expr.value_lower_bound)
            expr.value_upper_bound = conv_time_obj(abstime_expr.value_upper_bound)
            expr.options = self.show_options(abstime_expr)

            total_exprs.append(expr)

        for reltime_expr in reltime_exprs:
            expr = Expression()
            expr.type = "reltime"
            expr.original_expr = reltime_expr.original_expr
            expr.position_start = reltime_expr.position_start
            expr.position_end = reltime_expr.position_end
            expr.counter = "none"
            expr.value_lower_bound_abs = conv_time_obj(reltime_expr.value_lower_bound_abs)
            expr.value_upper_bound_abs = conv_time_obj(reltime_expr.value_upper_bound_abs)
            expr.value_lower_bound_rel = conv_time_obj(reltime_expr.value_lower_bound_rel)
            expr.value_upper_bound_rel = conv_time_obj(reltime_expr.value_upper_bound_rel)
            expr.value_upper_bound = conv_time_obj(reltime_expr.value_upper_bound)
            expr.options = self.show_options(reltime_expr)

            total_exprs.append(expr)

        for duration_expr in duration_exprs:
            expr = Expression()
            expr.type = "duration"
            expr.original_expr = duration_expr.original_expr
            expr.position_start = duration_expr.position_start
            expr.position_end = duration_expr.position_end
            expr.counter = "none"
            expr.value_lower_bound = conv_time_obj(duration_expr.value_lower_bound)
            expr.value_upper_bound = conv_time_obj(duration_expr.value_upper_bound)
            expr.options = self.show_options(duration_expr)

            total_exprs.append(expr)

        return list(sorted(total_exprs, key=lambda x: x.position_start))

    def show_options(self, expr: NormalizedExpression) -> list[str]:
        """optionsを整理.

        Parameters
        ----------
        expr : NormalizedExpression
            任意の数値表現

        Returns
        -------
        list[str]
            整理したoptions
        """
        options: list[str] = []
        if expr.ordinary:
            options.append("ordinary")

        for opt in expr.options:
            if len(opt) == 0:
                continue

            options.append(opt)

        return options
