#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Build main index page
pandoc index.md -o docs/index.html \
    --standalone \
    --template="templates/index.html" \
    --css "style/main.css" \
    --css "style/index.css" \
    --include-in-header="templates/scroller.html" \
    --include-in-header="templates/selected.html" \
    --filter filters/index.py

# Build blog posts
# delete all the .html files in docs/posts
rm -f docs/posts/*.html

for file in posts/*.md; do
    filename=$(basename "$file" .md)
    pandoc "$file" -o "docs/posts/$filename.html" \
        --standalone \
        --template="templates/post.html" \
        --css "../style/main.css" \
        --css "../style/post.css" \
        --include-in-header="templates/scroller.html"
done

# Build CV
echo "Building CV..."
pandoc cv.md -o docs/cv.html \
    --standalone \
    --template="templates/cv.html" \
    --css "style/main.css" \
    --css "style/cv.css" \
    --include-in-header="templates/scroller.html" \
    --filter filters/cv.py 

echo "✓ Build complete!"
