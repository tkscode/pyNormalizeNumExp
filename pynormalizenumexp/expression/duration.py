"""絶対時間の表現定義モジュール."""
import typing
from typing import List, Union

from .base import INF, BasePattern, NNumber, NormalizedExpression, NTime


class DurationPattern(BasePattern):
    """パターン辞書用の相対時間表現クラス."""

    def __init__(self) -> None:
        """コンストラクタ."""
        super().__init__()

        self.corresponding_time_position: List[str] = []
        self.process_type: List[str] = []

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, DurationPattern) and super().__eq__(o) \
            and self.corresponding_time_position == o.corresponding_time_position \
            and self.process_type == o.process_type

    @typing.no_type_check
    def __str__(self) -> str:  # noqa: D105
        params = super().__str__(only_params=True)
        params.update({
            "corresponding_time_position": self.corresponding_time_position,
            "process_type": self.process_type
        })
        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'{self.__class__}({str_params})'


class DurationExpression(NormalizedExpression):
    """期間の表現クラス."""

    value_lower_bound: NTime
    value_upper_bound: NTime
    org_value_lower_bound: Union[int, float]
    org_value_upper_bound: Union[int, float]

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
        self.value_lower_bound = NTime(INF)
        self.value_upper_bound = NTime(-INF)
        self.ordinary = False

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, DurationExpression) and super().__eq__(o) \
            and self.org_value_lower_bound == o.org_value_lower_bound \
            and self.org_value_upper_bound == o.org_value_upper_bound

    @typing.no_type_check
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
