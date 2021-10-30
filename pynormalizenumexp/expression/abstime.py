"""絶対時間の表現定義モジュール."""
from typing import Optional

from .base import NNumber, NormalizedExpression, NTime


class AbstimeExpression(NormalizedExpression):
    """絶対時間の表現クラス."""

    def __init__(self, number: NNumber):
        """コンストラクタ.

        Parameters
        ----------
        number : NNumber
            数値表現
        """
        super().__init__(number.original_expr, number.position_start, number.position_end)

        self.org_value_lower_bound = number.value_lower_bound
        self.org_value_upper_bound = number.value_upper_bound
        self.value_lower_bound: Optional[NTime] = None
        self.value_upper_bound: Optional[NTime] = None
        self.ordinary = False

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, AbstimeExpression) and super().__eq__(o) \
            and self.org_value_lower_bound == o.org_value_lower_bound \
            and self.org_value_upper_bound == o.org_value_upper_bound

    def __str__(self, only_params: bool = False) -> str:  # noqa: D105
        params = super().__str__(only_params=True)
        params.update({
            "org_value_lower_bound": self.org_value_lower_bound,
            "org_value_upper_bound": self.org_value_upper_bound
        })
        if only_params:
            return params

        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'{self.__class__}({str_params})'
