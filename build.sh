#!/bin/bash

# Color codes
RED="\033[31m"; GREEN="\033[32m"; YELLOW="\033[33m"; BLUE="\033[34m"; MAGENTA="\033[35m"; CYAN="\033[36m"; BOLD="\033[1m"; RESET="\033[0m"

# Pretty logger (single line). Use emojis + colors.
log() {
    printf "\n%b\n" "$1"
}

# Section header
section() {
    printf "\n${BOLD}${MAGENTA}== ${1} ==${RESET}\n"
}

# Error handler
error_exit() {
    log "${RED}error:${RESET} $1"
    exit 1
}

# Always run from the repository root so relative paths resolve.
cd "$(dirname "$0")" || error_exit "Cannot cd to script directory"

# The pandoc filters need Python >= 3.10 (they use `match`) and the packages
# in requirements.txt. Run pandoc through uv so its filters get both.
command -v uv >/dev/null 2>&1 \
    || error_exit "uv is required: https://docs.astral.sh/uv/getting-started/installation/"
command -v pandoc >/dev/null 2>&1 \
    || error_exit "pandoc is required: https://pandoc.org/installing.html"
command -v xelatex >/dev/null 2>&1 \
    || error_exit "xelatex is required to build cv.pdf (install MacTeX or BasicTeX)"

# Check that every LaTeX package used by the CV template is installed.
# (BasicTeX ships without many of them.)
MISSING_STY=""
for pkg in $(grep -ohE '\\usepackage(\[[^]]*\])?\{[^}]*\}' templates/cv.latex \
                | sed -E 's/.*\{(.*)\}/\1/' | tr ',' ' '); do
    kpsewhich "$pkg.sty" >/dev/null || MISSING_STY="$MISSING_STY $pkg"
done
[ -z "$MISSING_STY" ] \
    || error_exit "missing LaTeX packages:$MISSING_STY\n       install with: sudo tlmgr install$MISSING_STY"

pandoc() {
    uv run --quiet --no-project --python ">=3.10" --with-requirements requirements.txt \
        pandoc "$@"
}

section "Index"
log "${YELLOW}build:${RESET} index → docs/index.html"
# Build main index page
pandoc index.md -o docs/index.html \
    --standalone \
    --template="templates/index.html" \
    --css "style/base.css" \
    --css "style/index.css" \
    --include-in-header="templates/scroller.html" \
    --include-in-header="templates/selected.html" \
    --filter filters/index.py || error_exit "Failed to build index.html"

# Build blog posts
section "Posts"
log "${YELLOW}clean:${RESET} docs/posts/*.html"
# delete all the .html files in docs/posts
rm -f docs/posts/*.html

if [ $? -ne 0 ]; then
    error_exit "Failed to clean docs/posts/*.html"
fi

POST_COUNT=0
for file in posts/*.md; do
    filename=$(basename "$file" .md)
    # Posts with a 'url' front-matter field link directly to an external
    # page and have no body, so there's nothing to render locally.
    if grep -q '^url:' "$file"; then
        continue
    fi
    POST_COUNT=$((POST_COUNT + 1))
    pandoc "$file" -o "docs/posts/$filename.html" \
        --standalone \
        --template="templates/post.html" \
        --css "../style/base.css" \
        --css "../style/post.css" \
        --include-in-header="templates/scroller.html" \
        || log "${RED}error:${RESET} Failed to build $filename.html"
done
log "${YELLOW}build:${RESET} docs/posts/*.md → docs/posts/*.html (${BOLD}$POST_COUNT${RESET} posts)"

# Build CV
section "CV"
log "${YELLOW}build:${RESET} cv.md → docs/cv.html"
pandoc cv.md -o docs/cv.html \
    --standalone \
    --template="templates/cv.html" \
    --css "style/main.css" \
    --css "style/cv.css" \
    --include-in-header="templates/scroller.html" \
    --filter filters/cv.py || error_exit "Failed to build cv.html"

# Build CV PDF
log "${YELLOW}build:${RESET} cv.md → docs/cv.pdf"
pandoc cv.md -o docs/cv.pdf \
    --template="templates/cv.latex" \
    --pdf-engine=xelatex \
    -V table-use-row-colors=false \
    --filter filters/cv.py || error_exit "Failed to build cv.pdf"

log "${BOLD}${GREEN}✓ complete${RESET}"
log "outputs: docs/index.html, docs/cv.html, docs/cv.pdf, docs/posts/*.html\n"
