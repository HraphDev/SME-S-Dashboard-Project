document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("successModal");
  const modalContent = document.getElementById("modalContent");

  if (window.showLoginSuccess && modal && modalContent) {
    modal.style.display = "flex";
    setTimeout(() => { modalContent.classList.add("show"); }, 50);

    let seconds = 10;
    const countdownEl = document.getElementById("countdown");
    const timer = setInterval(() => {
      seconds--;
      if (countdownEl) countdownEl.textContent = seconds;
      if (seconds <= 0) {
        clearInterval(timer);
        modalContent.classList.remove("show");
        setTimeout(() => {
          const url = modalContent.dataset.redirect || window.location.href;
          window.location.href = url;
        }, 400);
      }
    }, 1000);
  }
});
