"""数値表現のノーマライザ定義モジュール."""
from copy import deepcopy
from typing import Any, List, Optional

from pynormalizenumexp.expression.base import NNumber
from pynormalizenumexp.utility.dict_loader import DictLoader
from pynormalizenumexp.utility.digit_utility import DigitUtility

from .number_extractor import NumberExtractor
from .symbol_fixer import SymbolFixer


class NumberNormalizer(object):
    """数値表現のノーマライザクラス."""

    inf_number_converter: Optional[Any] = None

    def __init__(self, dict_loader: DictLoader) -> None:
        """コンストラクタ.

        Parameters
        ----------
        dict_loader : DictLoader
            辞書ファイルのローダー
        """
        self.digit_utility = DigitUtility(dict_loader)
        self.digit_utility.init_kansuji()
        self.number_extractor = NumberExtractor(self.digit_utility)
        self.symbol_fixer = SymbolFixer(self.digit_utility)
        if dict_loader.language == "ja":
            from .converter.japanese_number_converter import JapaneseNumberConverter
            self.number_converter = JapaneseNumberConverter(self.digit_utility)
        else:
            raise ValueError(f'Not supported language "{dict_loader.language}"')

    def process(self, input: str, do_fix_symbol: bool = True) -> List[NNumber]:
        """テキストから数値表現を抽出し、正規化する.

        Parameters
        ----------
        input : str
            入力テキスト
        do_fix_symbol : bool, optional
            記号の処理を行うかのフラグ（True：行う、False：行わない）, by default True
            絶対時間表現の場合はFalseにする

        Returns
        -------
        List[NNumber]
            抽出・正規化した数値表現
        """
        # 入力文に含まれる数値表現を抽出
        numbers = self.number_extractor.extract_number(input)

        # コンマがある場合、数値表現を連結する
        numbers = self.join_numbers_by_comma(input, numbers)

        # 数値表現を数値に変換する
        numbers = self.convert_number(numbers)

        # 「数万」などの「数」表現を数値に変換する
        # TODO fix_symbolとマージ
        numbers = self.fix_numbers_by_su(input, numbers)

        # 「京」「万」など「万」以上の桁区切り文字しかないものを削除
        numbers = self.remove_only_kansuji_kurai_man(numbers)

        # 絶対時間表現の規格化の際は実行しない（絶対時間表現では、前もって記号を処理させないため）
        if do_fix_symbol:
            # 記号の処理を行う
            numbers = self.symbol_fixer.fix_numbers_by_symbol(input, numbers)

        # 不要なデータを削除
        numbers = self.remove_unnecessary_data(numbers)

        return numbers

    def suffix_is_arabic(self, number_string: str) -> bool:
        """数値文字列の末尾がアラビア数字かどうか判定する.

        Parameters
        ----------
        number_string : str
            判定対象の数値文字列

        Returns
        -------
        bool
            True：末尾がアラビア数字、False：末尾がアラビア数字でない
        """
        return len(number_string) > 0 and self.digit_utility.is_arabic(number_string[-1])

    def prefix_3digits_is_arabic(self, number_string: str) -> bool:
        """数値文字列の先頭3文字がアラビア数字かどうか判定する.

        Parameters
        ----------
        number_string : str
            判定対象の数字文字列

        Returns
        -------
        bool
            True：先頭三文字がアラビア数字、False：先頭三文字がアラビア数字でない
        """
        return len(number_string) > 2 and all([self.digit_utility.is_arabic(char) for char in number_string[:3]])

    def is_valid_comma_notation(self, number_string1: str, number_string2: str) -> bool:
        """2つの連続する数値文字列がコンマで連結可能か判定する.

        Parameters
        ----------
        number_string1 : str
            数値文字列の片方
        number_string2 : str
            数値文字列のもう片方

        Returns
        -------
        bool
            True：連結可能、False：連結不可

        Notes
        -----
            「3,000」などの3桁ごとにコンマがある場合はOK。「29,30」のようなものはNG。
        """
        return self.suffix_is_arabic(number_string1) \
            and self.prefix_3digits_is_arabic(number_string2) \
            and (len(number_string2) == 3 or not self.digit_utility.is_arabic(number_string2[3]))

    def join_numbers_by_comma(self, text: str, numbers: List[NNumber]) -> List[NNumber]:
        """コンマで連結できる数値表現があれば連結する.

        Parameters
        ----------
        text : str
            元のテキスト
        numbers : List[NNumber]
            数値表現

        Returns
        -------
        List[NNumber]
            コンマで連結したものを含む数値表現
        """
        new_numbers = deepcopy(numbers)
        for i in list(reversed(range(1, len(new_numbers)))):
            a = new_numbers[i-1].position_end
            b = new_numbers[i].position_start - 1
            if a != b:
                continue

            char_intermediate = text[a]
            if not self.digit_utility.is_comma(char_intermediate):
                # 1つ前の数値表現の末尾がコンマでなければ次へ
                continue
            if not self.is_valid_comma_notation(new_numbers[i-1].original_expr, new_numbers[i].original_expr):
                # 連続する数値表現がコンマで連結できなければ次へ
                continue

            new_numbers[i-1].position_end = new_numbers[i].position_end
            new_numbers[i-1].original_expr += char_intermediate + new_numbers[i].original_expr
            # i番目は不要なので削除する
            # -> iはnew_numbersの後ろから見ているので削除しても整合性は保たれる
            del(new_numbers[i])

        return new_numbers

    def convert_number(self, numbers: List[NNumber]) -> List[NNumber]:
        """数値表現を数値に変換する.

        Parameters
        ----------
        numbers : List[NNumber]
            変換対象の数値表現

        Returns
        -------
        List[NNumber]
            変換後の数値表現
        """
        new_numbers = deepcopy(numbers)
        for i, number in enumerate(new_numbers):
            converted_number = self.number_converter.convert_number(number.original_expr)
            new_numbers[i].value_lower_bound = converted_number
            new_numbers[i].value_upper_bound = converted_number

        return new_numbers

    def fix_prefix_su(self, text: str, number: NNumber) -> NNumber:
        """数値先頭の冒頭に出現する「数」表現を数値に変換する.

        Parameters
        ----------
        text : str
            元のテキスト
        number : NNumber
            変換対象の数値表現

        Returns
        -------
        NNumber
            変換後の数値表現

        Notes
        -----
            「数十万円」「数万円」「数十円」といった表現の処理を行う
        """
        if number.position_start == 0:
            return number
        if text[number.position_start-1] != "数":
            return number

        new_number = deepcopy(number)

        # 「数」の範囲の操作
        new_number.value_upper_bound *= 9

        new_number.position_start -= 1
        new_number.original_expr = "数" + new_number.original_expr

        return new_number

    def fix_intermediate_su(self, text: str, cur_number: NNumber, next_number: NNumber) -> NNumber:
        """数値表現中に出現する「数」表現を数値に変換する.

        Parameters
        ----------
        text : str
            元のテキスト
        cur_number : NNumber
            注目する数値表現
        next_number : NNumber
            1つ後の数値表現

        Returns
        -------
        NNumber
            変換後の数値表現

        Notes
        -----
            「十数万円」といった表現の処理を行う
        """
        if cur_number.position_end != next_number.position_start - 1:
            return cur_number
        if text[cur_number.position_end] != "数":
            return cur_number

        new_cur_number = deepcopy(cur_number)
        new_next_number = deepcopy(next_number)

        # 「数」の範囲の操作
        # new_cur_number.valueを、new_next_number.valueのスケールに合わせる
        while True:
            if new_next_number.value_lower_bound < new_cur_number.value_lower_bound:
                break

            new_cur_number.value_lower_bound *= 10 ** 4
            if new_cur_number.value_lower_bound <= 0:
                # 「0数万」のような場合
                return new_cur_number

        new_cur_number.value_upper_bound = new_cur_number.value_lower_bound
        # new_next_numberに「数」の処理を行う
        new_next_number.value_upper_bound *= 9
        # 2つの数の範囲をマージ
        new_cur_number.value_lower_bound += new_next_number.value_lower_bound
        new_cur_number.value_upper_bound += new_next_number.value_upper_bound

        new_cur_number.position_end = new_next_number.position_end
        new_cur_number.original_expr += "数" + new_next_number.original_expr

        return new_cur_number

    def fix_suffix_su(self, text: str, number: NNumber) -> NNumber:
        """数値表現の末尾に出現する「数」を数値に変換する.

        Parameters
        ----------
        text : str
            元のテキスト
        number : NNumber
            変換対象の数値表現

        Returns
        -------
        NNumber
            変換後の数値表現

        Notes
        -----
            「十数円」のパターンしかない
        """
        if number.position_end == len(text):
            return number
        if text[number.position_end] != "数":
            return number

        new_number = deepcopy(number)

        new_number.value_upper_bound += 9
        new_number.value_lower_bound += 1
        new_number.original_expr += "数"
        new_number.position_end += 1

        return new_number

    def fix_numbers_by_su(self, text: str, numbers: List[NNumber]) -> List[NNumber]:
        """抽出した各数値表現中に含まれる「数」表現を数値に変換する.

        Parameters
        ----------
        text : str
            元のテキスト
        numbers : List[NNumber]
            変換対象の抽出された数値表現

        Returns
        -------
        List[NNumber]
            変換後の数値表現
        """
        new_numbers = deepcopy(numbers)
        i = 0
        while i < len(new_numbers):
            new_numbers[i] = self.fix_prefix_su(text, new_numbers[i])
            if i < len(new_numbers) - 1:
                new_number = self.fix_intermediate_su(text, new_numbers[i], new_numbers[i+1])
                if new_number != new_numbers[i]:
                    new_numbers[i] = new_number
                    del(new_numbers[i+1])

            new_numbers[i] = self.fix_suffix_su(text, new_numbers[i])

            i += 1

        return new_numbers

    def is_only_kansuji_kurai_man(self, original_expr: str) -> bool:
        """数値文字列の位が万以上のものしかないかを判定.

        Parameters
        ----------
        original_expr : str
            判定対象の数値文字列

        Returns
        -------
        bool
            True：万以上の位しかない、False：そうでない
        """
        for char in original_expr:
            if not self.digit_utility.is_kansuji_kurai_man(char):
                return False

        return True

    def remove_only_kansuji_kurai_man(self, numbers: List[NNumber]) -> List[NNumber]:
        """数値文字列に「万」以上の桁区切り文字しかないものを削除する.

        Parameters
        ----------
        numbers : List[NNumber]
            抽出された数値表現

        Returns
        -------
        List[NNumber]
            削除処理後の数値表現
        """
        new_numbers = deepcopy(numbers)
        for i, number in enumerate(new_numbers):
            if self.is_only_kansuji_kurai_man(number.original_expr):
                new_numbers[i] = None  # type: ignore

        # 逆順にしていたのでもと順番に戻す
        return [number for number in new_numbers if number]

    def remove_unnecessary_data(self, numbers: List[NNumber]) -> List[NNumber]:
        """重複するような不要なデータを削除する.

        Parameters
        ----------
        numbers : List[NNumber]
            抽出された数値表現

        Returns
        -------
        List[NNumber]
            削除処理後の数値表現
        """
        new_numbers: List[NNumber] = []
        position_start = -1
        position_end = -1
        for number in numbers:
            if position_start <= number.position_start and number.position_end <= position_end:
                # 重複は除外
                pass
            elif position_end <= number.position_start:
                new_numbers.append(number)
                position_start = number.position_start
                position_end = number.position_end

        return new_numbers
