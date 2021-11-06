"""TypedDictを使った独自の型定義モジュール."""
from typing import List

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


# 漢数字辞書
ChineseCharacterDict = TypedDict("ChineseCharacterDict", {
    "character": str,
    "value": int,
    "notation_type": str
})

# 時間系以外の表現パターン辞書
CounterDict = TypedDict("CounterDict", {
    "pattern": str,
    "counter": str,
    "SI_prefix": int,
    "optional_power_of_ten": int,
    "ordinary": bool,
    "option": str
})

# 絶対時間の表現パターン辞書
LimitedAbstimeExpressionDict = TypedDict("LimitedAbstimeExpressionDict", {
    "pattern": str,
    "corresponding_time_position": List[str],
    "process_type": List[str],
    "ordinary": bool,
    "option": str
})

# 各種表現のprefix/suffixパターン辞書
NumberModifierDict = TypedDict("NumberModifierDict", {
    "pattern": str,
    "process_type": str
})
