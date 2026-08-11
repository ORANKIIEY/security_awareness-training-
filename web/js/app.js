/**
 * Phishing awareness training — quiz / reveal controls
 * TRAINING EXAMPLE — DO NOT SEND
 */
(function () {
  const revealBtn = document.getElementById("reveal-btn");
  const hideBtn = document.getElementById("hide-btn");
  const statusHint = document.getElementById("quiz-hint");

  if (!revealBtn) return;

  function setRevealed(on) {
    document.body.classList.toggle("revealed", on);
    revealBtn.hidden = on;
    if (hideBtn) hideBtn.hidden = !on;
    if (statusHint) {
      statusHint.textContent = on
        ? "Red flags revealed — scroll for psychology and checklist links."
        : "Quiz mode: find the red flags, then reveal the answer key.";
    }
    if (on) {
      const panel = document.getElementById("answer-key");
      if (panel) panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }

  revealBtn.addEventListener("click", function () {
    setRevealed(true);
  });

  if (hideBtn) {
    hideBtn.addEventListener("click", function () {
      setRevealed(false);
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // Dead links: never navigate training CTAs
  document.querySelectorAll('a[data-training-dead-link]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
    });
  });
})();
