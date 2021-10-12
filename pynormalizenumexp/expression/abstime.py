"""絶対時間の表現定義モジュール."""
from datetime import datetime
from typing import Optional

from .base import NNumber, NormalizedExpression


class AbstimeExpression(NormalizedExpression):
    """絶対時間の表現クラス."""

    def __init__(self, number: NNumber):
        """コンスタラクタ.

        Parameters
        ----------
        number : NNumber
            数値表現
        """
        super().__init__(number.original_expr, number.position_start, number.position_end)

        self.org_value_lower_bound = number.value_lower_bound
        self.org_value_upper_bound = number.value_upper_bound
        self.value_lower_bound: Optional[datetime] = None
        self.value_upper_bound: Optional[datetime] = None
        self.ordinary = False
