from typing import List

from pynormalizenumexp.expression import LimitedExpression, NNumber, NumberModifier
from pynormalizenumexp.utility import DictLoader


class BaseNormalizer(object):
    def __init__(self, dict_loader: DictLoader) -> None:
        self.dict_loader = dict_loader

        self.limited_expressions: List[LimitedExpression] = []
        self.prefix_counters: List[LimitedExpression] = []
        self.prefix_number_modifier: List[NumberModifier] = []
        self.suffix_number_modifier: List[NumberModifier] = []

    def load_dictionaries(self, limited_expr_dict_path: str, prefix_counter_dict_path: str,
                          prefix_number_modifier_dict_path: str, suffix_number_modifier_dict_path: str) -> None:
        raise NotImplementedError()

    def normalize_number(self, text: str, numbers: List[NNumber]) -> None:
        raise NotImplementedError()
