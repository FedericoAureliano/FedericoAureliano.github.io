pandoc README.md -o docs/index.html \
    --standalone \
    --template="templates/index.html" \
    --css "style/main.css" \
    --css "style/index.css" \
    --include-in-header="templates/scroller.html" \
    --filter filters/news.py \
    --filter filters/publications.py \
    --filter filters/sections.py 
    # sections filter has to be last

# delete all the .html files in docs/posts
rm -f docs/posts/*.html

for file in posts/*.md; do
    filename=$(basename "$file" .md)
    pandoc "$file" -o "docs/posts/$filename.html" \
        --standalone \
        --template="templates/post.html" \
        --css "../style/main.css" \
        --css "../style/post.css" \
        --css "../style/post.css" \
        --include-in-header="templates/scroller.html"
done
