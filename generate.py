#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, html, os, zipfile

OUT = "word/word"
GA = "G-MKNGEYPKNJ"
LD_SET_URL = "https://eigo-duke.com/word/word.html"

SPK = ('<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
       '<path d="M3 9v6h4l5 5V4L7 9H3z"/>'
       '<path class="wave" d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" opacity="0.7"/>'
       '<path class="wave" d="M19 12c0-3.53-2.04-6.58-5-8.05v2.23c2.02 1.29 3.38 3.55 3.38 5.82 0 2.27-1.36 4.53-3.38 5.82v2.23c2.96-1.47 5-4.52 5-8.05z" opacity="0.5"/></svg>')
EXSPK = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9v6h4l5 5V4L7 9H3z"/>'
         '<path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" opacity="0.7"/></svg>')
BM = ('<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
      '<path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>')

def e(s): return html.escape(str(s if s is not None else ""), quote=False)
def ea(s): return html.escape(str(s if s is not None else ""), quote=True)

def build(d):
    w = e(d["english"])
    fn = d["english"].lower()
    desc = e(d.get("description") or d.get("meaning_main",""))
    kw = ea(",".join(d.get("keywords", [])))
    ld1 = {
        "@context":"https://schema.org","@type":"DefinedTerm","name":d["english"],
        "description":d.get("description") or d.get("meaning_main",""),
        "inDefinedTermSet":{"@type":"DefinedTermSet","name":"英単語辞書","url":LD_SET_URL},
        "additionalProperty":[
            {"@type":"PropertyValue","name":"品詞","value":d.get("ld_pos") or d.get("hinshi","")},
            {"@type":"PropertyValue","name":"発音","value":"/"+d.get("pron","")+"/"},
            {"@type":"PropertyValue","name":"語源","value":d.get("ld_etym","")},
            {"@type":"PropertyValue","name":"英検レベル","value":d.get("ld_level","")},
        ],
    }
    faq = d.get("faq", [])
    faq_ld = None
    if faq:
        faq_ld = {"@context":"https://schema.org","@type":"FAQPage",
                  "mainEntity":[{"@type":"Question","name":f["q"],
                                 "acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in faq]}

    badges = "\n      ".join('<span class="word-badge">%s</span>' % e(b) for b in d.get("badges", []))

    meanings = "\n".join(
        ('      <li>\n        <span class="meaning-num">%d</span>\n        <span>\n'
         '          <span class="meaning-ja">%s</span>\n          <span class="meaning-note">%s</span>\n'
         '        </span>\n      </li>') % (i+1, e(m["hinshi"]), e(m["note"]))
        for i, m in enumerate(d.get("meanings", [])))

    usages = "\n".join(
        ('    <div class="usage-block">\n      <div class="usage-title">%s</div>\n'
         '      <div class="usage-desc">%s</div>\n      <div class="example-wrap">\n'
         '        <div class="example-en">%s\n'
         '          <button class="ex-speak-btn" data-word="%s" data-lang="en-US" aria-label="例文を聞く">%s</button>\n'
         '        </div>\n        <div class="example-ja">%s</div>\n      </div>\n    </div>') %
        (e(u["title"]), e(u["desc"]), e(u["example_en"]), ea(u["example_en"]), EXSPK, e(u["example_ja"]))
        for u in d.get("usages", []))

    warn = ""
    if d.get("warn"):
        warn = ('    <div class="warn-box">\n      ' +
                "<br>\n      ".join("⚠️ " + e(x) for x in d["warn"]) + "\n    </div>")

    etym = ""
    chain_data = d.get("etym_chain", [])
    if d.get("etym_note") or chain_data:
        chain = ""
        n = len(chain_data)
        for i, s in enumerate(chain_data):
            center = " flow-center" if i == n-1 else ""
            sub = ('<br><small>%s</small>' % e(s["sub"])) if s.get("sub") else ""
            chain += ('        <div class="flow-step" style="animation-delay:%.2fs">\n'
                      '          <div class="flow-node%s">%s%s</div>\n'
                      '          <div class="flow-era">%s</div>\n        </div>\n') % (i*0.18, center, e(s["node"]), sub, e(s.get("era","")))
            if i < n-1:
                dly = i*0.18+0.1
                chain += ('        <div class="flow-connector" style="animation-delay:%.2fs">\n'
                          '          <div class="flow-line" style="animation-delay:%.2fs"></div>\n'
                          '          <div class="flow-arrow"></div>\n        </div>\n') % (dly, dly)
        etym = ('  <div class="info-card">\n    <span class="card-label label-etym">🏛 語源・歴史</span>\n'
                '    <p class="etym-note">%s</p>\n    <div class="flow-scroll">\n      <div class="flow-chain">\n%s'
                '      </div>\n    </div>\n  </div>\n') % (e(d.get("etym_note","")), chain)

    phrases = ""
    if d.get("phrases"):
        items = "\n".join(
            ('      <div class="phrase-item" style="animation-delay:%.2fs">\n'
             '        <div class="phrase-en">%s</div>\n        <div class="phrase-ja">%s</div>\n      </div>') %
            (i*0.06, e(p["en"]), e(p["ja"])) for i, p in enumerate(d["phrases"]))
        phrases = ('  <div class="info-card">\n    <span class="card-label label-phrase">💬 %s を使った頻出表現</span>\n'
                   '    <div class="phrase-grid">\n%s\n    </div>\n  </div>\n') % (w, items)

    related = ""
    if d.get("related"):
        items = "\n".join(
            ('      <a class="word-chip" href="/word/word/%s.html" style="animation-delay:%.2fs">\n'
             '        <span class="chip-en">%s</span>\n        <span class="chip-ja">%s</span>\n      </a>') %
            (r["en"].lower(), i*0.07, e(r["en"]), e(r["ja"])) for i, r in enumerate(d["related"]))
        related = ('  <div class="info-card">\n    <span class="card-label label-related">🔗 関連語・あわせて覚えよう</span>\n'
                   '    <div class="chips-grid">\n%s\n    </div>\n  </div>\n') % items

    quiz = ""
    if d.get("quiz"):
        qs = []
        for i, q in enumerate(d["quiz"]):
            stem = ('Q%d. %s<br>\n        A&nbsp;%s &nbsp;&nbsp; B&nbsp;%s &nbsp;&nbsp; C&nbsp;%s &nbsp;&nbsp; D&nbsp;%s'
                    % (i+1, e(q["q"]), e(q["A"]), e(q["B"]), e(q["C"]), e(q["D"])))
            qs.append('    <div class="quiz-q" data-correct="%s">\n      <div class="quiz-blank">%s\n      </div>\n'
                      '      <div class="quiz-choices">\n'
                      '        <button type="button" class="quiz-choice" data-ans="A">A</button>\n'
                      '        <button type="button" class="quiz-choice" data-ans="B">B</button>\n'
                      '        <button type="button" class="quiz-choice" data-ans="C">C</button>\n'
                      '        <button type="button" class="quiz-choice" data-ans="D">D</button>\n'
                      '      </div>\n      <div class="quiz-feedback"></div>\n    </div>' % (ea(q.get("correct","A")), stem))
        quiz = ('  <div class="info-card quiz-card">\n    <span class="card-label label-quiz">🧩 確認クイズ</span>\n'
                + "\n".join(qs) + '\n    <div class="quiz-score" style="display:none"></div>\n  </div>\n')

    faq_ld_block = ('<script type="application/ld+json">\n%s\n</script>\n' % json.dumps(faq_ld, ensure_ascii=False, indent=2)) if faq_ld else ""

    return (
'<!DOCTYPE html>\n<html lang="ja">\n<head>\n'
'<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
'<title>%s の意味・使い方・語源・例文 | 英単語辞書</title>\n'
'<meta name="description" content="%s">\n'
'<meta name="keywords" content="%s">\n'
'<link rel="canonical" href="/word/word/%s.html">\n'
'<meta property="og:type" content="article">\n'
'<meta property="og:title" content="%s の意味・使い方・語源・例文 | 英単語辞書">\n'
'<meta property="og:description" content="%s">\n'
'<script type="application/ld+json">\n%s\n</script>\n'
'%s'
'<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css" crossorigin="anonymous">\n'
'<link rel="stylesheet" href="/word/style.css">\n'
'<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>\n'
'<script data-ad-client="ca-pub-3234684892462480" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>\n'
'<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>\n'
'<script src="/common/js/common.js"></script>\n'
'<script>\n$(function(){ $("#header").load("/headermaster.html",function(){viewauth();}); setTimeout(function(){$("#footer").load("/footer.html");},1200); });\n'
'window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","%s");\n</script>\n'
'<link rel="stylesheet" href="/word/word-page.css">\n</head>\n<body>\n\n'
'<div id="header" style="min-height:40px"></div>\n\n'
'<div class="search-header">\n  <form action="/word/word.html" method="get">\n'
'    <input type="text" name="word" placeholder="英単語を入力して検索" autocomplete="off"><!--\n    --><button type="submit">検索</button>\n  </form>\n</div>\n\n'
'<div class="main-wrap">\n\n'
'  <div class="word-title-card">\n    <div class="word-title-row">\n      <h1>%s</h1>\n'
'      <button class="speak-btn" data-word="%s" data-lang="en-US" title="発音を聞く" aria-label="発音を聞く">%s</button>\n'
'      <button class="bookmark-btn" data-word="%s" aria-label="単語帳に追加" title="単語帳に追加">%s</button>\n'
'      <span class="word-hinshi">%s</span>\n    </div>\n'
'    <div class="word-pron">発音：/%s/（%s）</div>\n'
'    <div class="word-badges">\n      %s\n    </div>\n'
'    <div class="word-meaning-main">%s</div>\n  </div>\n\n'
'  <div class="info-card">\n    <span class="card-label label-meaning">📖 主な意味</span>\n    <ul class="meaning-list">\n%s\n    </ul>\n  </div>\n\n'
'  <div class="info-card">\n    <span class="card-label label-usage">💡 使い方・例文</span>\n\n%s\n\n%s\n  </div>\n\n'
'%s%s%s%s'
'  <ins class="adsbygoogle" style="display:block" data-ad-format="autorelaxed" data-ad-client="ca-pub-3234684892462480" data-ad-slot="3522844244"></ins>\n'
'  <script>(adsbygoogle=window.adsbygoogle||[]).push({});</script>\n\n'
'</div>\n\n<div id="footer"></div>\n\n'
'<script src="/word/js/pronunciation.js"></script>\n'
'<script src="/word/js/wordbook.js"></script>\n'
'<script src="/word/js/quiz.js"></script>\n'
'<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js" crossorigin="anonymous"></script>\n'
'<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js" crossorigin="anonymous"></script>\n'
'</body>\n</html>\n'
) % (
        w, desc, kw, fn, w, desc,
        json.dumps(ld1, ensure_ascii=False, indent=2), faq_ld_block,
        GA, GA,
        w, ea(d["english"]), SPK, ea(d["english"]), BM, e(d.get("hinshi","")),
        e(d.get("pron","")), e(d.get("kana","")), badges, e(d.get("meaning_main","")),
        meanings, usages, warn, etym, phrases, related, quiz,
    )


# -------------------- データ読み込み & 生成 --------------------
import glob

def load_words():
    words = []
    for path in sorted(glob.glob("data/*.json")):
        with open(path, encoding="utf-8") as f:
            batch = json.load(f)
            if isinstance(batch, dict):
                batch = [batch]
            words.extend(batch)
    return words

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    words = load_words()
    made = []
    for d in words:
        p = os.path.join(OUT, d["english"].lower() + ".html")
        with open(p, "w", encoding="utf-8") as f:
            f.write(build(d))
        made.append(os.path.basename(p))
    print(f"{len(made)} ページを生成しました -> {OUT}/")
    for n in made:
        print("  ", n)
