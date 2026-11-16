"use strict";
document.querySelectorAll("[data-qr-target]").forEach((button) => {
  button.addEventListener("click", async () => {
    const input = document.getElementById(button.dataset.qrTarget);
    if (!input || !navigator.mediaDevices?.getUserMedia) {
      alert("Tu navegador no permite acceder a la cámara. Usa un navegador actualizado o escribe el código manualmente.");
      return;
    }
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: "environment"}});
    } catch {
      alert("No se pudo abrir la cámara. Revisa el permiso de cámara del navegador y vuelve a intentar.");
      return;
    }
    const container = document.createElement("section");
    const video = document.createElement("video");
    const status = document.createElement("p");
    const close = document.createElement("button");
    video.srcObject = stream;
    video.className = "qr-camera";
    video.playsInline = true;
    close.type = "button";
    close.textContent = "Cerrar cámara";
    container.className = "qr-camera-panel";
    container.append(video, status, close);
    document.body.append(container);
    const stop = () => { stream.getTracks().forEach(track => track.stop()); container.remove(); };
    close.addEventListener("click", stop);
    await video.play();
    if (!window.BarcodeDetector) {
      status.textContent = "La cámara está activa, pero este navegador no puede leer QR automáticamente. Prueba con Chrome o Edge, o escribe el código manualmente.";
      return;
    }
    status.textContent = "Apunta la cámara al código QR.";
    const detector = new BarcodeDetector({formats: ["qr_code"]});
    const timer = setInterval(async () => {
      try {
        const codes = await detector.detect(video);
        if (codes[0]?.rawValue) { input.value = codes[0].rawValue; clearInterval(timer); stop(); }
      } catch { clearInterval(timer); status.textContent = "No se pudo leer el QR. Intenta de nuevo o escribe el código manualmente."; }
    }, 300);
  });
});
