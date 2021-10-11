from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pynormalizenumexp.utility import PLACE_HOLDER


INF = float("inf")


class NotationType(Enum):
    NOT_NUMBER = 0
    KANSUJI_09 = 1
    KANSUJI_KURAI_SEN = 2
    KANSUJI_KURAI_MAN = 4
    KANSUJI_KURAI = 6
    KANSUJI = 7
    ZENKAKU = 8
    HANKAKU = 16


class BaseExpression(object):
    original_expr: str
    position_start: int
    position_end: int
    pattern: str
    value_lower_bound: Union[float, Optional[datetime]]
    value_upper_bound: Union[float, Optional[datetime]]


class LimitedExpression(BaseExpression):
    ordinary: bool
    option: str
    # patternが含むPLACE_HOLDERの数（*月*日 -> 2個）
    total_number_of_place_holder: int
    # pattern中の最後のPLACE_HOLDERの後に続く文字列の長さ（*月*日 -> 1）
    # -> positionの同定に必要
    len_of_after_final_place_holder: int

    def set_total_number_of_place_holder(self):
        self.total_number_of_place_holder = self.pattern.count(PLACE_HOLDER)

    def set_len_of_after_final_place_holder(self):
        try:
            idx = self.pattern.index(PLACE_HOLDER)
            self.len_of_after_final_place_holder = len(self.pattern[idx:])
        except ValueError:
            # PLACE_HOLDERがない場合はindex関数の仕様によりValueErrorが発生する
            self.len_of_after_final_place_holder = len(self.pattern)


class NNumber(BaseExpression):
    def __init__(self, original_expr: str = "", position_start: int = -1, position_end: int = -1) -> None:
        self.original_expr = original_expr
        self.position_start = position_start
        self.position_end = position_end

        self.value_lower_bound: float = INF
        self.value_upper_bound: float = -INF
        self.notation_type: List[NotationType] = []


class NormalizedExpression(BaseExpression):
    def __init__(self, original_expr: str, position_start: int, position_end: int) -> None:
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
        if len(text) < self.position_end:
            return

        self.original_expr = text[self.position_start:self.position_end]


class NumberModifier(NormalizedExpression):
    def __init__(self, pattern: str, process_type: str) -> None:
        self.pattern = pattern
        self.process_type = process_type
