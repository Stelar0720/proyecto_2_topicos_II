#!/usr/bin/env bash
# Ejecutar en Git Bash desde la PC del usuario. No fusiona ni usa force.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."

branch='base/plaza-reserva'
repository='Stelar0720/proyecto_2_topicos_II'
for program in git gh python; do
  command -v "$program" >/dev/null || { printf 'Falta %s en PATH.\n' "$program"; exit 1; }
done

remote_url=$(git remote get-url origin)
case "$remote_url" in
  "https://github.com/$repository"|"https://github.com/$repository.git"|"git@github.com:$repository.git") ;;
  *) printf 'origin no corresponde al repositorio esperado. No se hicieron cambios.\n'; exit 1 ;;
esac
git var GIT_AUTHOR_IDENT >/dev/null || {
  printf 'Configura tu nombre y correo reales de Git antes de reintentar.\n'; exit 1;
}
gh repo view "$repository" --json viewerPermission
if [[ -n $(git diff --cached --name-only) ]]; then
  printf 'Hay archivos previamente preparados en el índice. Revísalos antes de reintentar.\n'
  exit 1
fi

git fetch origin
git show-ref --verify --quiet "refs/remotes/origin/$branch" || {
  printf 'No se encontró la rama remota existente. No se creará un historial distinto.\n'; exit 1;
}

if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  # Caso verificado: carpeta local sin commits; archivos de trabajo se conservan.
  if [[ "$(git rev-parse "origin/$branch")" != 'e279839177e31a3b80b6276242d2ed5621475c90' ]]; then
    printf 'La rama remota cambió desde la última inspección. Revisarla antes de enlazar esta copia.\n'
    exit 1
  fi
  if git show-ref --verify --quiet "refs/heads/$branch"; then
    printf 'La rama local ya existe con otro estado; revisar antes de continuar.\n'; exit 1
  fi
  git switch --orphan "$branch"
  git reset --mixed "origin/$branch"
else
  current_branch=$(git branch --show-current)
  if [[ "$current_branch" != "$branch" ]]; then
    printf 'Se esperaba la rama %s; estás en %s. No se cambió tu rama.\n' "$branch" "$current_branch"
    exit 1
  fi
  git merge-base --is-ancestor "origin/$branch" HEAD || {
    printf 'La rama remota avanzó o el historial difiere. Integra esos cambios antes de reintentar.\n'; exit 1;
  }
fi

# Lista explícita: no se suben .env, bases, .tmp, entornos o credenciales.
git add -- README.md AGENTS.md .gitignore .env.example pyproject.toml alembic.ini \
  DSaIA-Proyecto2.pdf DSaIA-Tema9.pdf src tests migrations specs docs scripts .github
git diff --cached --check
git diff --cached --stat
if ! git diff --cached --quiet; then
  git commit -m 'BASE-01 BASE-02: completar especificaciones y esqueleto compartido'
fi
git push -u origin "HEAD:refs/heads/$branch"

pr_url=$(gh pr list --repo "$repository" --head "$branch" --base main --state open \
  --json url --jq '.[0].url // empty')
if [[ -z "$pr_url" ]]; then
  pr_url=$(gh pr create --repo "$repository" --base main --head "$branch" --draft \
    --title 'BASE-01/02: especificaciones y base compartida de Plaza Reserva' \
    --body-file docs/initial-pr.md)
fi

BASE_PR_URL="$pr_url" BASE_PUBLISHED_SHA="$(git rev-parse HEAD)" python - <<'PY'
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os

url = os.environ['BASE_PR_URL']
state_path = Path('docs/github-state.json')
state = json.loads(state_path.read_text(encoding='utf-8'))
state['pull_request'] = url
state['published_commit'] = os.environ['BASE_PUBLISHED_SHA']
state['branch'] = 'base/plaza-reserva'
state['last_error'] = None
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
readme = Path('README.md')
text = readme.read_text(encoding='utf-8')
if url not in text:
    text += f'\nPR inicial (sin fusionar): [base compartida]({url}).\n'
    readme.write_text(text, encoding='utf-8')
log = Path('docs/ai-log.md')
text = log.read_text(encoding='utf-8')
if f'Publicación por script: {url}' not in text:
    timestamp = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    text += (f'\n- {timestamp}: Publicación por script: {url}. Rama base/plaza-reserva '
             'publicada desde su historial remoto; PR creado o reutilizado sin fusión. '
             'No equivale a ejecución de pruebas ni aceptación humana.\n')
    log.write_text(text, encoding='utf-8')
PY
git add -- README.md docs/github-state.json docs/ai-log.md
if ! git diff --cached --quiet; then
  git commit -m 'BASE-01 BASE-02: registrar PR inicial y publicación real'
  git push origin "HEAD:refs/heads/$branch"
fi
printf '\nPublicación completada. PR sin fusionar: %s\n' "$pr_url"
printf 'El workflow debe ejecutar las pruebas; no se afirma CI aprobado.\n'
