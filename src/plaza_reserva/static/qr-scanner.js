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
    let stop = () => { stream.getTracks().forEach(track => track.stop()); container.remove(); };
    close.addEventListener("click", () => stop());
    await video.play();
    if (!window.BarcodeDetector) {
      stream.getTracks().forEach(track => track.stop());
      video.remove();
      status.textContent = "Preparando lector QR compatible…";
      if (!window.Html5Qrcode) {
        status.textContent = "No se pudo cargar el lector QR compatible. Verifica tu conexión o escribe el código manualmente.";
        return;
      }
      const scannerId = `qr-fallback-${Date.now()}`;
      const scannerElement = document.createElement("div");
      scannerElement.id = scannerId;
      container.prepend(scannerElement);
      const scanner = new Html5Qrcode(scannerId);
      const closeFallback = () => scanner.stop().catch(() => {}).finally(() => container.remove());
      stop = closeFallback;
      try {
        await scanner.start({facingMode: "environment"}, {fps: 10, qrbox: {width: 240, height: 240}},
          value => { input.value = value; closeFallback(); }, () => {});
        status.textContent = "Apunta la cámara al código QR.";
      } catch {
        status.textContent = "No se pudo iniciar el lector QR. Revisa el permiso de cámara e inténtalo de nuevo.";
      }
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
