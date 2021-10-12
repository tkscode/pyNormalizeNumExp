"""狭義の絶対時間表現クラスの定義モジュール."""
from typing import List

from .base import LimitedExpression


class LimitedAbstimeExpression(LimitedExpression):
    """狭義の絶対時間表現クラス."""

    corresponding_time_position: List[str] = []
    process_type: List[str] = []
