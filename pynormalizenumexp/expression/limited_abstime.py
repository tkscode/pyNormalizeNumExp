"""狭義の絶対時間表現クラスの定義モジュール."""
from typing import List

from .base import LimitedExpression


class LimitedAbstimeExpression(LimitedExpression):
    """狭義の絶対時間表現クラス."""

    def __init__(self):
        """コンストラクタ."""
        super().__init__()

        self.corresponding_time_position: List[str] = []
        self.process_type: List[str] = []

    def __eq__(self, o: object) -> bool:  # noqa: D105
        return isinstance(o, LimitedAbstimeExpression) and super().__eq__(o) \
            and self.corresponding_time_position == o.corresponding_time_position \
            and self.process_type == o.process_type

    def __str__(self) -> str:  # noqa: D105
        params = super().__str__(only_params=True)
        params.update({
            "corresponding_time_position": self.corresponding_time_position,
            "process_type": self.process_type
        })
        str_params = ", ".join([f'{k}={v}' for k, v in params.items()])

        return f'{self.__class__}({str_params})'
