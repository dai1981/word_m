# /word 英単語辞書ページ生成キット（r- 担当）

このリポジトリは、**r で始まる英単語**の詳細ページを `word/word/{単語}.html` に量産するためのものです。
（s- を担当する別リポジトリと、ライブサイト上は同じ `/word/word/` を共有します。リポジトリは頭文字ごとに分かれています。）

## 使い方（Claude への指示）

スマホ・PCの Claude Code on the web で、こう言うだけです。

> **次の10単語**

このとき Claude が行うこと:

1. 既存の `data/*.json` と `word/word/*.html` を見て、**まだ作っていない r- の単語**を辞書順で10個決める
2. 新しいバッチを `data/r-batchN.json`（初回は `r-batch1.json`）として、下記スキーマで作成する
3. `python3 generate.py` を実行して `word/word/*.html` を生成する
4. 生成された HTML と追加した `data/*.json` を **main に直接コミット**する

> 補足: まだ1語も無い初回は「r で始まる最初の10語（rabbit, race, ...）」から始めてください。

## コミット方針（重要）

- **main ブランチに直接コミット**してください（新しいブランチ・PRは作らない）。
- 1バッチを1コミットにまとめる。メッセージ例: `Add r-batch2 (10 words: rain...reach)`

## 生成スクリプト

```bash
python3 generate.py
```

`data/` 内のすべての `*.json` を読み、`word/word/{単語}.html` を出力します（標準ライブラリのみ、依存なし）。

## データのスキーマ（1単語 = 1オブジェクト）

`s-` 側と同じスキーマです。各単語は次のキーを持ちます。

```json
{
  "english": "見出し語(小文字, rで始まる)",
  "pron": "発音記号(IPA, スラッシュ無し)",
  "kana": "カナ発音",
  "hinshi": "品詞表示 (例: 動詞 / 名詞)",
  "ld_pos": "JSON-LD用の品詞",
  "ld_etym": "JSON-LD用の語源(短く)",
  "ld_level": "英検レベル (例: 4級)",
  "badges": ["対象(例:小学生〜)", "英検X級", "CEFR Xx", "特徴"],
  "meaning_main": "主な意味をスラッシュ区切り",
  "description": "meta description (70字程度)",
  "keywords": ["xxx 意味", "xxx 使い方", "..."],
  "meanings": [{ "hinshi": "【品詞】意味", "note": "例や補足" }],
  "usages":   [{ "title": "① 見出し", "desc": "説明", "example_en": "英語例文", "example_ja": "和訳" }],
  "warn":     ["よくある間違い・注意点"],
  "etym_note": "語源の解説文",
  "etym_chain": [{ "node": "語形", "sub": "意味", "era": "時代" }],
  "phrases":  [{ "en": "フレーズ", "ja": "意味" }],
  "related":  [{ "en": "関連語", "ja": "意味" }],
  "faq":      [{ "q": "質問", "a": "回答" }],
  "quiz":     [{ "q": "問題文", "A": "選択肢A", "B": "選択肢B", "C": "選択肢C", "D": "選択肢D", "correct": "B" }]
}
```

### 推奨の分量
meanings 3〜5 / usages 2〜3 / phrases 6〜8 / related 3〜4 / faq 2〜3 / quiz 2 / etym_chain 2〜3段（最後が現代英語）。

### 出力先・固定値
- 出力: `word/word/{english}.html`（実サイトの `/word/word/` に対応）
- canonical: `/word/word/{english}.html`
- GA4: `G-MKNGEYPKNJ`、AdSense: `ca-pub-3234684892462480`、JSON-LD set URL: `https://eigo-duke.com/word/word.html`

## 注意
- 扱う単語は **r- のみ**。s- など他の頭文字は作らないこと（s- は別リポジトリの担当）。
- デプロイは「アップロードのみ（削除なし）」なので、同じ `/word/word/` にある s- のページを消しません。
- `data/*.json` は追記式。過去バッチは消さないこと。
- 内容は学習者向けの正確さを優先。名詞なら可算名詞か不可算名詞か表示
