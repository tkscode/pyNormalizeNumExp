from pynormalizenumexp.utility import DictLoader

from .base import BaseNormalizer


class AbstimeExpressionNormalizer(BaseNormalizer):
    def __init__(self, dict_loader: DictLoader) -> None:
        super().__init__(dict_loader)

        self.number_normalizer = None

        self.load_dictionaries("abstime_expression.json", "abstime_prefix_counter.json",
                               "abstime_prefix.json", "abstime_suffix.json")

    def load_dictionaries(self, limited_expr_dict_file: str, prefix_counter_dict_file: str,
                          prefix_number_modifier_dict_file: str, suffix_number_modifier_dict_file: str) -> None:
        self.limited_expressions = self.dict_loader.load_limited_abstime_expr_dict(limited_expr_dict_file)
        self.prefix_counters = self.dict_loader.load_limited_abstime_expr_dict(prefix_counter_dict_file)
        self.prefix_number_modifier = self.dict_loader.load_number_modifier_dict(prefix_number_modifier_dict_file)
        self.suffix_number_modifier = self.dict_loader.load_number_modifier_dict(suffix_number_modifier_dict_file)

    def revise_any_expr_by_limited_expression(self):
        pass

    def revise_any_expr_by_prefix_counter(self):
        pass

    def delete_not_any_expr(self):
        pass

    def fix_by_range_expression(self):
        pass
