"""正規化・補正処理における共通処理を定義モジュール."""
import re
from typing import Dict, List, Optional, Tuple

from pynormalizenumexp.expression.base import INF, PLACE_HOLDER, NNumber, NTime


class NormalizerUtility(object):
    """正規化・補正処理における共通処理のクラス."""

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
        return re.sub(f"[{PLACE_HOLDER}]{{2,}}", PLACE_HOLDER, text, flags=re.DOTALL)

    def search_pattern(self, text: str, patterns: Dict[str, int], search_type: str) -> int:
        """patternsの中から、テキストのprefix/suffixになっているものを探索する.

        Parameters
        ----------
        text : str
            探索対象のテキスト
        patterns : Dict[str, int]
            パターン情報（Key：パターン文字列、Value：パターンID）
        search_type : str
            先頭から見るprefixか末尾から見るsuffixか

        Returns
        -------
        int
            マッチしたパターンID

        Notes
        -----
            複数パターンがある場合はテキストのprefix/suffixが最長一致するものを採用する
        """
        shortened_text = self.shorten_place_holder_in_text(text)
        if search_type == "prefix":
            match_patterns = [(p_str, p_id) for p_str, p_id in patterns.items() if shortened_text.startswith(p_str)]
        elif search_type == "suffix":
            match_patterns = [(p_str, p_id) for p_str, p_id in patterns.items() if shortened_text.endswith(p_str)]
        else:
            raise ValueError(f'Invalid search_type: "{search_type}"')

        fixed_pattern: Optional[Tuple[str, int]] = None
        for pattern in match_patterns:
            if fixed_pattern is None or len(pattern[0]) > len(fixed_pattern[0]):
                fixed_pattern = pattern

        if fixed_pattern is not None:
            return fixed_pattern[1]

        return -1

    def search_prefix_number_modifier(self, text: str, expr_position_start: int, patterns: Dict[str, int]) -> int:
        """数値表現の前に来る修飾表現を検索する.

        Parameters
        ----------
        text : str
            検索対象のテキスト
        expr_position_start : int
            数値表現の開始位置
        patterns : Dict[str, int]
            修飾表現パターン

        Returns
        -------
        int
            マッチした修飾表現パターンのID

        Notes
        -----
            数値表現の直前から探していくので、search_patternにはsuffixを指定している
        """
        before_text = text[:expr_position_start]

        # 「コンビニで$100を払った」の場合、「100」が数値表現になるので「コンビニで$」を末尾から見ていく
        # -> 「$」が修飾表現に該当する
        return self.search_pattern(before_text, patterns, "suffix")

    def search_suffix_number_modifier(self, text: str, expr_position_end: int, patterns: Dict[str, int]) -> int:
        """数値表現の後に来る修飾表現を検索する.

        Parameters
        ----------
        text : str
            検索対象のテキスト
        expr_position_end : int
            数値表現の終了位置
        patterns : Dict[str, int]
            修飾表現パターン

        Returns
        -------
        int
            マッチした修飾表現パターンのID

        Notes
        -----
            数値表現の直後から探していくので、search_patternにはprefixを指定している
        """
        after_text = text[expr_position_end:]

        return self.search_pattern(after_text, patterns, "prefix")

    def is_finite(self, value: float) -> bool:
        """与えられた数値が正負の無限大でないかどうかを判定する.

        Parameters
        ----------
        value : float
            判定対象の数値

        Returns
        -------
        bool
            判定結果（True：正負の無限大でない、False：正負の無限大である）
        """
        return value != INF and value != -INF

    def is_null_time(self, time: NTime) -> bool:
        """与えられた時間オブジェクトがNullかどうかを判定する.

        Parameters
        ----------
        time : NTime
            判定対象の時間オブジェクト

        Returns
        -------
        bool
            判定結果（True：Nullである、False：Nullでない）

        Notes
        -----
            Nullの場合はNTimeのすべての属性がINFまたは-INFになっている
        """
        return time == NTime(INF) or time == NTime(-INF)

    def identify_time_detail(self, time: NTime) -> str:
        """与えられた時間オブジェクトがどの単位のものかを判定する.

        Parameters
        ----------
        time : NTime
            判定対象の時間オブジェクト

        Returns
        -------
        str
            単位を表す文字列

        Notes
        -----
            s: 秒、mn: 分、h: 時、d: 日、m: 月、 y: 年
        """
        if self.is_finite(time.second):
            return "s"
        elif self.is_finite(time.minute):
            return "mn"
        elif self.is_finite(time.hour):
            return "h"
        elif self.is_finite(time.day):
            return "d"
        elif self.is_finite(time.month):
            return "m"
        elif self.is_finite(time.year):
            return "y"
        else:
            return ""
