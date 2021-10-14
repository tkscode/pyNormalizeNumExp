from pynormalizenumexp.utility.digit_utility import DigitUtility

from .number_converter import NumberConverter


class JapaneseNumberConverter(NumberConverter):
    def __init__(self, digit_utility: DigitUtility) -> None:
        super().__init__(digit_utility)

    def convert_arabic_kansuji_mixed_of_4digits(self):
        pass
