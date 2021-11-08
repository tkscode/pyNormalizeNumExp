"""TypedDictを使った独自の型定義モジュール."""
from typing import Dict, List, Optional, Union

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
NumericalPatternDict = TypedDict("NumericalPatternDict", {
    "pattern": str,
    "counter": str,
    "SI_prefix": int,
    "optional_power_of_ten": int,
    "ordinary": bool,
    "option": str
})

# 絶対時間の表現パターン辞書
AbstimePatternDict = TypedDict("AbstimePatternDict", {
    "pattern": str,
    "corresponding_time_position": List[str],
    "process_type": List[str],
    "ordinary": bool,
    "option": str
})

# 相対時間の表現パターン辞書
ReltimePatternDict = TypedDict("ReltimePatternDict", {
    "pattern": str,
    "corresponding_time_position": List[str],
    "process_type": List[str],
    "ordinary": bool,
    "option": str
})

# 期間の表現パターン辞書
DurationPatternDict = TypedDict("DurationPatternDict", {
    "pattern": str,
    "corresponding_time_position": List[str],
    "process_type": List[str],
    "ordinary": bool,
    "option": str
})

# 除外表現パターン辞書
InappropriateStringDict = TypedDict("InappropriateStringDict", {
    "str": str
})

# 各種表現のprefix/suffixパターン辞書
NumberModifierDict = TypedDict("NumberModifierDict", {
    "pattern": str,
    "process_type": str
})

# 返却用の表現辞書
ReturnExpressionDict = TypedDict("ReturnExpressionDict", {
    "type": str,
    "original_expr": str,
    "position_start": int,
    "position_end": int,
    "counter": str,
    "value_lower_bound": Union[int, float, Dict[str, Union[int, float]]],
    "value_upper_bound": Union[int, float, Dict[str, Union[int, float]]],
    "value_lower_bound_abs": Optional[Dict[str, Union[int, float]]],
    "value_upper_bound_abs": Optional[Dict[str, Union[int, float]]],
    "value_lower_bound_rel": Optional[Dict[str, Union[int, float]]],
    "value_upper_bound_rel": Optional[Dict[str, Union[int, float]]]
})
