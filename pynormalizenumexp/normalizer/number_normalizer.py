from typing import Any, List, Optional

from pynormalizenumexp.expression import NNumber
from pynormalizenumexp.utility import DigitUtility


class NumberNormalizer(object):
    inf_number_converter: Optional[Any] = None

    def __init__(self, language: str) -> None:
        self.language = language
        self.digit_utility = DigitUtility()
        self.digit_utility.init_kansuji()
        # self.number_extractor = NumberExtractor(self.digit_utility)
        # self.symbol_fixer = SymbolFixer(self.digit_utility)

    def process(self, input: str) -> List[NNumber]:
        pass

    # 絶対時間表現の規格化の際に使用する（絶対時間表現では、前もって記号を処理させないため）
    def process_dont_fix_by_symbol(self, input: str) -> List[NNumber]:
        pass
