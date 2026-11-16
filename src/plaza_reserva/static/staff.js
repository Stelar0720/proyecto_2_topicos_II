"use strict";
const dialog = document.querySelector("#booking-dialog");
if (dialog) {
  document.querySelectorAll("[data-booking]").forEach(button => button.addEventListener("click", () => {
    dialog.querySelectorAll("article").forEach(article => { article.hidden = true; });
    const detail = dialog.querySelector(`#booking-${button.dataset.booking}`);
    if (detail) { detail.hidden = false; dialog.showModal(); }
  }));
  dialog.querySelector("[data-dialog-close]").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
}
