/* 古文単語 検索ウィジェット（依存なし・自己完結）
 *
 * 使い方：任意のページに次を置くだけ。
 *   <div id="koten-search"></div>
 *   <script src="/exam/koten/koten-search.js"></script>
 *
 * 見出し（歴史的仮名遣い）・現代仮名遣い・読み・意味・コアで部分一致検索し、
 * 候補をクリック（またはEnter）で /exam/koten/{id}.html へ遷移します。
 * インデックスは /exam/koten/koten-index.json（generate_koten.py が自動生成）。
 */
(function () {
  "use strict";
  if (window.__kotenSearchInit) return;
  window.__kotenSearchInit = true;

  var INDEX_URL = "/exam/koten/koten-index.json";
  var LEVEL_COLOR = { "最重要": "#c0392b", "重要": "#d68910", "標準": "#5b8a72", "発展": "#5b6bbf" };
  var MAX = 12;

  // カタカナ→ひらがな＋小文字化（ひらがな入力でも読み(カナ)にヒットさせる）
  function norm(s) {
    s = (s || "").toLowerCase();
    var out = "";
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      out += (c >= 0x30a1 && c <= 0x30f6) ? String.fromCharCode(c - 0x60) : s[i];
    }
    return out;
  }

  function injectCSS() {
    if (document.getElementById("koten-search-css")) return;
    var css = ''
      + '.ks-wrap{position:relative;max-width:520px;margin:14px auto 0;padding:0 14px;font-family:-apple-system,BlinkMacSystemFont,"Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,sans-serif;}'
      + '.ks-form{display:flex;gap:8px;}'
      + '.ks-input{flex:1;min-width:0;padding:11px 14px;font-size:16px;border:2px solid #d8c9a8;border-radius:12px;background:#fffdf8;color:#2b2620;outline:none;}'
      + '.ks-input:focus{border-color:#a8843f;box-shadow:0 0 0 3px rgba(168,132,63,.18);}'
      + '.ks-btn{flex:0 0 auto;padding:0 16px;border:none;border-radius:12px;background:#7c5c2e;color:#fff;font-weight:700;font-size:15px;cursor:pointer;}'
      + '.ks-btn:hover{background:#a8843f;}'
      + '.ks-box{display:none;position:absolute;left:14px;right:14px;top:100%;margin-top:6px;background:#fff;border:1px solid #e7ddcd;border-radius:12px;box-shadow:0 12px 30px rgba(80,60,20,.22);overflow:hidden;max-height:66vh;overflow-y:auto;z-index:400;}'
      + '.ks-item{display:flex;align-items:center;gap:10px;padding:10px 14px;text-decoration:none;color:#2b2620;border-bottom:1px solid #f2ece0;cursor:pointer;}'
      + '.ks-item:last-child{border-bottom:none;}'
      + '.ks-item.on,.ks-item:hover{background:#f6efdf;}'
      + '.ks-main{display:flex;flex-direction:column;min-width:0;flex:1;}'
      + '.ks-mid{font-family:"Hiragino Mincho ProN","Yu Mincho",serif;font-size:17px;font-weight:700;color:#3a2f22;line-height:1.25;}'
      + '.ks-core{font-size:12.5px;color:#6f665a;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}'
      + '.ks-lv{flex:0 0 auto;font-size:10.5px;font-weight:700;color:#fff;border-radius:6px;padding:2px 7px;white-space:nowrap;}'
      + '.ks-empty{padding:14px;font-size:13px;color:#999;text-align:center;}'
      + '.ks-hint{margin:6px 14px 0;font-size:11.5px;color:#8a8072;}';
    var st = document.createElement("style");
    st.id = "koten-search-css";
    st.textContent = css;
    document.head.appendChild(st);
  }

  var _data = null, _promise = null;
  function loadIndex() {
    if (_data) return Promise.resolve(_data);
    if (_promise) return _promise;
    _promise = fetch(INDEX_URL, { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (j) {
        _data = (j || []).map(function (d) {
          d._q = norm([d.midashi, d.kana, d.yomi, d.core].concat(d.means || []).join(" "));
          d._h = norm(d.midashi + " " + d.kana + " " + d.yomi);
          return d;
        });
        return _data;
      })
      .catch(function () { _data = []; return _data; });
    return _promise;
  }

  function search(data, q) {
    q = norm(q).trim();
    if (!q) return [];
    var hits = [];
    for (var i = 0; i < data.length; i++) {
      var d = data[i];
      if (d._q.indexOf(q) === -1) continue;
      // 見出し/読みの前方一致を上位に
      d._rank = d._h.indexOf(q) === 0 ? 0 : (d._h.indexOf(q) !== -1 ? 1 : 2);
      hits.push(d);
    }
    hits.sort(function (a, b) { return a._rank - b._rank; });
    return hits.slice(0, MAX);
  }

  function build(container) {
    var wrap = document.createElement("div");
    wrap.className = "ks-wrap";
    wrap.innerHTML =
      '<form class="ks-form" action="#" autocomplete="off">' +
        '<input class="ks-input" type="text" placeholder="古文単語を検索（見出し・読み・意味）" ' +
          'autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" ' +
          'role="combobox" aria-autocomplete="list" aria-expanded="false">' +
        '<button class="ks-btn" type="submit" aria-label="検索">検索</button>' +
      '</form>' +
      '<div class="ks-box" role="listbox"></div>';
    container.appendChild(wrap);

    var input = wrap.querySelector(".ks-input");
    var box = wrap.querySelector(".ks-box");
    var form = wrap.querySelector(".ks-form");
    var active = -1, current = [];

    function close() { box.style.display = "none"; input.setAttribute("aria-expanded", "false"); active = -1; }
    function go(d) { if (d) window.location.href = "/exam/koten/" + d.id + ".html"; }

    function render(list) {
      current = list; active = -1;
      if (!list.length) {
        box.innerHTML = '<div class="ks-empty">該当する古文単語が見つかりません</div>';
        box.style.display = "block"; input.setAttribute("aria-expanded", "true");
        return;
      }
      var h = "";
      for (var i = 0; i < list.length; i++) {
        var d = list[i];
        var col = LEVEL_COLOR[d.level] || "#8a8072";
        h += '<a class="ks-item" role="option" data-id="' + d.id + '">' +
               '<span class="ks-main"><span class="ks-mid">' + esc(d.midashi) + '</span>' +
               '<span class="ks-core">' + esc(d.core || (d.means && d.means[0]) || "") + '</span></span>' +
               (d.level ? '<span class="ks-lv" style="background:' + col + '">' + esc(d.level) + '</span>' : '') +
             '</a>';
      }
      box.innerHTML = h;
      box.style.display = "block"; input.setAttribute("aria-expanded", "true");
    }

    function esc(s) {
      return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
      });
    }

    function highlight() {
      var items = box.querySelectorAll(".ks-item");
      for (var i = 0; i < items.length; i++) items[i].classList.toggle("on", i === active);
      if (active >= 0 && items[active]) items[active].scrollIntoView({ block: "nearest" });
    }

    input.addEventListener("input", function () {
      var q = input.value;
      if (!q.trim()) { close(); return; }
      loadIndex().then(function (data) {
        if (input.value === q) render(search(data, q));
      });
    });

    input.addEventListener("keydown", function (ev) {
      if (box.style.display !== "block") return;
      if (ev.key === "ArrowDown") { ev.preventDefault(); active = Math.min(active + 1, current.length - 1); highlight(); }
      else if (ev.key === "ArrowUp") { ev.preventDefault(); active = Math.max(active - 1, -1); highlight(); }
      else if (ev.key === "Enter") { if (active >= 0) { ev.preventDefault(); go(current[active]); } }
      else if (ev.key === "Escape") { close(); }
    });

    box.addEventListener("mousedown", function (ev) {
      var a = ev.target.closest ? ev.target.closest(".ks-item") : null;
      if (!a) return;
      ev.preventDefault();
      var id = a.getAttribute("data-id");
      var d = current.filter(function (x) { return x.id === id; })[0];
      go(d);
    });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (current.length) go(active >= 0 ? current[active] : current[0]);
    });

    input.addEventListener("focus", function () { if (input.value.trim() && current.length) box.style.display = "block"; });
    document.addEventListener("click", function (ev) { if (!wrap.contains(ev.target)) close(); });

    // インデックスを先読み（初回入力を速く）
    loadIndex();
  }

  function init() {
    var hosts = document.querySelectorAll("#koten-search");
    if (!hosts.length) return;
    injectCSS();
    for (var i = 0; i < hosts.length; i++) {
      if (hosts[i].getAttribute("data-ks") === "1") continue;
      hosts[i].setAttribute("data-ks", "1");
      build(hosts[i]);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
