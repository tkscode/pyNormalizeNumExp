import re
from typing import Dict, List, Optional, Tuple

from pynormalizenumexp.expression import NNumber
from pynormalizenumexp.expression.base import PLACE_HOLDER


class NormalizerUtility(object):
    def replace_numbers_in_text(self, text: str, numbers: List[NNumber]) -> str:
        """テキスト中の数値表現をPlaceholderに置換する.

        Parameters
        ----------
        text : str
            置換対象のテキスト
        numbers : List[NNumber]
            数値表現

        Returns
        -------
        str
            置換後のテキスト
        """
        # 数値表現の開始・終了位置をもとに置換するため、テキストをリスト（要素は各文字）にする
        new_text_list = list(text)
        for number in numbers:
            new_text_list[number.position_start:number.position_end] = \
                [PLACE_HOLDER] * (number.position_end - number.position_start)

        return "".join(new_text_list)

    def shorten_place_holder_in_text(self, text: str) -> str:
        """連続するPlaceholderを縮約する.

        Parameters
        ----------
        text : str
            縮約対象のテキスト

        Returns
        -------
        str
            縮約後のテキスト

        Notes
        -----
            「****年*月」 -> 「*年*月」のように数の部分を縮約する
        """
        return re.sub(f"[{PLACE_HOLDER}]{2,}", PLACE_HOLDER, text)

    def prefix_search(self, text: str, patterns: Dict[str, int]) -> int:
        """patternsの中から、テキストのprefixになっているものを探索する.

        Parameters
        ----------
        text : str
            探索対象のテキスト
        patterns : Dict[str, int]
            パターン情報（Key：パターン文字列、Value：パターンID）

        Returns
        -------
        int
            マッチしたパターンID

        Notes
        -----
            複数パターンがある場合はテキストのprefixが最長一致するものを採用する
        """
        shortened_text = self.shorten_place_holder_in_text(text)
        match_patterns = [(p_str, p_id) for p_str, p_id in patterns.items() if shortened_text.startswith(p_str)]

        fixed_pattern: Optional[Tuple[str, int]] = None
        for pattern in match_patterns:
            if fixed_pattern is not None and len(pattern[0]) > len(fixed_pattern[0]):
                fixed_pattern = pattern

        if fixed_pattern is not None:
            return fixed_pattern[1]

        return -1
