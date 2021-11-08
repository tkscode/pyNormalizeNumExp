"""各種表現パターンクラスの定義モジュール."""
import typing
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# 定数定義
INF = float("inf")
PLACE_HOLDER = "ǂ"


class NotationType(Enum):
    """数値表現の列挙クラス."""

    NOT_NUMBER = 0
    KANSUJI_09 = 1
    KANSUJI_KURAI_SEN = 2
    KANSUJI_KURAI_MAN = 4
    KANSUJI_KURAI = 6
    KANSUJI = 7
    ZENKAKU = 8
    HANKAKU = 16


class NTime:
    """時間情報を保持するためのクラス."""

    @typing.overload
    def __init__(self, value: Union[int, float]) -> None:
        """コンストラクタ."""
        ...

    @typing.overload
    def __init__(self, year: Union[int, float], month: Union[int, float], day: Union[int, float],
                 hour: Union[int, float], minute: Union[int, float], second: Union[int, float]) -> None:
        """コンストラクタ."""
        ...

    def __init__(self, *args) -> None:  # type: ignore
        """コンストラクタ."""
        try:
            self.year, self.month, self.day, self.hour, self.minute, self.second = args
        except ValueError:
            self.year = self.month = self.day = self.hour = self.minute = self.second = args[0]

    def __eq__(self, o: object) -> bool:  # noqa: D105
        if not isinstance(o, NTime):
            return False

        return o.year == self.year and o.month == self.month and o.day == self.day \
            and o.hour == self.hour and o.minute == self.minute and o.second == self.second

    @typing.no_type_check
    def __str__(self, only_params: bool = False) -> Union[str, Dict[str, int]]:  # noqa: D105
        params = {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second
        }
        if only_params:
            return params

        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'NTime({str_params})'

    @typing.no_type_check
    def __repr__(self) -> str:  # noqa: D105
        return self.__str__()

    # def is_null(self, val: float) -> bool:  # noqa: D102
    #     return val == INF or val == -INF

    # def to_date_str(self, is_upper_bound: bool) -> str:  # noqa: D102
    #     if self.is_null(self.year):
    #         return "INF" if is_upper_bound else "-INF"

    #     s = [
    #         f'{self.year:04}',
    #         "XX" if self.is_null(self.month) else f'{self.month:02}',
    #         "XX" if self.is_null(self.day) else f'{self.day:02}'
    #     ]

    #     return "/".join(s)

    # def to_time_str(self, is_upper_bound: bool) -> str:  # noqa: D102
    #     if self.is_null(self.hour):
    #         return "INF" if is_upper_bound else "-INF"

    #     s = [
    #         f'{self.hour:02}',
    #         "XX" if self.is_null(self.minute) else f'{self.minute:02}',
    #         "XX" if self.is_null(self.second) else f'{self.second:02}'
    #     ]

    #     return ":".join(s)

    # def to_str(self, is_upper_bound: bool) -> str:  # noqa: D102
    #     if self.is_null(self.year) and self.is_null(self.month) and self.is_null(self.day):
    #         return self.to_time_str(is_upper_bound)

    #     return self.to_date_str(is_upper_bound)


class BaseExpression(object):
    """各種表現の基底クラス."""

    def __init__(self) -> None:
        """コンストラクタ."""
        self.original_expr: str = ""
        self.position_start: int = -1
        self.position_end: int = -1
        self.pattern: str = ""
        self.value_lower_bound: Optional[Union[float, NTime]] = None
        self.value_upper_bound: Optional[Union[float, NTime]] = None

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, BaseExpression) \
            and self.original_expr == o.original_expr \
            and self.position_start == o.position_start \
            and self.position_end == o.position_end \
            and self.pattern == o.pattern \
            and self.value_lower_bound == o.value_lower_bound \
            and self.value_upper_bound == o.value_upper_bound

    @typing.no_type_check
    def __str__(self, only_params: bool = False) -> Union[str, Dict[str, Any]]:  # noqa: D105
        params = {
            "original_expr": self.original_expr,
            "position_start": self.position_start,
            "position_end": self.position_end,
            "pattern": self.pattern,
            "value_lower_bound": self.value_lower_bound,
            "value_upper_bound": self.value_upper_bound
        }
        if only_params:
            return params

        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'{self.__class__}({str_params})'


class BasePattern(BaseExpression):
    """パターン辞書用の各種表現の基底クラス."""

    def __init__(self) -> None:
        """コンストラクタ."""
        super().__init__()

        self.ordinary: bool = False
        self.option: str = ""
        # patternが含むPLACE_HOLDERの数（*月*日 -> 2個）
        self.total_number_of_place_holder: int = 0
        # pattern中の最後のPLACE_HOLDERの後に続く文字列の長さ（*月*日 -> 1）
        # -> positionの同定に必要
        self.len_of_after_final_place_holder: int = 0

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, BasePattern) and super().__eq__(o) \
            and self.ordinary == o.ordinary \
            and self.option == o.option \
            and self.total_number_of_place_holder == o.total_number_of_place_holder \
            and self.len_of_after_final_place_holder == o.len_of_after_final_place_holder

    @typing.no_type_check
    def __str__(self, only_params: bool = False) -> str:  # noqa: D105
        params = super().__str__(only_params=True)
        params.update({
            "ordinary": self.ordinary,
            "option": self.option,
            "total_number_of_place_holder": self.total_number_of_place_holder,
            "len_of_after_final_place_holder": self.len_of_after_final_place_holder
        })
        if only_params:
            return params

        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'{self.__class__}({str_params})'

    def set_total_number_of_place_holder(self) -> None:
        """パターン文字列中に出現したPlace holderをカウント."""
        if self.pattern:
            self.total_number_of_place_holder = self.pattern.count(PLACE_HOLDER)

    def set_len_of_after_final_place_holder(self) -> None:
        """パターン文字列中にPlace holderが最後に出現した位置より後のパターン文字列の長さを取得."""
        if self.pattern:
            idx = self.pattern.rfind(PLACE_HOLDER)
            if idx > -1:
                self.len_of_after_final_place_holder = len(self.pattern[idx+1:])
            else:
                self.len_of_after_final_place_holder = len(self.pattern)


class NNumber(BaseExpression):
    """任意の数値表現のクラス."""

    value_lower_bound: Union[int, float]
    value_upper_bound: Union[int, float]

    def __init__(self, original_expr: str = "", position_start: int = -1, position_end: int = -1) -> None:
        """コンストラクタ.

        Parameters
        ----------
        original_expr : str, optional
            数値表現文字列, by default ""
        position_start : int, optional
            表現の開始位置, by default -1
        position_end : int, optional
            表現の終了位置, by default -1
        """
        super().__init__()

        self.original_expr = original_expr
        self.position_start = position_start
        self.position_end = position_end

        self.value_lower_bound = INF
        self.value_upper_bound = -INF
        self.notation_type: List[NotationType] = []

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, NNumber) and super().__eq__(o) \
            and self.notation_type == o.notation_type

    @typing.no_type_check
    def __str__(self, only_params: bool = False) -> str:  # noqa:D105
        params = super().__str__(only_params=True)
        params.update({"notation_type": self.notation_type})
        if only_params:
            return params

        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'{self.__class__}({str_params})'


class NormalizedExpression(BaseExpression):
    """各種正規化表現の基底クラス."""

    def __init__(self, original_expr: str, position_start: int, position_end: int) -> None:
        """コンストラクタ.

        Parameters
        ----------
        original_expr : str
            正規化表現文字列
        position_start : int
            表現の開始位置
        position_end : int
            表現の終了位置
        """
        super().__init__()

        self.original_expr = original_expr
        self.position_start = position_start
        self.position_end = position_end

        self.number_notation_type: NotationType = NotationType.NOT_NUMBER
        self.include_lower_bound: bool = True
        self.include_upper_bound: bool = True
        self.is_over: bool = False
        self.is_less: bool = False
        self.ordinary: bool = False
        self.options: List[str] = []

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, NormalizedExpression) and super().__eq__(o) \
            and self.number_notation_type == o.number_notation_type \
            and self.include_lower_bound == o.include_lower_bound \
            and self.include_upper_bound == o.include_upper_bound \
            and self.is_over == o.is_over \
            and self.is_less == o.is_less \
            and self.ordinary == o.ordinary \
            and self.options == o.options

    @typing.no_type_check
    def __str__(self, only_params: bool = False) -> str:  # noqa: D105
        params = super().__str__(only_params=True)
        params.update({
            "number_notation_type": self.number_notation_type,
            "include_lower_bound": self.include_lower_bound,
            "include_upper_bound": self.include_upper_bound,
            "is_over": self.is_over,
            "is_less": self.is_less,
            "ordinary": self.ordinary,
            "options": self.options
        })
        if only_params:
            return params

        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'{self.__class__}({str_params})'

    def set_original_expr_from_position(self, text: str) -> None:
        """与えられたテキストから開始・終了位置を使って表現を抽出する.

        Parameters
        ----------
        text : str
            抽出対象のテキスト
        """
        if len(text) < self.position_end:
            return

        self.original_expr = text[self.position_start:self.position_end]


class NumberModifier(NormalizedExpression):
    """修飾表現用クラス."""

    def __init__(self, pattern: str, process_type: str) -> None:
        """コンストラクタ.

        Parameters
        ----------
        pattern : str
            パターン文字列
        process_type : str
            パターン種別
        """
        self.pattern = pattern
        self.process_type = process_type

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, NumberModifier) \
            and self.pattern == o.pattern \
            and self.process_type == o.process_type

    @typing.no_type_check
    def __str__(self, only_params: bool = False) -> str:  # noqa: D105
        params = {
            "pattern": self.pattern,
            "process_type": self.process_type
        }
        if only_params:
            return params

        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'{self.__class__}({str_params})'
