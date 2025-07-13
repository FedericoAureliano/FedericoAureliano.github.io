#!/usr/bin/env python3

"""
Add most recent news items
"""

from typing import List, Tuple
import panflute as pf
import os
import pathlib
import markdown
import datetime

def prepare(doc):
    news_items: List[Tuple[datetime.date,str,str]] = []

    news_dir = doc.get_metadata('news')

    if not news_dir:
        pf.debug("No 'news' metadata found, skipping news filter.")
        return

    pf.debug(f"Loading news items from directory: {news_dir}")
    news_files = [f for f in os.listdir(news_dir) if f.endswith('.md')]
    for news_file in news_files:
        news_path = os.path.join(news_dir, news_file)
        pf.debug(f"\t- {news_path}")

        data = pathlib.Path(news_path).read_text(encoding='utf-8')
        md = markdown.Markdown(extensions=['meta'])
        md.convert(data)

        assert 'date' in md.Meta, f"Missing 'date' metadata in {news_file}"
        assert 'title' in md.Meta, f"Missing 'title' metadata in {news_file}"

        date = datetime.datetime.strptime(md.Meta['date'][0], '%m/%Y').date()
        title = md.Meta['title'][0]
        name = os.path.splitext(news_file)[0]  # Remove the .md extension
        
        news_items.append((date, name, title))

    # Sort by date, most recent first
    news_items.sort(key=lambda x: x[0], reverse=True)  
    
    doc.news_items = [(pf.Link(pf.Str(date.strftime('%m/%Y')), url=f"{news_dir}/{name}.html"), pf.Str(title)) for (date, name, title) in news_items]

def action(elem, doc):
    match elem:
        case pf.Header(identifier=name, level=1) if "news" in name or "posts" in name:
            rows = []
            for (i, (date, title)) in enumerate(doc.news_items):
                classes = ['not-recent'] if i >= 5 else []
                rows.append(pf.TableRow(pf.TableCell(pf.Plain(date)), pf.TableCell(pf.Plain(title)), classes=classes))
            toggle_link = pf.Link(
                pf.Str("(show all)"),
                url=f"#{name}",
                classes=["toggle-recent"]
            )
            elem.content += [pf.Space(), toggle_link]
            return pf.Div(elem, pf.Table(pf.TableBody(*rows)), classes=['posts'])

def finalize(doc):
    pass

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()