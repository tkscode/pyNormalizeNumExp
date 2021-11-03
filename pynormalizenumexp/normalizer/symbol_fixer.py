"""数値表現に関わる表記（プラスマイナスや小数点、カンマ、範囲文字など）を考慮した数値表現の変換処理定義モジュール."""
from copy import deepcopy
from typing import List, Optional

from pynormalizenumexp.expression.base import INF, NNumber
from pynormalizenumexp.utility.digit_utility import DigitUtility


class SymbolFixer(object):
    """数値表現に関わる表記（プラスマイナスや小数点、カンマ、範囲文字など）を考慮した数値表現の変換処理クラス."""

    def __init__(self, digit_utility: DigitUtility) -> None:
        """コンストラクタ.

        Parameters
        ----------
        digit_utility : DigitUtility
            文字列処理用ユーティリティ
        """
        self.digit_utility = digit_utility

    def fix_numbers_by_symbol(self, text: str, numbers: List[NNumber]) -> List[NNumber]:
        """数値表現のPrefixや数値表現間の表現を考慮した表現の修正を行う.

        Parameters
        ----------
        text : str
            元のテキスト
        numbers : List[NNumber]
            抽出された数値表現

        Returns
        -------
        List[NNumber]
            修正後の数値表現
        """
        new_numbers = deepcopy(numbers)
        i = 0
        while i < len(new_numbers):
            number = new_numbers[i]

            # prefixの修正
            fixed_number = self.fix_prefix_symbol(text, number)
            new_numbers[i] = fixed_number

            # 1つ後の数値表現と組み合わせた修正
            if i + 1 < len(new_numbers):
                fixed_number = self.fix_intermediate_symbol(text, new_numbers[i], new_numbers[i+1])
                # 修正がされていれば1つ後の数値表現は不要なので削除する
                if fixed_number.original_expr != new_numbers[i].original_expr:
                    new_numbers[i] = fixed_number
                    del(new_numbers[i+1])

            i += 1

        return new_numbers

    def extract_plus(self, text: str, i: int) -> Optional[str]:
        """プラス表現であれば該当部分を抽出する.

        Parameters
        ----------
        text : str
            抽出対象のテキスト
        i : int
            テキスト中文字列のi番目

        Returns
        -------
        Optional[str]
            抽出したプラス表現
        """
        if i < 0:
            return None
        elif text[i] == "+" or text[i] == "＋":
            return text[i]
        elif i < 2:
            return None
        elif text[i-2:i+1] == "プラス":
            return text[i-2:i+1]
        else:
            return None

    def extract_minus(self, text: str, i: int) -> Optional[str]:
        """マイナス表現であれば該当部分を抽出する.

        Parameters
        ----------
        text : str
            抽出対象のテキスト
        i : int
            テキスト中文字列のi番目

        Returns
        -------
        Optional[str]
            抽出したマイナス表現
        """
        if i < 0:
            return None
        elif text[i] == "-" or text[i] == "－" or text[i] == "ー":
            return text[i]
        elif i < 3:
            return None
        elif text[i-3:i+1] == "マイナス":
            return text[i-3:i+1]
        else:
            return None

    def create_decimal_value(self, number: NNumber) -> float:
        """小数点以下の文字列を数値に変換する.

        Parameters
        ----------
        number : NNumber
            数値表現

        Returns
        -------
        float
            変換後の数値
        """
        decimal = number.value_lower_bound

        # 1より小さくなるまで0.1を乗算する
        while decimal >= 1:
            decimal *= 0.1

        pos = 0
        while True:
            if len(number.original_expr) <= pos:
                break

            char = number.original_expr[pos]
            if char != "0" and char != "０" and char != "零" and char != "〇":
                break

            # 1.001のような0が含まれる表記のため、先頭のゼロの分0.1を乗算する
            decimal *= 0.1
            pos += 1

        return decimal

    def fix_decimal_point(self, number: NNumber, next_number: NNumber, decimal_string: str) -> NNumber:
        """1つ後の数値表現と合わせて小数表現に変換する.

        Parameters
        ----------
        number : NNumber
            注目する数値表現
        next_number : NNumber
            1つ後の数値表現
        decimal_string : str
            小数点文字

        Returns
        -------
        NNumber
            変換後の数値表現
        """
        new_number = deepcopy(number)

        # 3.14などの小数点以下の文字列（14）を数値（0.14）に変換する
        decimal = self.create_decimal_value(next_number)
        new_number.value_lower_bound += decimal

        # 9.3万などの末尾の位表記を数値に変換して計算する
        char = next_number.original_expr[-1]
        if self.digit_utility.is_kansuji_kurai_man(char):
            power_value = self.digit_utility.kansuji_kurai2power_value(char)
            new_number.value_lower_bound *= 10 ** power_value

        new_number.value_upper_bound = new_number.value_lower_bound
        new_number.original_expr += decimal_string + next_number.original_expr
        new_number.position_end = next_number.position_end

        return new_number

    def fix_range_expression(self, number: NNumber, next_number: NNumber, range_string: str) -> NNumber:
        """1つ後の数値表現と合わせて範囲表現に変換する.

        Parameters
        ----------
        number : NNumber
            注目する数値表現
        next_number : NNumber
            1つ後の数値表現
        range_string : str
            2つの数値表現を連結する範囲文字（「～」など）

        Returns
        -------
        NNumber
            変換後の数値表現
        """
        new_number = deepcopy(number)
        new_number.value_upper_bound = next_number.value_lower_bound
        new_number.original_expr += range_string + next_number.original_expr
        new_number.position_end = next_number.position_end

        return new_number

    def fix_prefix_symbol(self, text: str, number: NNumber) -> NNumber:
        """数値表現の前にプラス/マイナス表現があればそれを付加する.

        Parameters
        ----------
        text : str
            元のテキスト
        number : NNumber
            数値表現

        Returns
        -------
        NNumber
            プラス/マイナス表現を付加した数値表現
        """
        new_number = deepcopy(number)

        plus_expr = self.extract_plus(text, number.position_start-1)
        if plus_expr:
            new_number.original_expr = plus_expr + number.original_expr
            new_number.position_start -= len(plus_expr)

            return new_number

        minus_expr = self.extract_minus(text, number.position_start-1)
        if minus_expr:
            new_number.original_expr = minus_expr + number.original_expr
            new_number.value_lower_bound *= -1
            new_number.value_upper_bound *= -1
            new_number.position_start -= len(minus_expr)

            return new_number

        return new_number

    def fix_intermediate_symbol(self, text: str, number: NNumber, next_number: NNumber) -> NNumber:
        """2つの数値表現の間にある記号などに応じて数値表現をマージする.

        Parameters
        ----------
        text : str
            元のテキスト
        number : NNumber
            注目する数値表現
        next_number : NNumber
            1つ後の数値表現

        Returns
        -------
        NNumber
            マージ後の数値表現
        """
        i = number.position_end
        j = next_number.position_start

        if i > j:
            return number

        intermediate = text[i:j]
        if len(intermediate) == 0:
            return number

        if number.value_lower_bound == INF or next_number.value_lower_bound == INF:
            return number

        if self.digit_utility.is_decimal_point(intermediate[0]):
            # 小数点があれば2つの数値表現を連結して小数の数値表現にする
            fixed_number = self.fix_decimal_point(number, next_number, intermediate[0])
            return fixed_number

        if self.digit_utility.is_range_expression(intermediate) \
            or (self.digit_utility.is_comma(intermediate[0])
                and len(intermediate) == 1
                and number.value_lower_bound == next_number.value_upper_bound - 1):
            # カンマの並列表現（1,2など）や範囲表現があれば2つの数値表現を連結して1つの数値表現にする
            fixed_number = self.fix_range_expression(number, next_number, intermediate)
            return fixed_number

        return number
