from .normalizer import AbstimeExpressionNormalizer
from .utility import DictLoader


class NormalizeNumexp(object):
    def __init__(self, language: str):
        dict_loader = DictLoader(language)

        # self.numerical_expr_normalizer =
        self.abstime_expr_normalizer = AbstimeExpressionNormalizer(dict_loader)

    def normalize(self, text: str):
        pass

    def normalize_data(self, text: str):
        pass
