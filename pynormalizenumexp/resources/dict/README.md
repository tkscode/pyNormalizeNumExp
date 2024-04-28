# 数値表現パターン辞書

## カスタム辞書の作り方

カスタム辞書はJSON形式で以下のフォーマットにする必要があります。
```json
[
  {
    "expr_type": "number:limited",
    "value": {
      "pattern": "ファイル",
      "counter": "ファイル",
      "SI_prefix": 0,
      "optional_power_of_ten": 0,
      "ordinary": false,
      "option": ""
    }
  },
  ...
]
```
**絶対時間や期間などの数値表現タイプ（`expr_type`）ごとに`value`の構造は変化するため、構造は以下に示す元の辞書を参考にしてください。**  
なお、パターン文字列中の`ǂ`は任意の数字を表します。

### 時間系以外

+ `number:limited`：「円」や「ページ」など時間系以外の数値表現（[元の辞書ファイル](./ja/num_counter.json)）
+ `number:counter`：「時速」や「東経」などの時間系以外の接頭辞表現（[元の辞書ファイル](./ja/num_prefix_counter.json)）
+ `number:prefix_modifier`：「約」や「およそ」などの抽象的な時間系以外の接頭辞表現（[元の辞書ファイル](./ja/num_prefix.json)）
+ `number:suffix_modifier`：「以内」や「以上」などの抽象的な時間系以外の接尾辞表現（[元の辞書ファイル](./ja/num_suffix.json)）

### 絶対時間

+ `abstime:limited`：年月日などの絶対時間表現（[元の辞書ファイル](./ja/abstime_expression.json)）
+ `abstime:counter`：「令和」などの接頭辞表現（[元の辞書ファイル](./ja/abstime_prefix_counter.json)）
+ `abstime:prefix_modifier`：「およそ」などの抽象的な時間の接頭辞表現（[元の辞書ファイル](./ja/abstime_prefix.json)）
+ `abstime:suffix_modifier`：「上旬」や「下旬」などの抽象的な時間の接尾辞表現（[元の辞書ファイル](./ja/abstime_suffix.json)）

### 相対時間

+ `reltime:limited`：「年前」などの相対時間表現（[元の辞書ファイル](./ja/reltime_expression.json)）
+ `reltime:counter`：「去年」や「来年」などの接頭辞表現（[元の辞書ファイル](./ja/reltime_prefix_counter.json)）
+ `reltime:prefix_modifier`：「およそ」などの抽象的な時間の接頭辞表現（[元の辞書ファイル](./ja/reltime_prefix.json)）
+ `reltime:suffix_modifier`：「中頃」などの抽象的な時間の接尾辞表現（[元の辞書ファイル](./ja/reltime_suffix.json)）

### 期間

+ `duration:limited`：「年間」などの期間表現（[元の辞書ファイル](./ja/duration_expression.json)）
+ `duration:counter`：接頭辞表現（[元の辞書ファイル](./ja/duration_prefix_counter.json)）
	+ 元の辞書では定義なし
+ `duration:prefix_modifier`：「およそ」などの抽象的な期間の接頭辞表現（[元の辞書ファイル](./ja/duration_prefix.json)）
+ `duration:suffix_modifier`：「毎」や「台」などの抽象的な期間の接尾辞表現（[元の辞書ファイル](./ja/duration_suffix.json)）

### 不適切な数値表現

+ `inappropriate_string`：「九州」や「三振」など数値表現として抽出しない文字列（[元の辞書ファイル](./ja/inappropriate_strings.json)）
