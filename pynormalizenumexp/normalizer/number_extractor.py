"""数値表現の抽出処理の定義モジュール."""
import re
from typing import List

from pynormalizenumexp.expression.base import NNumber, NotationType
from pynormalizenumexp.utility.digit_utility import DigitUtility

INVALID_NOTATION_TYPE_REG = re.compile(f"{NotationType.HANKAKU} {NotationType.ZENKAKU}"
                                       + f"|{NotationType.ZENKAKU} {NotationType.HANKAKU}"
                                       + f"|{NotationType.HANKAKU} {NotationType.KANSUJI_09}"
                                       + f"|{NotationType.KANSUJI_09} {NotationType.HANKAKU}"
                                       + f"|{NotationType.ZENKAKU} {NotationType.KANSUJI_09}"
                                       + f"|{NotationType.KANSUJI_09} {NotationType.ZENKAKU}",
                                       flags=re.DOTALL)


class NumberExtractor(object):
    """数値表現の抽出クラス."""

    def __init__(self, digit_utility: DigitUtility) -> None:
        """コンストラクタ.

        Parameters
        ----------
        digit_utility : DigitUtility
            文字列処理用ユーティリティ
        """
        self.digit_utility = digit_utility

    def is_invalid_notation_type(self, notation_type: List[NotationType]) -> bool:
        """不適切な数字の表記を数字種から判定する.

        Parameters
        ----------
        notation_type : List[NotationType]
            判定対象の数字種

        Returns
        -------
        bool
            True：不適切、False：適切

        Notes
        -----
            「２０００30」や「2000三十」などの、数字の表記が入り乱れているものを見つける
        """
        # notation_typeは数値のリストなので、スペースで結合した文字列にして正規表現でチェックする
        notation_type_str = " ".join([str(n) for n in notation_type])
        if INVALID_NOTATION_TYPE_REG.search(notation_type_str):
            return True

        return False

    def split_number_by_kansuji_kurai(self, number: NNumber) -> List[NNumber]:
        """漢数字の位表記で不適切な箇所ごとに分割する.

        Parameters
        ----------
        number : NNumber
            分割対象の数値表現

        Returns
        -------
        List[NNumber]
            分割後の数値表現

        Notes
        -----
            例：「一万五千七百億」のように「万」のあとに「億」が来るものを「一万五千七百」と「億」に分割する
            Java版の isInvalidKansujiKuraiOrder と同義
        """
        if not any([self.digit_utility.is_kansuji(char) for char in number.original_expr]):
            # 漢数字でない表記の場合は分割できないのでそのままにする
            return [number]

        numbers: List[NNumber] = []
        prev_num_str = ""
        position_start = 0
        for i in range(len(number.notation_type)):
            if number.notation_type[i] == NotationType.KANSUJI_09 \
                    or number.notation_type[i] == NotationType.HANKAKU \
                    or number.notation_type[i] == NotationType.ZENKAKU:
                continue

            # 一の位でない場合（KANSUJI_SEN or KANSUJI_MANの場合）は新たに数値表現を切り出す
            cur_num_str = number.original_expr[position_start:i+1]
            if len(prev_num_str) == 0:
                # 記憶している表現がなければ記憶して次へ
                prev_num_str = cur_num_str
                continue

            # 漢数字の文字列を数値に変換
            prev_kansuji_value = self.digit_utility.kansuji_kurai2power_value(prev_num_str[-1])
            cur_kansuji_value = self.digit_utility.kansuji_kurai2power_value(cur_num_str[-1])
            # 記憶している文字列の数値が新たな文字列の数値より小さい場合（prev:二千 cur:三億 など）
            # -> 漢数字の文字列としてつながることはないため、prev_num_strを新たな数値表現として切り出す
            # -> ただし、百二十万などの場合は分割しない（二万三億のように万以上の位続く場合だけ分割する）
            if prev_kansuji_value == cur_kansuji_value \
                or (prev_kansuji_value < cur_kansuji_value
                    and any([self.digit_utility.is_kansuji_kurai_man(char) for char in prev_num_str])):
                new_num_str = number.original_expr[position_start:i]
                new_position_start = number.position_start + position_start
                new_position_end = new_position_start + len(new_num_str)
                new_number = NNumber(new_num_str, new_position_start, new_position_end)
                new_number.notation_type = number.notation_type[position_start:i]
                numbers.append(new_number)

                position_start = i

            prev_num_str = cur_num_str

        if len(numbers) == 0:
            return [number]

        # 余った部分があれば切り出す
        if numbers[-1].position_end != len(number.notation_type):
            new_num_str = number.original_expr[position_start:]
            new_position_start = numbers[-1].position_end
            new_position_end = new_position_start + len(new_num_str)
            new_number = NNumber(new_num_str, new_position_start, new_position_end)
            new_number.notation_type = number.notation_type[position_start:]
            numbers.append(new_number)

        return numbers

    def split_number_by_notation_type(self, number: NNumber) -> List[NNumber]:
        """数字種が不適切な並びから数値表現を分割する.

        Parameters
        ----------
        number : NNumber
            分割対象の数値表現

        Returns
        -------
        List[NNumber]
            分割後の数値表現

        Notes
        -----
            例：「2000三十」を「2000」と「三十」に分割する
        """
        numbers: List[NNumber] = []
        position_start = 0
        for i in range(1, len(number.notation_type)-1):
            # 数字の表記が入り乱れているか
            if self.is_invalid_notation_type(number.notation_type[i-1:i+1]):
                # 新たに数値表現を切り出す
                new_num_str = number.original_expr[position_start:i]
                new_position_start = number.position_start + position_start
                new_position_end = new_position_start + len(new_num_str)
                new_number = NNumber(new_num_str, new_position_start, new_position_end)
                new_number.notation_type = number.notation_type[position_start:i]
                numbers.append(new_number)

                position_start = i

        if len(numbers) == 0:
            return [number]

        # 余った部分があれば切り出す
        if numbers[-1].position_end != len(number.notation_type):
            new_num_str = number.original_expr[position_start:]
            new_position_start = numbers[-1].position_end
            new_position_end = new_position_start + len(new_num_str)
            new_number = NNumber(new_num_str, new_position_start, new_position_end)
            new_number.notation_type = number.notation_type[position_start:]
            numbers.append(new_number)

        return numbers

    def extract_number(self, text: str) -> List[NNumber]:
        """テキストからの数値表現の抽出.

        Parameters
        ----------
        text : str
            抽出対象のテキスト

        Returns
        -------
        List[NNumber]
            抽出された数値表現情報
        """
        # テキストの各文字がどの数字種にあたるか調べる
        text_notation_type = [self.digit_utility.chars2full_notation_type(char) for char in text]

        # 数字である部分の文字列を抜き出す
        numbers: List[NNumber] = []
        num_str = ""
        i = 0
        while i < len(text):
            if text_notation_type[i] == NotationType.NOT_NUMBER:
                if len(num_str) > 0:
                    number = NNumber(num_str, i-len(num_str), i)
                    number.notation_type = text_notation_type[i-len(num_str):i]
                    numbers.append(number)

                    num_str = ""
            else:
                num_str += text[i]

            i += 1

        if len(num_str) > 0:
            number = NNumber(num_str, i-len(num_str), i)
            number.notation_type = text_notation_type[i-len(num_str):i]
            numbers.append(number)

        # 不適切な数字種の並びから数値表現を分割する
        numbers_notation_type_splitted: List[NNumber] = []
        for number in numbers:
            numbers_notation_type_splitted += self.split_number_by_notation_type(number)

        # 不適切な漢数字の位表記から数値表現を分割する
        numbers_kansuji_kurai_splitted: List[NNumber] = []
        for number in numbers_notation_type_splitted:
            numbers_kansuji_kurai_splitted += self.split_number_by_kansuji_kurai(number)

        return numbers_kansuji_kurai_splitted
