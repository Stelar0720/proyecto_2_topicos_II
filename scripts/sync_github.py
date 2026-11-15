"""Publicación reintentable del backlog; sin credenciales, assignees o cierres supuestos.

Por defecto solo muestra plan. --publish crea/reutiliza issues y Project.
No crea ramas/commits/PR ni sustituye revisión humana.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = "Stelar0720/proyecto_2_topicos_II"
OWNER = "Stelar0720"
TITLE = "Plaza Reserva - Proyecto 2"
STATES = ["Pendiente", "Listo", "En desarrollo", "En revisión", "Terminado"]
STATE_FILE = ROOT / "docs/github-state.json"


def gh(*args, json_output=False):
    result = subprocess.run(["gh", *args], cwd=ROOT, text=True, encoding="utf-8",
                            capture_output=True, timeout=90)
    if result.returncode:
        # Solo comandos públicos de gh; nunca auth token ni captura de secretos.
        raise RuntimeError(result.stderr.strip() or "GitHub CLI devolvió error")
    return json.loads(result.stdout) if json_output else result.stdout.strip()


def save(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sync_issues(backlog, state):
    existing = gh("issue", "list", "--repo", REPO, "--state", "all", "--limit", "1000",
                  "--json", "number,title,url", json_output=True)
    if len(existing) >= 1000:
        raise RuntimeError("Se alcanzó el límite de búsqueda; paginar antes de publicar sin duplicados")
    labels = {row["name"] for row in gh("label", "list", "--repo", REPO, "--limit", "1000",
                                       "--json", "name", json_output=True)}
    for label, color in (("base", "0E8A16"), ("historia", "1D76DB"), ("qa", "5319E7"), ("entrega", "FBCA04")):
        if label not in labels:
            gh("label", "create", label, "--repo", REPO, "--color", color,
               "--description", "Backlog inicial de Plaza Reserva")
    for task in backlog:
        prefix = task["id"] + ":"
        matches = [item for item in existing if item["title"].startswith(prefix)]
        if len(matches) > 1:
            raise RuntimeError(f"Duplicados existentes para {task['id']}; revisar manualmente")
        if matches:
            issue = matches[0]
        else:
            url = gh("issue", "create", "--repo", REPO, "--title", f"{task['id']}: {task['title']}",
                     "--body-file", str(ROOT / "docs/issues" / f"{task['id']}.md"),
                     "--label", task["label"])
            issue = gh("issue", "view", url, "--repo", REPO, "--json", "number,title,url", json_output=True)
            existing.append(issue)
        state["issues"][task["id"]] = issue["url"]
        save(state)  # Guardar progreso parcial real antes de cualquier paso posterior.


def sync_project(state):
    projects = gh("project", "list", "--owner", OWNER, "--limit", "1000", "--format", "json", json_output=True)
    rows = projects["projects"]
    if len(rows) >= 1000:
        raise RuntimeError("Se alcanzó límite de Projects; revisar paginación")
    matches = [p for p in rows if p["title"] == TITLE]
    if len(matches) > 1:
        raise RuntimeError("Hay varios Projects con el título dedicado; seleccionar uno sin duplicar")
    project = matches[0] if matches else gh("project", "create", "--owner", OWNER,
                                           "--title", TITLE, "--format", "json", json_output=True)
    number = str(project["number"])
    state["project"] = {"number": project["number"], "id": project["id"], "url": project.get("url")}
    save(state)
    gh("project", "link", number, "--owner", OWNER, "--repo", REPO)
    fields = gh("project", "field-list", number, "--owner", OWNER, "--limit", "100",
                "--format", "json", json_output=True)["fields"]
    state_field = next((f for f in fields if f["name"] in {"Status", "Estado"}
                        and all(name in {o["name"] for o in f.get("options", [])} for name in STATES)), None)
    if state_field is None:
        state_field = gh("project", "field-create", number, "--owner", OWNER, "--name", "Estado",
                         "--data-type", "SINGLE_SELECT", "--single-select-options", ",".join(STATES),
                         "--format", "json", json_output=True)
    options = {o["name"]: o["id"] for o in state_field.get("options", [])}
    if not all(name in options for name in STATES):
        raise RuntimeError("El campo Estado existente no contiene las cinco opciones; ajustar sin borrar valores")
    items = gh("project", "item-list", number, "--owner", OWNER, "--limit", "1000",
               "--format", "json", json_output=True)["items"]
    if len(items) >= 1000:
        raise RuntimeError("Se alcanzó límite de items; revisar paginación")
    existing_urls = {i.get("content", {}).get("url") for i in items}
    for url in state["issues"].values():
        if url in existing_urls:
            continue  # Nunca retroceder avances reales del equipo al reintentar.
        item = gh("project", "item-add", number, "--owner", OWNER, "--url", url,
                  "--format", "json", json_output=True)
        gh("project", "item-edit", "--id", item["id"], "--project-id", project["id"],
           "--field-id", state_field["id"], "--single-select-option-id", options["Pendiente"])
    state["board_view_pending"] = True  # La vista Board agrupada se configura/verifica en UI.
    save(state)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    backlog = json.loads((ROOT / "docs/backlog.json").read_text(encoding="utf-8"))
    if not args.publish:
        for item in backlog:
            print(f"{item['id']}: {item['title']} ({item['owner']})")
        print("Sin cambios remotos. Para publicar: python scripts/sync_github.py --publish")
        return
    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    try:
        repo = gh("repo", "view", REPO, "--json", "nameWithOwner,viewerPermission,isEmpty", json_output=True)
        if repo["viewerPermission"] not in {"ADMIN", "MAINTAIN", "WRITE"}:
            raise RuntimeError("Faltan permisos de escritura sobre el repositorio")
        sync_issues(backlog, state)
        sync_project(state)
        state["last_error"] = None
        save(state)
        print("Issues y Project sincronizados; verificar vista Board según docs/github-project-setup.md")
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
        state["last_error"] = str(exc)
        save(state)
        print(f"Publicación incompleta: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
