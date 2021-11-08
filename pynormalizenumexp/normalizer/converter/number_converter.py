"""数値文字列を数値に変換する処理の基底クラス定義モジュール."""
from typing import List, Tuple
from unicodedata import normalize

from pynormalizenumexp.utility.digit_utility import DigitUtility


class NumberConverter(object):
    """数値文字列を数値に変換する処理の基底クラス."""

    def __init__(self, digit_utility: DigitUtility) -> None:
        """コンストラクタ.

        Parameters
        ----------
        digit_utility : DigitUtility
            数字操作ユーティリティ
        """
        self.digit_utility = digit_utility

    def convert_number(self, number_string: str) -> int:
        """数値文字列を数値に変換する.

        Parameters
        ----------
        number_string : str
            変換対象の数値文字列

        Returns
        -------
        int
            変換後の数値
        """
        new_number_string = self.delete_connma(number_string)
        new_number_string = normalize("NFKC", new_number_string)

        splitted_number_string = self.split_by_kansuji_kurai(new_number_string)

        value = 0
        number_converted = 0
        for each_number_string, kurai in splitted_number_string:
            number_converted = self.convert_arabic_kansuji_mixed_of_4digits(each_number_string)
            if number_converted == 0 and kurai != "　":
                if value == 0:
                    # 「万」や「億」が単体で出てくる場合
                    number_converted = 1
                else:
                    # 「1億万」など「億」「万」で区切った際に数字がない場合
                    # -> TODO 処理するケースがあるか不明のため何もしない
                    pass

            n_pow = self.digit_utility.kansuji_kurai2power_value(kurai)
            value += number_converted * (10 ** n_pow)
            number_converted = 0

        return value

    def delete_connma(self, number_string: str) -> str:
        """文字列からコンマ表記を削除する.

        Parameters
        ----------
        number_string : str
            削除対象の文字列

        Returns
        -------
        str
            削除後の文字列
        """
        return "".join(["" if self.digit_utility.is_comma(char) else char for char in number_string])

    def split_by_kansuji_kurai(self, number_string: str) -> List[Tuple[str, str]]:
        """文字列を位表記で分割する.

        Parameters
        ----------
        number_string : str
            分割対象の文字列

        Returns
        -------
        List[Tuple[str, str]]
            分割後の文字列
        """
        splitted_number_string = []
        temp_string = ""
        for char in number_string:
            if self.digit_utility.is_kansuji_kurai_man(char):
                splitted_number_string.append((temp_string, char))
                temp_string = ""
            else:
                temp_string += char

        splitted_number_string.append((temp_string, "　"))

        return splitted_number_string

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
        raise NotImplementedError()
