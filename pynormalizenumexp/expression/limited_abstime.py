from typing import List

from .base import LimitedExpression


class LimitedAbstimeExpression(LimitedExpression):
    corresponding_time_position: List[str] = []
    process_type: List[str] = []
