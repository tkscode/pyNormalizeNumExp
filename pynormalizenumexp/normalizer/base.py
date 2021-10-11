import json
import os
from importlib.resources import open_text
from typing import List

import pynormalizenumexp
from pynormalizenumexp.expression import LimitedExpression, NNumber, NumberModifier


class BaseNormalizer(object):
    BASE_DICT_DIR = "resources/dict/"
    language: str = ""
    limited_expressions: List[LimitedExpression] = []
    prefix_counters: List[LimitedExpression] = []
    prefix_number_modifier: List[NumberModifier] = []
    suffix_number_modifier: List[NumberModifier] = []

    def setup(self):
        raise NotImplementedError()

    def load_limited_expr_dict(self, dict_path: str) -> List[LimitedExpression]:
        raise NotImplementedError()

    def load_number_modifier_dict(self, dict_path: str) -> List[NumberModifier]:
        with open_text(pynormalizenumexp.__package__, os.path.join(self.BASE_DICT_DIR, self.language, dict_path)) as fp:
            dict_obj = json.load(fp)
            load_target = [NumberModifier(pattern["pattern"], pattern["process_type"])
                           for pattern in dict_obj["patterns"]]

        return load_target

    def load_dictionaries(self, limited_expr_dict_path: str, prefix_counter_dict_path: str,
                          prefix_number_modifier_dict_path: str, suffix_number_modifier_dict_path: str) -> None:
        self.limited_expressions = self.load_limited_expr_dict(limited_expr_dict_path)
        self.prefix_counters = self.load_limited_expr_dict(prefix_counter_dict_path)
        self.prefix_number_modifier = self.load_number_modifier_dict(prefix_number_modifier_dict_path)
        self.suffix_number_modifier = self.load_number_modifier_dict(suffix_number_modifier_dict_path)

    def normalize_number(self, text: str, numbers: List[NNumber]) -> None:
        raise NotImplementedError()
