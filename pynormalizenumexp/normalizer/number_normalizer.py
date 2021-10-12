"""数値表現のノーマライザ定義モジュール."""
from typing import Any, List, Optional

from pynormalizenumexp.expression import NNumber
from pynormalizenumexp.utility import DictLoader, DigitUtility

from .number_extractor import NumberExtractor


class NumberNormalizer(object):
    """数値表現のノーマライザクラス."""

    inf_number_converter: Optional[Any] = None

    def __init__(self, dict_loader: DictLoader) -> None:
        """コンスタラクタ.

        Parameters
        ----------
        dict_loader : DictLoader
            辞書ファイルのローダー
        """
        self.digit_utility = DigitUtility(dict_loader)
        self.digit_utility.init_kansuji()
        self.number_extractor = NumberExtractor(self.digit_utility)
        # self.symbol_fixer = SymbolFixer(self.digit_utility)

    def process(self, input: str) -> List[NNumber]:
        pass

    # 絶対時間表現の規格化の際に使用する（絶対時間表現では、前もって記号を処理させないため）
    def process_dont_fix_by_symbol(self, input: str) -> List[NNumber]:
        pass
