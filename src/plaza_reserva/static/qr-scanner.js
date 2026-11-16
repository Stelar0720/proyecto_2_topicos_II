"use strict";
document.querySelectorAll("[data-qr-target]").forEach((button) => {
  button.addEventListener("click", async () => {
    const input = document.getElementById(button.dataset.qrTarget);
    if (!input || !window.BarcodeDetector || !navigator.mediaDevices?.getUserMedia) {
      alert("Tu navegador no permite leer QR con cámara. Escribe el código manualmente.");
      return;
    }
    const video = document.createElement("video");
    const stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: "environment"}});
    video.srcObject = stream; await video.play();
    const detector = new BarcodeDetector({formats: ["qr_code"]});
    const timer = setInterval(async () => {
      const codes = await detector.detect(video);
      if (codes[0]?.rawValue) { input.value = codes[0].rawValue; clearInterval(timer); stream.getTracks().forEach(t => t.stop()); video.remove(); }
    }, 300);
    document.body.append(video); video.className = "qr-camera";
  });
});
