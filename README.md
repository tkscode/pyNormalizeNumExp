[![PyPI version](https://badge.fury.io/py/pynormalizenumexp.svg)](https://badge.fury.io/py/pynormalizenumexp)
[![Python Versions](https://img.shields.io/pypi/pyversions/pynormalizenumexp.svg)](https://pypi.org/project/pynormalizenumexp/)
![pytest](https://github.com/tkscode/pyNormalizeNumExp/workflows/pytest/badge.svg)
[![codecov](https://codecov.io/gh/tkscode/pyNormalizeNumExp/branch/main/graph/badge.svg?token=3Z0YIZV5U1)](https://codecov.io/gh/tkscode/pyNormalizeNumExp)


# pyNormalizeNumexp

数量表現や時間表現の抽出・正規化を行う[NormalizeNumexp](https://www.cl.ecei.tohoku.ac.jp/Open_Resources-normalizeNumexp.html)のPython実装です。  
本家でもSWIGによるPythonバインディングが提供されていますが、NormalizeNumexp本体のインストールにトラブルに遭うことが多いため、全ての実装をPythonで移植しました。


## Prerequired

Python >=3.7, <=3.9


## Installation

```
pip install pynormalizenumexp
```


## Usage

```python
from pynormalizenumexp.normalize_numexp import NormalizeNumexp

normalizer = NormalizeNumexp("ja")

results = normalizer.normalize("魔女狩りは15世紀～18世紀にかけてみられ、全ヨーロッパで4万人が処刑された", as_dict=True)
for r in results:
	print(r)
# {'type': 'abstime', 'original_expr': '15世紀～18世紀', 'position_start': 5, 'position_end': 14, 'counter': 'none', 'value_lower_bound': {'year': 1401, 'month': inf, 'day': inf, 'hour': inf, 'minute': inf, 'second': inf}, 'value_upper_bound': {'year': 1800, 'month': -inf, 'day': -inf, 'hour': -inf, 'minute': -inf, 'second': -inf}, 'value_lower_bound_abs': None, 'value_upper_bound_abs': None, 'value_lower_bound_rel': None, 'value_upper_bound_rel': None, 'options': []}
# {'type': 'numerical', 'original_expr': '4万人', 'position_start': 29, 'position_end': 32, 'counter': '人', 'value_lower_bound': 40000, 'value_upper_bound': 40000, 'value_lower_bound_abs': None, 'value_upper_bound_abs': None, 'value_lower_bound_rel': None, 'value_upper_bound_rel': None, 'options': []}
```

+ `NormalizeNumexp`クラスの引数に言語識別子を指定します（例：日本語であれば`ja`）
	+ 本家では英語`en`や中国語`zh`にも対応していますが、本ライブラリでは日本語のみに対応しています（将来的には英語・中国語も入れる予定です）
+ `NormalizeNumexp`クラスの`normalize`関数に抽出・正規化対象のテキストを指定します
	+ `as_dict`引数に`True`を指定することで、返り値の数量・時間表現のオブジェクトが`dict`型になります
		+ 数量・時間表現のオブジェクトの属性については[`Expression`](./pynormalizenumexp/normalize_numexp.py#L19)クラスを参照してください
+ 返り値が`dict`型の場合のデータ構造は以下の通りです
	```python
	{
		"type": str, # 表現種別（numerical：数量、abstime：絶対時間、reltime：相対時間、duration：期間）
		"original_expr": str, # 数値・時間表現の文字列
		"position_start": int, # 抽出元テキストにおける開始位置
		"position_end": int, # 抽出元テキストにおける終了位置
		"counter": str, # 「人」や「匹」などの単位（typeがnumerical以外の場合は "none" になる）
		"value_lower_bound": None | int | float | Dict[str, int | float], # ※1
		"value_upper_bound": None | int | float | Dict[str, int | float], # ※1
		"value_lower_bound_abs": None | Dict[str, int | float], # ※2
		"value_upper_bound_abs": None | Dict[str, int | float], # ※2
		"value_lower_bound_rel": None | Dict[str, int | float], # ※3
		"value_upper_bound_rel": None | Dict[str, int | float], # ※3
		"options": List[str]
	}
	```
	+ ※1：数量・時間表現の下限値（lower）・上限値（upper）が入るが、`type`によって値の種類が変化する
		+ `numerical`の場合：`int`または`float`
			+ 例：`15.3ポイント`の場合は下限・上限ともに`15.3`
			+ 例：`1～2人`の場合は下限が`1`、上限が`2`
		+ `abstime`または`duration`の場合：`Dict[str, int | float]`
			+ 例：`2021年1月1日`の場合は下限・上限ともに`{"year": 2021, "month": 1, "day": 1}`となる（`hour`, `minute`, `second`は該当する情報がないので`inf`または`-inf`になる）
			+ 例：`3/3～3/5`の場合は下限が`{"month": 3, "day": 3}`、上限が`{"month": 3, "day": 5}`となる（`year`, `hour`, `minute`, `second`は該当する情報がないので`inf`または`-inf`になる）
			+ 例：`100年間`の場合は下限・上限ともに`{"year": 100}`となる（`month`, `day`, `hour`, `minute`, `second`は該当する情報がないので`inf`または`-inf`になる）
		+ `reltime`の場合：`None`
	+ ※2：`type`が`reltime`の場合に絶対時間表現の下限値（lower）・上限値（upper）が入る（その他の`type`の場合は`None`になる）
		+ 例：`昨年3月`の場合は下限・上限ともに`{"month": 3}`となる（`year`, `day`, `hour`, `minute`, `second`は該当する情報がないので`inf`または`-inf`になる）
	+ ※3：`type`が`reltime`の場合に相対時間表現の下限値（lower）・上限値（upper）が入る（その他の`type`の場合は`None`になる）
		+ 例：`昨年3月`の場合は下限・上限ともに`{"year": -1}`となる（`month`, `day`, `hour`, `minute`, `second`は該当する情報がないので`inf`または`-inf`になる）
		+ 例：`15年前`の場合下限・上限ともに`{"year": -15}`となる（`month`, `day`, `hour`, `minute`, `second`は該当する情報がないので`inf`または`-inf`になる）

## 免責事項

+ 本ライブラリの作成にあたり、単体テスト等で動作確認はしていますが、ケースによっては期待通りの振る舞いをしない可能性があります
+ 本ライブラリの利用により、万一、利用者に何らかの不都合や損害が発生したとしても、作者は何らの責任を負うものではありません


## Special thanks

+ [東北大学 乾・鈴木研究室](https://www.cl.ecei.tohoku.ac.jp/Open_Resources-normalizeNumexp.html)
+ [nullnull/normalizeNumexp](https://github.com/nullnull/normalizeNumexp)（本家実装）
+ [cotogoto/normalize-numexp](https://github.com/cotogoto/normalize-numexp)（Java移植版）
