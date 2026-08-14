/* 古文単語辞典：確認クイズの正誤判定（依存なし・自己完結） */
(function () {
  "use strict";
  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest ? ev.target.closest(".k-quiz-choice") : null;
    if (!btn) return;
    var q = btn.closest(".k-quiz-q");
    if (!q || q.dataset.answered === "1") return;
    var correct = q.getAttribute("data-correct");
    var picked = btn.getAttribute("data-ans");
    q.dataset.answered = "1";
    var fb = q.querySelector(".k-quiz-feedback");
    q.querySelectorAll(".k-quiz-choice").forEach(function (b) {
      b.disabled = true;
      if (b.getAttribute("data-ans") === correct) b.classList.add("correct");
    });
    if (picked === correct) {
      btn.classList.add("correct");
      if (fb) { fb.textContent = "正解！"; fb.style.color = "#5b8a72"; }
    } else {
      btn.classList.add("wrong");
      if (fb) { fb.textContent = "不正解 … 正解は " + correct; fb.style.color = "#c0392b"; }
    }
  });
})();
