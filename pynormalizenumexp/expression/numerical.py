"""時間系以外の数値表現定義モジュール."""
import typing
from typing import Any

from .base import BasePattern, NNumber, NormalizedExpression


class NumericalPattern(BasePattern):
    """時間系以外の数値表現表現クラス."""

    def __init__(self) -> None:
        """コンストラクタ."""
        super().__init__()

        self.counter = ""
        self.si_prefix = -1
        self.optional_power_of_ten = -1

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, NumericalPattern) and super().__eq__(o) \
            and self.si_prefix == o.si_prefix \
            and self.optional_power_of_ten == o.optional_power_of_ten

    @typing.no_type_check
    def __str__(self) -> str:  # noqa: D105
        params = super().__str__(only_params=True)
        params.update({
            "si_prefix": self.si_prefix,
            "optional_power_of_ten": self.optional_power_of_ten
        })
        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'{self.__class__}({str_params})'


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

    def __init__(self, *args: Any) -> None:  # type: ignore
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
