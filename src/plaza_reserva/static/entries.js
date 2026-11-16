"use strict";
const printButton = document.querySelector("#print-ticket");
if (printButton) printButton.addEventListener("click", () => window.print());
