"""時間系以外の数値表現定義モジュール."""
import typing
from typing import Any

from .base import NNumber, NormalizedExpression


class NumericalExpression(NormalizedExpression):
    """時間系以外の数値表現クラス."""

    value_lower_bound: float
    value_upper_bound: float

    @typing.overload
    def __init__(self, original_expr: str, position_start: int, position_end: int,
                 value_lower_bound: float, value_upper_bound: float) -> None:
        """コンストラクタ."""
        ...

    @typing.overload
    def __init__(self, number: NNumber) -> None:
        """コンストラクタ."""
        ...

    def __init__(self, args: Any) -> None:  # type: ignore
        """コンストラクタ."""
        try:
            original_expr, position_start, position_end, value_lower_bound, value_upper_bound = args

            super().__init__(original_expr, position_start, position_end)
            self.value_lower_bound = value_lower_bound
            self.value_upper_bound = value_upper_bound
        except ValueError:
            number: NNumber = args[0]
            super().__init__(number.original_expr, number.position_start, number.position_end)
            self.value_lower_bound = number.value_lower_bound
            self.value_upper_bound = number.value_upper_bound

        self.counter = ""
        self.ordinary = False

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, NumericalExpression) and super().__eq__(o) \
            and self.counter == o.counter

    @typing.no_type_check
    def __str__(self, only_params: bool = False) -> str:  # noqa: D105
        params = super().__str__(only_params=True)
        params.update({
            "counter": self.counter
        })
        if only_params:
            return params

        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'{self.__class__}({str_params})'
