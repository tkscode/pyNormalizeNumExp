import json
import os
from importlib.resources import open_text
from typing import List

from pynormalizenumexp.expression import LimitedAbstimeExpression

from .base import BaseNormalizer


class AbstimeExpressionNormalizer(BaseNormalizer):
    def __init__(self, language: str):
        self.number_normalizer = None
        self.language = language

        self.setup()

    def setup(self):
        self.load_dictionaries("abstime_expression.json", "abstime_prefix_counter.json",
                               "abstime_prefix.json", "abstime_suffix.json")

    def load_limited_expr_dict(self, dict_path: str) -> List[LimitedAbstimeExpression]:
        load_target: List[LimitedAbstimeExpression] = []
        with open_text("pynormalizenumexp", os.path.join(self.BASE_DICT_DIR, self.language, dict_path)) as fp:
            dict_obj = json.load(fp)
            for pattern in dict_obj["patterns"]:
                expr = LimitedAbstimeExpression()
                expr.pattern = pattern["pattern"]
                expr.corresponding_time_position = pattern["corresponding_time_position"]
                expr.process_type = pattern["process_type"]
                expr.ordinary = pattern["ordinary"]
                expr.option = pattern["option"]

                load_target.append(expr)

        return load_target
