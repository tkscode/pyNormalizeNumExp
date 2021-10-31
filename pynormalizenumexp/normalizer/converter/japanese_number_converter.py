"""日本語の数値文字列を数値に変換するクラスの定義モジュール."""
from pynormalizenumexp.utility.digit_utility import DigitUtility

from .number_converter import NumberConverter


class JapaneseNumberConverter(NumberConverter):
    """日本語の数値文字列を数値に変換するクラス."""

    def __init__(self, digit_utility: DigitUtility) -> None:
        """コンストラクタ.

        Parameters
        ----------
        digit_utility : DigitUtility
            数字操作ユーティリティ
        """
        super().__init__(digit_utility)

    def convert_arabic_kansuji_mixed_of_4digits(self, number_string: str) -> int:
        """アラビア数字や漢数字からなる数値文字列を数値に変換する.

        Parameters
        ----------
        number_string : str
            変換対象の文字列

        Returns
        -------
        int
            変換後の数値
        """
        number_converted = 0
        temp_num = 0
        for char in number_string:
            if self.digit_utility.is_kansuji_kurai_sen(char):
                if temp_num == 0:
                    temp_num = 1

                number_converted += temp_num * (10 ** self.digit_utility.kansuji_kurai2power_value(char))
                temp_num = 0
            elif self.digit_utility.is_kansuji09(char):
                temp_num = temp_num * 10 + self.digit_utility.kansuji_09_to_value[char]
            elif self.digit_utility.is_hankakusuji(char):
                temp_num = temp_num * 10 + int(char)

        if temp_num != 0:
            number_converted += temp_num

        return number_converted
