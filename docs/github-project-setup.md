# GitHub: estado real y reanudación sin duplicados

## Vía preparada para Git Bash

Desde Git Bash abierto en esta carpeta: `bash scripts/publish-base.sh`.
El script verifica repositorio/identidad, conserva los commits de la rama remota,
agrega solo archivos del proyecto y abre/reutiliza un PR borrador. No fusiona,
no usa force ni vuelve a crear issues/Project. Si hay un estado Git inesperado,
se detiene. Su ejecución real queda pendiente hasta que el usuario lo ejecute.

El remoto local origin ya apunta a `Stelar0720/proyecto_2_topicos_II`.
Las consultas de permisos/repositorio/issues/Projects fallaron por proxy inaccesible
`127.0.0.1:9`. No se concluye que el token sea inválido a partir de ese fallo.
Después se conectó GitHub y se verificó la cuenta Stelar0720 y el repositorio;
existe `main` en commit `973432095fbd2ea9f40d9125b7cc35af9a2e1b6e` (Initial commit,
README mínimo). La consulta de issues devolvió lista vacía. Intentos de crear
BASE-01 y `base/plaza-reserva` devolvieron 403 `Resource not accessible by integration`.
Estos fallos describen los intentos iniciales. Después, la sesión de navegador
abierta por el usuario sí permitió crear Project 4, issues #1–9 y rama
`base/plaza-reserva`. Estado actual y URLs: `github-state.json`. No recrearlos.
Las URLs verificadas se guardarán en `github-state.json`; valores nulos no son enlaces.
Los cuerpos locales de issues están en `docs/issues/`, no equivalen a un tablero.
La cuenta posee permisos sobre el repositorio, pero esta integración no autoriza
esas escrituras. No confundir el permiso de la cuenta con el alcance de la conexión.
Las herramientas conectadas tampoco ofrecen administración de Projects.

## Publicar/reintentar backlog

Desde raíz con Python y GitHub CLI autenticada, en un entorno con acceso:

```powershell
gh auth status
gh repo view Stelar0720/proyecto_2_topicos_II --json viewerPermission,isEmpty,defaultBranchRef
python scripts/sync_github.py
python scripts/sync_github.py --publish
```

Solo usar como sincronización de faltantes. El script comprueba permiso WRITE/MAINTAIN/ADMIN, busca IDs en issues abiertos y
cerrados, reutiliza coincidencia única, crea solo faltantes, deja assignees vacíos,
y registra URLs reales tras cada creación. No sobreescribe cuerpos editados por
el equipo. Busca Project con título exacto `Plaza Reserva - Proyecto 2`, crea solo
si no existe y lo vincula al repositorio. Si hay varios, se detiene sin elegir.
Ante error en Projects se conservan issues ya creados; reintentar no los duplica.

Si falta permiso Projects y `gh` lo indica explícitamente, en la terminal local:
`gh auth refresh -h github.com -s project`. Completa tú cualquier autenticación
interactiva; no compartas tokens por chat. No ejecutar refresh solo por fallo de red.

## Terminar la vista del tablero (paso manual verificable)

1. Abre la URL real de Project registrada en `github-state.json`.
2. La vista Board ya está creada y agrupada por **Status** con las cinco opciones.
3. Ordena columnas: Pendiente → Listo → En desarrollo → En revisión → Terminado.
4. Verifica que los nueve issues del manifiesto están agregados. El script crea
   opciones y agrega items, pero no afirma haber configurado/verificado esa vista.
5. El flujo de este equipo usa el campo **Status** ya configurado. El script
   reutiliza Status o Estado si contiene las cinco opciones; no borra avances.
6. BASE solo pasa a En revisión tras implementar **y ejecutar** sus verificaciones.
   Terminado requiere aceptación/revisión humana; nadie está asignado sin usuario verificado.

Si solo tienes permisos de issues: usa los mismos issues creados, agrega sus URLs
al Project mediante Add item o `gh project item-add NUMERO --owner Stelar0720 --url URL`.
No vuelvas a crearlos. Los IDs se pueden usar para buscar y verificar duplicados.

## Rama y PR inicial

La rama remota es `base/plaza-reserva`, creada por navegador desde main. La sesión
no pudo escribir `.git/HEAD.lock`; el local sigue main sin commits. La publicación
web conserva ese estado local sin sincronizarlo; no confundir ambos historiales.

Antes de publicar: instalar y pasar pruebas, `git fetch origin`, inspeccionar
ramas/historial remotos y conservar trabajo ajeno. Si origin ya tiene main, crear
la rama desde ese historial y revisar el diff de estos archivos antes de commit.
No usar force ni reemplazar main remoto con un historial no relacionado.

El remoto **ya tiene main**: no hacer bootstrap ni reemplazarlo. El local sigue
sin commits y contiene estos archivos sin seguimiento. Para enlazar su historial
sin sobrescribir los archivos, después de verificar `git status` e identidad real:

```powershell
git fetch origin main
git switch --orphan base/plaza-reserva
git reset --mixed origin/base/plaza-reserva
```

`reset --mixed` solo prepara índice e historial de la rama; conserva los archivos
de trabajo. Este procedimiento es para el estado local sin commits verificado aquí;
si ya hay commits/cambios nuevos, revisar antes de aplicarlo. No inventar nombre/email.

Con base main existente y copia preparada:

```powershell
# Si ya hiciste el enlace anterior, estás en base/plaza-reserva.
git add README.md AGENTS.md .gitignore .env.example pyproject.toml alembic.ini src tests migrations specs docs scripts .github
git diff --cached --stat
git commit -m "BASE-01 BASE-02: preparar especificaciones y esqueleto compartido"
git push -u origin base/plaza-reserva
gh pr create --repo Stelar0720/proyecto_2_topicos_II --base main --head base/plaza-reserva --title "BASE-01/02: especificaciones y base de Plaza Reserva" --body-file docs/initial-pr.md
```

El cuerpo `initial-pr.md` debe actualizarse con resultados reales antes de publicar.
No fusionar ni cambiar protección de ramas. Registrar las URLs reales en README/
github-state y dejar a compañeros esperando la integración real de BASE-02.

Referencia de flags comprobados con gh 2.96.0 y [manual oficial](https://cli.github.com/manual/gh_project).
