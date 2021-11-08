"""文字列に関する共通処理モジュール."""
import re
from typing import Dict, Optional

from pynormalizenumexp.expression.base import NotationType

from .dict_loader import DictLoader


class DigitUtility(object):
    """文字列処理用クラス."""

    def __init__(self, dict_loader: DictLoader) -> None:
        """コンストラクタ.

        Parameters
        ----------
        dict_loader : DictLoader
            辞書ファイルのローダー
        """
        self.dict_loader = dict_loader

        self.str_to_notation_type: Dict[str, NotationType] = {}
        self.kansuji_09_to_value: Dict[str, int] = {}
        self.kansuji_kurai_to_power_val: Dict[str, int] = {}

    def init_kansuji(self) -> None:
        """漢数字に関する初期化処理."""
        chinese_characters = self.dict_loader.load_chinese_character_dict("chinese_character.json")
        for c_char in chinese_characters:
            if c_char.notation_type == "09":
                notation_type = NotationType.KANSUJI_09

                self.kansuji_09_to_value[c_char.character] = c_char.value
            elif c_char.notation_type == "sen":
                notation_type = NotationType.KANSUJI_KURAI_SEN

                self.kansuji_kurai_to_power_val[c_char.character] = c_char.value
            elif c_char.notation_type == "man":
                notation_type = NotationType.KANSUJI_KURAI_MAN

                self.kansuji_kurai_to_power_val[c_char.character] = c_char.value
            else:
                notation_type = NotationType.NOT_NUMBER

            self.str_to_notation_type[c_char.character] = notation_type

        self.kansuji_kurai_to_power_val["　"] = 0

    def is_hankakusuji(self, chars: Optional[str]) -> bool:
        """与えられた文字列が半角数字かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：半角数字、False：半角数字でない
        """
        if chars is None:
            return False

        if re.match(r"[0-9]+", chars):
            return True

        return False

    def is_zenkakusuji(self, chars: Optional[str]) -> bool:
        """与えられた文字列が全角数字かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：全角数字、False：全角数字でない
        """
        if chars is None:
            return False

        if re.match(r"[０-９]+", chars):
            return True

        return False

    def is_arabic(self, chars: Optional[str]) -> bool:
        """与えられた文字列がアラビア数字かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：アラビア数字、False：アラビア数字でない
        """
        return self.is_hankakusuji(chars) or self.is_zenkakusuji(chars)

    def is_notation_type(self, chars: Optional[str], notation_type: NotationType) -> bool:
        """与えられた文字列が指定された数字種かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列
        notation_type : NotationType
            指定された数字種

        Returns
        -------
        bool
            True：指定された数字種、False：指定された数字種でない
        """
        if chars is None or chars not in self.str_to_notation_type:
            return False

        return self.str_to_notation_type[chars] == notation_type

    def is_kansuji09(self, chars: Optional[str]) -> bool:
        """与えられた文字列が一の位の数字かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：一の位の数字、False：一の位の数字でない
        """
        return self.is_notation_type(chars, NotationType.KANSUJI_09)

    def is_kansuji_kurai_sen(self, chars: Optional[str]) -> bool:
        """与えられた文字列が十の位から千の位までの数字かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：十～千の位までの数字、False：十～千の位までの数字でない
        """
        return self.is_notation_type(chars, NotationType.KANSUJI_KURAI_SEN)

    def is_kansuji_kurai_man(self, chars: Optional[str]) -> bool:
        """与えられた文字列が万の位以上の数字かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：万の位以上の数字、False：万の位以上の数字でない
        """
        return self.is_notation_type(chars, NotationType.KANSUJI_KURAI_MAN)

    def is_kansuji_kurai(self, chars: Optional[str]) -> bool:
        """与えられた文字列が十の位以上かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：十の位以上の数字、False：十の位以上の数字でない
        """
        return self.is_kansuji_kurai_sen(chars) or self.is_kansuji_kurai_man(chars)

    def is_kansuji(self, chars: Optional[str]) -> bool:
        """与えられた文字列が漢数字かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：漢数字である、False：漢数字でない
        """
        return self.is_kansuji09(chars) or self.is_kansuji_kurai(chars)

    def is_number(self, chars: Optional[str]) -> bool:
        """与えられた文字列が数字かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：数字である、False：数字でない
        """
        return self.is_hankakusuji(chars) or self.is_zenkakusuji(chars) or self.is_kansuji(chars)

    def is_comma(self, chars: Optional[str]) -> bool:
        """与えられた文字列がコンマかどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：コンマである、False：コンマでない
        """
        return chars == "," or chars == "、" or chars == "，"

    def is_decimal_point(self, chars: Optional[str]) -> bool:
        """与えられた文字列が小数点かどうか判定する.

        Parameters
        ----------
        chars : Optional[str]
            判定対象の文字列

        Returns
        -------
        bool
            True：小数点である、False：小数点でない
        """
        return chars == "." or chars == "・" or chars == "．"

    def is_range_expression(self, chars: str) -> bool:
        """与えられた文字列が範囲を表す表現かどうか判定する.

        Parameters
        ----------
        chars : str
            判定対象の文字列

        Returns
        -------
        bool
            True：範囲表現である、False：範囲表現でない
        """
        return chars == "~" or chars == "〜" or chars == "～" or chars == "-" or chars == "−" or chars == "ー" \
            or chars == "―" or chars == "から"

    def kansuji_kurai2power_value(self, chars: Optional[str]) -> int:
        """漢数字を数値に変換する.

        Parameters
        ----------
        chars : Optional[str]
            変換対象の文字列

        Returns
        -------
        int
            変換した数値
        """
        if chars != "　" and (chars not in self.kansuji_kurai_to_power_val or not self.is_kansuji_kurai(chars)):
            raise ValueError(f'"{chars}" is not kansuji_kurai')

        return self.kansuji_kurai_to_power_val[chars]

    def chars2notation_type(self, chars: Optional[str]) -> NotationType:
        """与えられた文字列がどの数字種か調べる（数字種省略版）.

        Parameters
        ----------
        chars : Optional[str]
            調査対象の文字列

        Returns
        -------
        int
            数字種（Enumの変数）
        """
        if self.is_hankakusuji(chars):
            return NotationType.HANKAKU
        elif self.is_zenkakusuji(chars):
            return NotationType.ZENKAKU
        elif self.is_kansuji(chars):
            return NotationType.KANSUJI
        else:
            return NotationType.NOT_NUMBER

    def chars2full_notation_type(self, chars: Optional[str]) -> NotationType:
        """与えられた文字列がどの数字種か調べる（全数字種版）.

        Parameters
        ----------
        chars : Optional[str]
            調査対象の文字列

        Returns
        -------
        int
            数字種（Enumの変数）
        """
        if self.is_hankakusuji(chars):
            return NotationType.HANKAKU
        elif self.is_zenkakusuji(chars):
            return NotationType.ZENKAKU
        elif self.is_kansuji09(chars):
            return NotationType.KANSUJI_09
        elif self.is_kansuji_kurai_sen(chars):
            return NotationType.KANSUJI_KURAI_SEN
        elif self.is_kansuji_kurai_man(chars):
            return NotationType.KANSUJI_KURAI_MAN
        else:
            return NotationType.NOT_NUMBER
