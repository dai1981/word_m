# eigo-duke コンテンツ生成キット（3系統）

このリポジトリは、次の **3系統** のページを量産します。どれも `python3` の生成スクリプトで
JSON → HTML を作り、GitHub Actions からロリポップへFTPアップロードします。

| 系統 | データ | 生成スクリプト | 出力先 / 実サイト |
|------|--------|----------------|-------------------|
| ① 英単語（r-） | `data/*.json` | `generate.py` | `word/word/{単語}.html` → `/word/word/` |
| ② 古文単語 | `koten_data/*.json` | `generate_koten.py` | `exam/koten/{id}.html` → `/exam/koten/` |
| ③ 漢文用語 | `kanbun_data/*.json` | `generate_kanbun.py` | `exam/kanbun/{id}.html` → `/exam/kanbun/` |

「**次の10単語**」「**次の20**」と言われたら、直近で作業している系統のバッチを1つ作ります。
系統を切り替えたいときはユーザーが明示します（例:「次は古文にしよう」「次は漢文にしよう」）。
デプロイはそれぞれ独立（`.ftp-deploy-koten.json` / `.ftp-deploy-kanbun.json` の別 state、
`/exam/koten/`・`/exam/kanbun/` へアップロードのみ）で、互いに触りません。

---

# ① /word 英単語辞書ページ生成キット（r- 担当）

このパートは、**r で始まる英単語**の詳細ページを `word/word/{単語}.html` に量産します。
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
- canonical: `https://www.eigo-duke.com/word/word/{english}.html`
- GA4: `G-MKNGEYPKNJ`、AdSense: `ca-pub-3234684892462480`、JSON-LD set URL: `https://www.eigo-duke.com/word/word.html`

## 注意
- 扱う単語は **r- のみ**。s- など他の頭文字は作らないこと（s- は別リポジトリの担当）。
- デプロイは「アップロードのみ（削除なし）」なので、同じ `/word/word/` にある 他 のページを消しません。
- `data/*.json` は追記式。過去バッチは消さないこと。
- 内容は学習者向けの正確さを優先。名詞なら可算名詞か不可算名詞か表示

---

# ② 古文単語辞典 生成キット（大学受験向け）

**古文・古典の重要単語**の詳細ページを `exam/koten/{id}.html` に量産し、
既存のハブページ `/exam/kotenindex` からリンクさせます。対象読者は **大学受験生**。
「分かりやすい・覚えやすい・情報量が多い・SEO/AIに強い」ページを目指します。

## 使い方（Claude への指示）

> **次の10単語**

このとき Claude が行うこと:

1. 既存の `koten_data/*.json` を見て、**まだ作っていない古文重要語**を10個決める
   （入試頻出度の高い語＝「最重要」から優先。五十音順で網羅していくとよい）
2. 新しいバッチを `koten_data/koten-batchN.json`（初回は `koten-batch1.json`）として下記スキーマで作成
3. `python3 generate_koten.py` を実行して `exam/koten/*.html` を生成
4. 生成された HTML と追加した JSON をコミット
5. `exam/koten/_links_snippet.html`（自動生成されるリンク集）を確認し、
   **既存 `kotenindex` へ貼るリンク**をユーザーに知らせる（ハブ本体は自動で書き換えない）

## データのスキーマ（1語 = 1オブジェクト）

```json
{
  "id": "aware",                       // 半角英数のファイル名/URL（例: exam/koten/aware.html）
  "midashi": "あはれ",                  // 見出し語（歴史的仮名遣い）
  "gendai_kana": "あわれ",              // 現代仮名遣い
  "yomi": "アワレ",                     // 読み（カナ）
  "hinshi": "名詞／形容動詞ナリ活用",     // 品詞（活用の種類まで）
  "level": "最重要",                    // 入試頻出度: 最重要 / 重要 / 標準 / 発展
  "tags": ["感情語","頻出","源氏物語"],  // バッジ（ジャンル・出典など）
  "core": "しみじみとした深い感動・情趣", // 一言コア（見出しカードに大きく表示）
  "description": "meta description (70〜120字)",
  "keywords": ["あはれ 意味","あはれ 古文","あはれ をかし 違い"],
  "meanings":  [{ "gendai": "現代語訳", "note": "使い分け・補足" }],
  "examples":  [{ "honbun": "古文の本文", "shutten": "出典（作品名）", "yaku": "現代語訳" }],
  "point":     "識別・注意点（助動詞なら接続・意味の見分け、紛らわしい語との違い）",
  "goro":      "覚え方・ゴロ（暗記のコツ）",
  "gogen":     "語源・成り立ち",
  "kanren":    [{ "go": "をかし", "imi": "対義/関連の意味", "id": "okashi(任意:あればリンク化)" }],
  "faq":       [{ "q": "質問", "a": "回答" }],
  "quiz":      [{ "q": "問題文", "A": "..", "B": "..", "C": "..", "D": "..", "correct": "B" }]
}
```

### 推奨の分量
meanings 2〜5 / examples 1〜3（**必ず出典付き**。源氏物語・枕草子・徒然草・伊勢物語・古今集など）/
kanren 2〜4 / faq 2〜3 / quiz 2。`point` と `goro` は受験生に刺さる要なので特に丁寧に。

### 出力先・固定値
- 出力: `exam/koten/{id}.html`（実サイトの `/exam/koten/` に対応）
- canonical: `https://www.eigo-duke.com/exam/koten/{id}.html`
- ハブ: `/exam/kotenindex.html`（**既存。生成・上書きしない**。各ページからリンク＋検索窓で連携）
- GA4: `G-MKNGEYPKNJ`、AdSense: `ca-pub-3234684892462480`、JSON-LD set URL: `https://www.eigo-duke.com/exam/kotenindex`
- ページ用資産: `exam/koten/koten.css`・`exam/koten/koten.js`・`exam/koten/koten-search.js`（手動管理の静的ファイル）
- 検索: `generate_koten.py` が `exam/koten/koten-index.json` を自動生成。各ページ上部と
  `kotenindex.html` に `<div id="koten-search"></div>`＋`koten-search.js` を置けば全語検索が可能
  （見出し・現代仮名遣い・読み・意味で部分一致 → `/exam/koten/{id}.html` へ遷移）

## 注意
- `id` は半角英数で一意に（重複禁止。ローマ字読みが基本、衝突時は語義で区別）。
- `koten_data/*.json` は追記式。過去バッチは消さないこと。
- **出典は正確に**。本文・現代語訳・作品名の取り違えに注意（公開前に目視確認）。
- ハブ `kotenindex` は既存を尊重し、リンク追加は `_links_snippet.html` を貼る運用。
- デプロイは `/exam/koten/` へアップロードのみ（別 state ファイル `.ftp-deploy-koten.json`）。
  `/exam/kotenindex` や他の `/exam` 配下は触らない。

---

# ③ 漢文用語辞典 生成キット（大学受験向け）

**漢文の重要用語**（句法・再読文字・助字・重要語・故事成語 など）の詳細ページを
`exam/kanbun/{id}.html` に量産し、ハブページ `/exam/kanbunindex` からリンクさせます。
対象読者は **大学受験生**。②古文と完全並列で、同じ「分かりやすい・覚えやすい・
情報量が多い・SEO/AIに強い」ページを目指します。

## 使い方（Claude への指示）

> **次の20**

このとき Claude が行うこと:

1. 既存の `kanbun_data/*.json` を見て、**まだ作っていない漢文重要用語**を20個決める
2. 新しいバッチを `kanbun_data/kanbun-batchN.json` として下記スキーマで作成
3. `python3 generate_kanbun.py` を実行して `exam/kanbun/*.html` を生成
4. 生成された HTML と追加した JSON をコミット
5. `exam/kanbun/_links_snippet.html`（自動生成）を確認し、既存 `kanbunindex` へ貼るリンクを知らせる

### 1バッチの配分（バランス型）
句法・再読文字を軸に、助字・重要語（多義/特殊訓）・故事成語をまぜて20項目。
目安: 句法7／再読文字4／助字3／重要語3／故事成語3（ジャンルは `bunrui` と `tags` で分類）。
再読文字は9字（未・将・且・当・応・宜・須・猶・盍）を最優先で網羅。

## データのスキーマ（1項目 = 1オブジェクト・②古文ベース＋漢文用に拡張）

```json
{
  "id": "shieki",                       // 半角英数のファイル名/URL（例: exam/kanbun/shieki.html）
  "midashi": "使・令（使役）",             // 見出し（句形／漢字／故事成語）
  "yomi": "しム／〜をして…しむ",           // 読み方（訓読）
  "kana": "シエキ",                      // 検索用カナ（gendai_kana相当）
  "bunrui": "句法",                      // 分類: 句法/再読文字/助字/重要語/故事成語/文学史
  "level": "最重要",                     // 入試頻出度: 最重要 / 重要 / 標準 / 発展
  "tags": ["使役","句形","頻出"],
  "core": "AをしてB(せ)しむ＝AにBさせる",   // 一言コア
  "description": "meta description (70〜120字)",
  "keywords": ["使役 漢文","使 しむ 意味"],
  "meanings": [{ "gendai": "現代語訳・用法", "note": "補足" }],
  "examples": [{                         // ★白文→書き下し→訳→出典 の3段（漢文の要）
      "hakubun": "天帝使我長百獣",         // 白文（原文・返り点なし）
      "kakikudashi": "天帝我をして百獣に長たら使む", // 書き下し文（訓読）
      "yaku": "天の神は、私を百獣の王とさせた。",
      "shutten": "戦国策"                 // 出典（確かなもの。不確かなら「例文」）
  }],
  "kunten": "返り点・送り仮名・読む順序のポイント（訓読）", // ★漢文用の新フィールド
  "point": "識別・注意点（句形の見分け、置き字か読むか、再読の読み方）",
  "goro": "覚え方・ゴロ",
  "gogen": "由来・成り立ち（故事成語は元の故事／漢字の成り立ち）",
  "kanren": [{ "go": "見・被（受身）", "imi": "AがBされる", "id": "ukemi(任意:あればリンク化)" }],
  "faq": [{ "q": "質問", "a": "回答" }],
  "quiz": [{ "q": "問題文", "A": "..","B": "..","C": "..","D": "..","correct": "A" }]
}
```

### 推奨の分量
meanings 1〜4 / examples 1〜2（**白文・書き下し・訳・出典をそろえる**。史記・戦国策・論語・孟子・
韓非子・荀子・漢書 など。出典が不確かなら `shutten:"例文"`）/ kanren 2〜4 / faq 1〜3 / quiz 1〜2。
`point`・`kunten`・`goro` は受験生に刺さる要なので特に丁寧に。

### 出力先・固定値
- 出力: `exam/kanbun/{id}.html`（実サイトの `/exam/kanbun/` に対応）
- canonical: `https://www.eigo-duke.com/exam/kanbun/{id}.html`
- ハブ: `/exam/kanbunindex.html`（**生成・上書きしない**。各ページからリンク＋検索窓で連携）
- GA4: `G-MKNGEYPKNJ`、AdSense: `ca-pub-3234684892462480`
- ページ用資産: `exam/kanbun/kanbun.css`・`exam/kanbun/kanbun.js`・`exam/kanbun/kanbun-search.js`（手動管理）
- 検索: `generate_kanbun.py` が `exam/kanbun/kanbun-index.json` を自動生成。各ページ上部と
  `kanbunindex.html` に `<div id="kanbun-search"></div>`＋`kanbun-search.js` を置けば全語検索が可能。

## 注意
- `id` は半角英数で一意に（重複禁止。ローマ字読み・語義が基本、衝突時は区別）。
- `kanbun_data/*.json` は追記式。過去バッチは消さないこと。
- **出典・白文・書き下しは正確に**。返り点/送り仮名・作品名の取り違えに注意（公開前に目視確認）。
- 白文・書き下しにローマ字を混入しない（説明中の A/B などの記号は可）。
- ハブ `kanbunindex` は既存を尊重し、リンク追加は `_links_snippet.html` を貼る運用。
- デプロイは `/exam/kanbun/` へアップロードのみ（別 state ファイル `.ftp-deploy-kanbun.json`、
  ワークフロー `.github/workflows/deploy-kanbun.yml`）。`/exam/kanbunindex` や他の `/exam` 配下は触らない。
