"""時間系以外の数値表現表現クラスの定義モジュール."""
import typing

from .base import LimitedExpression


class Counter(LimitedExpression):
    """時間系以外の数値表現表現クラス."""

    def __init__(self) -> None:
        """コンストラクタ."""
        super().__init__()

        self.counter = ""
        self.si_prefix = -1
        self.optional_power_of_ten = -1

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, Counter) and super().__eq__(o) \
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
