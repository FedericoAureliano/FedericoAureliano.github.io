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

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    log "${CYAN}venv:${RESET} activating .venv"
    source .venv/bin/activate
fi

# Error handler
error_exit() {
    log "${RED}error:${RESET} $1"
    exit 1
}

section "Index"
log "${YELLOW}build:${RESET} index → docs/index.html"
# Build main index page
pandoc index.md -o docs/index.html \
    --standalone \
    --template="templates/index.html" \
    --css "style/main.css" \
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
    POST_COUNT=$((POST_COUNT + 1))
    pandoc "$file" -o "docs/posts/$filename.html" \
        --standalone \
        --template="templates/post.html" \
        --css "../style/main.css" \
        --css "../style/post.css" \
        --include-in-header="templates/scroller.html" || log "${RED}error:${RESET} Failed to build $filename.html"
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
