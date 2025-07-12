pandoc index.md -o docs/index.html \
    --standalone \
    --template="templates/index.html" \
    --css "style/main.css" \
    --css "style/index.css" \
    --filter filters/news.py \
    --filter filters/publications.py \
    --filter filters/sections.py 
    # sections filter has to be last

for file in posts/*.md; do
    filename=$(basename "$file" .md)
    pandoc "$file" -o "docs/posts/$filename.html" \
        --standalone \
        --template="templates/post.html" \
        --css "../style/main.css" \
        --css "../style/post.css"
done

for file in papers/*.md; do
    filename=$(basename "$file" .md)
    pandoc "$file" -o "docs/papers/$filename.html" \
        --standalone \
        --template="templates/paper.html" \
        --css "../style/main.css" \
        --css "../style/paper.css"
done