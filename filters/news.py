#!/usr/bin/env python3

"""
Add most recent news items
"""

from typing import List, Tuple
import panflute as pf
import os
import pathlib
import markdown

def prepare(doc):
    news_items: List[Tuple[str,str]] = []

    news_dir = doc.get_metadata('news')

    if not news_dir:
        pf.debug("No 'news' metadata found, skipping news filter.")
        return

    pf.debug(f"Loading news items from directory: {news_dir}")
    news_files = [f for f in os.listdir(news_dir) if f.endswith('.md')]
    for news_file in news_files:
        news_path = os.path.join(news_dir, news_file)
        pf.debug(f"Loading news file: {news_path}")
        data = pathlib.Path(news_path).read_text(encoding='utf-8')
        md = markdown.Markdown(extensions=['meta'])
        md.convert(data)
        news_items.append((md.Meta['date'][0], md.Meta['title'][0]))
    
    news_items.sort(key=lambda x: x[0], reverse=True)  # Sort by date, most recent first
    doc.news_items = news_items

def action(elem, doc):
    match elem:
        case pf.Header(identifier='news', level=1):
            bullets = pf.BulletList()
            for (date, title) in doc.news_items:
                bullets.content.append(pf.ListItem(pf.Plain(
                    pf.Str(f"{date}: "), pf.Str(title)
                )))
            return pf.Div(elem, bullets, classes=['posts'])

def finalize(doc):
    pass

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()