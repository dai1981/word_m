/* =====================================================================
   漢文セクション共通JS  /exam/kanbun/kanbun.js
   ・クイズエンジン（bunpoCategory / quizCategory）は変更しない
   ・このファイルは各ページの </body> 直前、エンジン読込後に置く
   ===================================================================== */
(function () {
  'use strict';

  // 1) 音声読み上げを止める
  //    エンジンは問題文(HTMLタグ入り)を英語音声で読むため、漢文ページでは無効化する。
  //    body に class="kanbun-page" があるページだけが対象。
  var isKanbunPage = document.body && /\bkanbun-page\b/.test(document.body.className);
  if (isKanbunPage) {
    try {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak = function () { /* 漢文ページでは読み上げない */ };
      }
    } catch (e) {}
    // quizInit 後に自動再生フラグが true に戻っても再生しないよう、念のため false に保つ
    var keepAudioOff = function () { try { window.autoaudio = false; } catch (e) {} };
    if (window.jQuery) { jQuery(function () { setTimeout(keepAudioOff, 0); }); } else { keepAudioOff(); }
  }

  // 2) ページ内リンクのスムーズスクロール
  //    <a href="#id" data-kb-scroll> または <div data-kb-scroll="#id"> で動く（onclick 直書き不要）
  function scrollToId(hash) {
    if (!hash || hash.charAt(0) !== '#') return false;
    var el = document.getElementById(hash.slice(1));
    if (!el) return false;
    try { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (e) { el.scrollIntoView(true); }
    if (window.history && history.replaceState) { history.replaceState(null, '', hash); }
    return true;
  }
  document.addEventListener('click', function (ev) {
    var t = ev.target;
    while (t && t !== document) {
      if (t.hasAttribute && t.hasAttribute('data-kb-scroll')) {
        var target = t.getAttribute('data-kb-scroll') || t.getAttribute('href');
        if (scrollToId(target)) ev.preventDefault();
        return;
      }
      t = t.parentNode;
    }
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Enter' && ev.key !== ' ') return;
    var t = ev.target;
    if (t && t.getAttribute && t.getAttribute('role') === 'button' && t.hasAttribute('data-kb-scroll')) {
      if (scrollToId(t.getAttribute('data-kb-scroll'))) ev.preventDefault();
    }
  });
})();

/* =====================================================================
   ★ 漢文用語辞典ページ（generate_kanbun.py 生成）用：確認クイズの正誤判定
   ・辞書ページの選択肢ボタン .k-quiz-choice だけを対象（既存エンジンと非干渉）
   ・依存なし・自己完結。既存のクイズエンジンには一切触れない。
   ===================================================================== */
(function () {
  'use strict';
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest ? ev.target.closest('.k-quiz-choice') : null;
    if (!btn) return;
    var q = btn.closest('.k-quiz-q');
    if (!q || q.dataset.answered === '1') return;
    var correct = q.getAttribute('data-correct');
    var picked = btn.getAttribute('data-ans');
    q.dataset.answered = '1';
    var fb = q.querySelector('.k-quiz-feedback');
    q.querySelectorAll('.k-quiz-choice').forEach(function (b) {
      b.disabled = true;
      if (b.getAttribute('data-ans') === correct) b.classList.add('correct');
    });
    if (picked === correct) {
      btn.classList.add('correct');
      if (fb) { fb.textContent = '正解！'; fb.style.color = '#006633'; }
    } else {
      btn.classList.add('wrong');
      if (fb) { fb.textContent = '不正解 … 正解は ' + correct; fb.style.color = '#c0392b'; }
    }
  });
})();
