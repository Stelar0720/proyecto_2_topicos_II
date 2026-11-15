"use strict";
const login = document.querySelector("#login-form");
if (login) login.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.querySelector("#login-message");
  const button = login.querySelector("button");
  button.disabled = true;
  try {
    const response = await fetch("/api/auth/login", {
      method: "POST", headers: {"Content-Type": "application/json"},
      credentials: "same-origin",
      body: JSON.stringify({username: login.username.value, password: login.password.value})
    });
    login.password.value = "";
    if (response.ok) { location.assign("/personal"); return; }
    const data = await response.json();
    message.textContent = data.error?.message || "No se pudo iniciar sesión";
  } catch { message.textContent = "No se pudo conectar. Vuelve a intentarlo."; }
  finally { button.disabled = false; }
});
const logout = document.querySelector("#logout");
if (logout) logout.addEventListener("click", async () => {
  try {
    const response = await fetch("/api/auth/logout", {method: "POST", credentials: "same-origin"});
    if (response.ok) location.assign("/acceso");
    else document.querySelector("#logout-message").textContent = "No se pudo cerrar la sesión";
  } catch { document.querySelector("#logout-message").textContent = "No se pudo conectar"; }
});
