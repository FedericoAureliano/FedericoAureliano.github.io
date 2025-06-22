pandoc index.md -o index.html \
    --standalone \
    --template="templates/index.html" \
    --css "style/main.css" \
    --filter filters/profile.py \
    --filter filters/publications.py \
    --filter filters/news.py 