#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
漢文・漢文用語集ジェネレータ（古文系 generate_koten.py と並列・独立）

  kanbun_data/*.json  ->  exam/kanbun/{id}.html
  併せて次も出力:
    exam/kanbun/kanbun-index.json   … 検索用インデックス（kanbun-search.js が読む）
    exam/kanbun/_links_snippet.html … 既存/新設 kanbunindex へ貼るリンク集

- ハブページ /exam/kanbunindex.html は生成・上書きしない（リンクはスニペット運用）。
- 各ページはハブへ相互リンク＋検索窓を設置。
- 依存なし（標準ライブラリのみ）。

古文スキーマとの主な違い:
  * hinshi → bunrui（句法/再読文字/助字/重要語/故事成語/文学史 など）
  * gendai_kana → kana（検索用カナ）
  * examples: {hakubun(白文), kakikudashi(書き下し文), yaku(現代語訳), shutten(出典)}
  * kunten（訓読のポイント：返り点・送り仮名・読む順序）を新設
"""
import json, html, os, glob

OUT = "exam/kanbun"
SITE = "https://www.eigo-duke.com"
INDEX_PATH = "/exam/kanbunindex.html"     # ハブ（相対リンク用）
INDEX_URL = SITE + INDEX_PATH             # JSON-LD 用の絶対URL
SET_NAME = "漢文用語辞典"
GA = "G-MKNGEYPKNJ"
ADSENSE = "ca-pub-3234684892462480"

LEVEL_CLASS = {"最重要": "max", "重要": "high", "標準": "std", "発展": "adv"}


def e(s):  return html.escape(str(s if s is not None else ""), quote=False)
def ea(s): return html.escape(str(s if s is not None else ""), quote=True)


def build(d):
    mid   = e(d["midashi"])
    wid   = d["id"]
    desc  = e(d.get("description") or d.get("core", ""))
    kw    = ea("，".join(d.get("keywords", [])))
    lvl   = d.get("level", "")
    lvlc  = LEVEL_CLASS.get(lvl, "std")
    bunrui = d.get("bunrui", d.get("hinshi", ""))
    path  = "/exam/kanbun/%s.html" % wid
    canon = SITE + path

    # --- JSON-LD: DefinedTerm ---
    ld_term = {
        "@context": "https://schema.org", "@type": "DefinedTerm",
        "name": d["midashi"],
        "description": d.get("description") or d.get("core", ""),
        "inDefinedTermSet": {"@type": "DefinedTermSet", "name": SET_NAME, "url": INDEX_URL},
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "分類", "value": bunrui},
            {"@type": "PropertyValue", "name": "読み", "value": d.get("yomi", "")},
            {"@type": "PropertyValue", "name": "入試頻出度", "value": lvl},
            {"@type": "PropertyValue", "name": "語源", "value": d.get("gogen", "")},
        ],
    }
    # --- JSON-LD: BreadcrumbList ---
    ld_bc = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "漢文用語索引", "item": INDEX_URL},
            {"@type": "ListItem", "position": 2, "name": d["midashi"], "item": canon},
        ],
    }
    # --- JSON-LD: FAQPage ---
    faq = d.get("faq", [])
    ld_faq = None
    if faq:
        ld_faq = {"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": f["q"],
                                  "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faq]}

    tags = "\n      ".join('<span class="k-tag">%s</span>' % e(t) for t in d.get("tags", []))

    meanings = "\n".join(
        ('      <li>\n        <span class="k-mnum">%d</span>\n'
         '        <div class="k-mbody">\n'
         '          <span class="k-gendai">%s</span>\n'
         '          <span class="k-note">%s</span>\n'
         '        </div>\n      </li>') % (i + 1, e(m.get("gendai", "")), e(m.get("note", "")))
        for i, m in enumerate(d.get("meanings", [])))

    examples = ""
    if d.get("examples"):
        blocks = []
        for x in d["examples"]:
            rows = []
            if x.get("hakubun"):
                rows.append('      <div class="k-hakubun"><span class="k-ex-label k-lbl-haku">白文</span>%s</div>'
                            % e(x["hakubun"]))
            if x.get("kakikudashi"):
                rows.append('      <blockquote class="k-kakikudashi"><span class="k-ex-label k-lbl-kaki">書き下し</span>%s</blockquote>'
                            % e(x["kakikudashi"]))
            if x.get("yaku"):
                rows.append('      <p class="k-yaku"><span class="k-yaku-label">訳</span>%s</p>' % e(x["yaku"]))
            if x.get("shutten"):
                rows.append('      <figcaption class="k-shutten">──『%s』</figcaption>' % e(x["shutten"]))
            blocks.append('    <figure class="k-ex">\n%s\n    </figure>' % "\n".join(rows))
        examples = ('  <section class="k-card">\n    <h2 class="k-card-label k-lb-ex">📜 例文（白文→書き下し→訳）</h2>\n%s\n  </section>\n'
                    % "\n".join(blocks))

    kunten = ""
    if d.get("kunten"):
        kunten = ('  <section class="k-card k-kunten">\n    <h2 class="k-card-label k-lb-kunten">✍️ 訓読のポイント</h2>\n'
                  '    <p class="k-kunten-text">%s</p>\n  </section>\n' % e(d["kunten"]))

    point = ""
    if d.get("point"):
        point = ('  <section class="k-card k-point">\n    <h2 class="k-card-label k-lb-point">⚠️ 識別・注意点</h2>\n'
                 '    <p class="k-point-text">%s</p>\n  </section>\n' % e(d["point"]))

    goro = ""
    if d.get("goro"):
        goro = ('  <section class="k-card k-goro">\n    <h2 class="k-card-label k-lb-goro">🧠 覚え方・ゴロ</h2>\n'
                '    <p class="k-goro-text">%s</p>\n  </section>\n' % e(d["goro"]))

    gogen = ""
    if d.get("gogen"):
        gogen = ('  <section class="k-card">\n    <h2 class="k-card-label k-lb-gogen">🏛 由来・成り立ち</h2>\n'
                 '    <p class="k-gogen-text">%s</p>\n  </section>\n' % e(d["gogen"]))

    kanren = ""
    if d.get("kanren"):
        chips = []
        for k in d["kanren"]:
            inner = ('<span class="k-chip-go">%s</span><span class="k-chip-imi">%s</span>'
                     % (e(k.get("go", "")), e(k.get("imi", ""))))
            if k.get("id"):
                chips.append('      <a class="k-chip" href="/exam/kanbun/%s.html">%s</a>' % (ea(k["id"]), inner))
            else:
                chips.append('      <span class="k-chip">%s</span>' % inner)
        kanren = ('  <section class="k-card">\n    <h2 class="k-card-label k-lb-kanren">🔗 関連・対照</h2>\n'
                  '    <div class="k-chips">\n%s\n    </div>\n  </section>\n' % "\n".join(chips))

    faq_html = ""
    if faq:
        items = "\n".join(
            ('      <div class="k-faq-item">\n        <p class="k-q">Q. %s</p>\n'
             '        <p class="k-a">%s</p>\n      </div>') % (e(f["q"]), e(f["a"])) for f in faq)
        faq_html = ('  <section class="k-card">\n    <h2 class="k-card-label k-lb-faq">❓ よくある質問</h2>\n'
                    '    <div class="k-faq">\n%s\n    </div>\n  </section>\n' % items)

    quiz = ""
    if d.get("quiz"):
        qs = []
        for i, q in enumerate(d["quiz"]):
            stem = ('Q%d. %s<br>\n        A&nbsp;%s &nbsp;&nbsp; B&nbsp;%s &nbsp;&nbsp; C&nbsp;%s &nbsp;&nbsp; D&nbsp;%s'
                    % (i + 1, e(q["q"]), e(q["A"]), e(q["B"]), e(q["C"]), e(q["D"])))
            qs.append('    <div class="k-quiz-q" data-correct="%s">\n      <div class="k-quiz-stem">%s\n      </div>\n'
                      '      <div class="k-quiz-choices">\n'
                      '        <button type="button" class="k-quiz-choice" data-ans="A">A</button>\n'
                      '        <button type="button" class="k-quiz-choice" data-ans="B">B</button>\n'
                      '        <button type="button" class="k-quiz-choice" data-ans="C">C</button>\n'
                      '        <button type="button" class="k-quiz-choice" data-ans="D">D</button>\n'
                      '      </div>\n      <div class="k-quiz-feedback"></div>\n    </div>'
                      % (ea(q.get("correct", "A")), stem))
        quiz = ('  <section class="k-card k-quiz-card">\n    <h2 class="k-card-label k-lb-quiz">🧩 確認クイズ</h2>\n'
                + "\n".join(qs) + '\n  </section>\n')

    ld_faq_block = ('<script type="application/ld+json">\n%s\n</script>\n'
                    % json.dumps(ld_faq, ensure_ascii=False, indent=2)) if ld_faq else ""

    return (
'<!DOCTYPE html>\n<html lang="ja">\n<head>\n'
'<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
'<title>%s の意味・用法・例文｜漢文用語辞典</title>\n'
'<meta name="description" content="%s">\n'
'<meta name="keywords" content="%s">\n'
'<link rel="canonical" href="%s">\n'
'<meta property="og:type" content="article">\n'
'<meta property="og:title" content="%s の意味・用法・例文｜漢文用語辞典">\n'
'<meta property="og:description" content="%s">\n'
'<script type="application/ld+json">\n%s\n</script>\n'
'<script type="application/ld+json">\n%s\n</script>\n'
'%s'
'<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css" crossorigin="anonymous">\n'
'<link rel="stylesheet" href="/exam/kanbun/kanbun.css">\n'
'<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>\n'
'<script data-ad-client="%s" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>\n'
'<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>\n'
'<script src="/common/js/common.js"></script>\n'
'<script>\n$(function(){ $("#header").load("/headermaster.html",function(){viewauth();}); setTimeout(function(){$("#footer").load("/footer.html");},1200); });\n'
'window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","%s");\n</script>\n'
'</head>\n<body>\n\n'
'<div id="header" style="min-height:40px"></div>\n\n'
'<div class="k-searchbar"><div id="kanbun-search"></div></div>\n\n'
'<main class="k-wrap">\n\n'
'  <header class="k-title-card">\n    <div class="k-title-row">\n      <h1 class="k-midashi">%s</h1>\n'
'      <span class="k-level k-level-%s">%s</span>\n    </div>\n'
'    <div class="k-kana">読み：%s</div>\n'
'    <div class="k-hinshi">%s</div>\n'
'    <div class="k-tags">\n      %s\n    </div>\n'
'    <p class="k-core">%s</p>\n  </header>\n\n'
'  <section class="k-card">\n    <h2 class="k-card-label k-lb-meaning">📖 意味・用法</h2>\n    <ol class="k-meaning-list">\n%s\n    </ol>\n  </section>\n\n'
'%s%s%s%s%s%s%s%s'
'  <div class="k-back">\n    <a href="%s" class="k-back-btn">← 漢文・漢詩 合格メニューへもどる</a>\n  </div>\n\n'
'  <ins class="adsbygoogle" style="display:block" data-ad-format="autorelaxed" data-ad-client="%s" data-ad-slot="3522844244"></ins>\n'
'  <script>(adsbygoogle=window.adsbygoogle||[]).push({});</script>\n\n'
'</main>\n\n<div id="footer"></div>\n\n'
'<script src="/exam/kanbun/kanbun.js"></script>\n'
'<script src="/exam/kanbun/kanbun-search.js"></script>\n'
'<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js" crossorigin="anonymous"></script>\n'
'<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js" crossorigin="anonymous"></script>\n'
'</body>\n</html>\n'
    ) % (
        mid, desc, kw, canon, mid, desc,
        json.dumps(ld_term, ensure_ascii=False, indent=2),
        json.dumps(ld_bc, ensure_ascii=False, indent=2),
        ld_faq_block,
        GA, ADSENSE, GA,
        mid, lvlc, e(lvl),
        e(d.get("yomi", "")),
        e(bunrui), tags, e(d.get("core", "")),
        meanings,
        examples, kunten, point, goro, gogen, kanren, faq_html, quiz,
        INDEX_PATH, ADSENSE,
    )


def load_words():
    words = []
    for path in sorted(glob.glob("kanbun_data/*.json")):
        with open(path, encoding="utf-8") as f:
            batch = json.load(f)
            if isinstance(batch, dict):
                batch = [batch]
            words.extend(batch)
    return words


def sort_key(d):
    return (d.get("kana") or d.get("yomi") or d["id"])


def write_links_snippet(words):
    """既存/新設 kanbunindex に貼り付けるためのリンク集（ハブは上書きしない）。"""
    order = ["最重要", "重要", "標準", "発展"]
    groups = {}
    for d in words:
        groups.setdefault(d.get("level", "標準"), []).append(d)
    parts = ['<!-- 自動生成：kanbunindex へ貼り付け用のリンク集。ハブ本体は上書きしません。 -->']
    for lvl in order + [g for g in groups if g not in order]:
        items = groups.get(lvl)
        if not items:
            continue
        parts.append('<h3 class="kanbun-idx-group">%s</h3>\n<ul class="kanbun-idx-list">' % e(lvl))
        for d in sorted(items, key=sort_key):
            parts.append('  <li><a href="/exam/kanbun/%s.html">%s</a>'
                         '<span class="kanbun-idx-core">%s</span></li>'
                         % (ea(d["id"]), e(d["midashi"]), e(d.get("core", ""))))
        parts.append('</ul>')
    with open(os.path.join(OUT, "_links_snippet.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")


def write_search_index(words):
    """検索用インデックス（kanbun-search.js が fetch する）。"""
    idx = []
    for d in sorted(words, key=sort_key):
        idx.append({
            "id": d["id"],
            "midashi": d["midashi"],
            "yomi": d.get("yomi", ""),
            "kana": d.get("kana", ""),
            "core": d.get("core", ""),
            "level": d.get("level", ""),
            "means": [m.get("gendai", "") for m in d.get("meanings", [])],
        })
    with open(os.path.join(OUT, "kanbun-index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    words = load_words()
    made = []
    seen = set()
    for d in words:
        wid = d["id"]
        if wid in seen:
            print("  ⚠ 重複ID:", wid)
        seen.add(wid)
        p = os.path.join(OUT, wid + ".html")
        with open(p, "w", encoding="utf-8") as f:
            f.write(build(d))
        made.append(os.path.basename(p))
    if words:
        write_links_snippet(words)
        write_search_index(words)
    print(f"{len(made)} ページを生成しました -> {OUT}/")
    for n in made:
        print("  ", n)
