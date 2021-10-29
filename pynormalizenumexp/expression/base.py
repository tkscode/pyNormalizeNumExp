"""各種表現パターンクラスの定義モジュール."""
from datetime import datetime
from enum import Enum
from typing import Final, List, Optional, Union

from pynormalizenumexp.utility.custom_type import NTimeInitDict

# 定数定義
INF: Final[float] = float("inf")
PLACE_HOLDER: Final[str] = "ǂ"


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


class BaseExpression(object):
    """各種表現の基底クラス."""

    original_expr: str
    position_start: int
    position_end: int
    pattern: str
    value_lower_bound: Union[float, Optional[datetime]]
    value_upper_bound: Union[float, Optional[datetime]]


class LimitedExpression(BaseExpression):
    """狭義の各種表現の基底クラス."""

    ordinary: bool
    option: str
    # patternが含むPLACE_HOLDERの数（*月*日 -> 2個）
    total_number_of_place_holder: int
    # pattern中の最後のPLACE_HOLDERの後に続く文字列の長さ（*月*日 -> 1）
    # -> positionの同定に必要
    len_of_after_final_place_holder: int

    def set_total_number_of_place_holder(self):
        """パターン文字列中に出現したPlace holderをカウント."""
        self.total_number_of_place_holder = self.pattern.count(PLACE_HOLDER)

    def set_len_of_after_final_place_holder(self):
        """パターン文字列中にPlace holderが最後に出現した位置より後のパターン文字列の長さを取得."""
        idx = self.pattern.rfind(PLACE_HOLDER)
        if idx > -1:
            self.len_of_after_final_place_holder = len(self.pattern[idx:])
        else:
            self.len_of_after_final_place_holder = len(self.pattern)


class NNumber(BaseExpression):
    """任意の数値表現のクラス."""

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
        self.original_expr = original_expr
        self.position_start = position_start
        self.position_end = position_end

        self.value_lower_bound: float = INF
        self.value_upper_bound: float = -INF
        self.notation_type: List[int] = []

    def __eq__(self, o: object) -> bool:
        """=演算子用の処理定義.

        Parameters
        ----------
        o : object
            比較対象のオブジェクト

        Returns
        -------
        bool
            比較結果（True：一致、False：不一致）
        """
        if not isinstance(o, NNumber):
            return False

        return o.original_expr == self.original_expr \
            and o.position_start == self.position_start and o.position_end == self.position_end \
            and o.value_lower_bound == self.value_lower_bound and self.value_upper_bound == self.value_upper_bound \
            and o.notation_type == self.notation_type


class NTime(object):
    """時間情報を保持するためのクラス."""

    def __init__(self, **kwargs: NTimeInitDict):
        """コンストラクタ."""
        if "value" in kwargs:
            self.year = self.month = self.day = self.hour = self.minute = self.second = kwargs["value"]
        else:
            self.year = kwargs["year"]
            self.month = kwargs["month"]
            self.day = kwargs["day"]
            self.hour = kwargs["hour"]
            self.minute = kwargs["minute"]
            self.second = kwargs["second"]

    def __eq__(self, o: object) -> bool:
        """=演算子による評価処理.

        Parameters
        ----------
        o : object
            評価対象のオブジェクト

        Returns
        -------
        bool
            等価かどうか
        """
        if not isinstance(o, NTime):
            return False

        return o.year == self.year and o.month == self.month and o.day == self.day \
            and o.hour == self.hour and o.minute == self.minute and o.second == self.second


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
        self.original_expr = original_expr
        self.position_start = position_start
        self.position_end = position_end

        self.number_notation_type: int = NotationType.NOT_NUMBER
        self.include_lower_bound: bool = True
        self.include_upper_bound: bool = True
        self.is_over: bool = False
        self.is_less: bool = False
        self.ordinary: bool = False
        self.options: List[str] = []

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
        self.pattern = pattern
        self.process_type = process_type
