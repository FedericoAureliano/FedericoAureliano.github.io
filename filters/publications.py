#!/usr/bin/env python3

"""
Add selected publications to the end of the document.
"""

import panflute as pf
import os
import pathlib
import markdown


def clean(text: str) -> str:
    """
    Clean the text by removing extra spaces and newlines.
    """
    return ' '.join(text.split()).strip()

def prepare(doc):
    papers_dir = doc.get_metadata('papers')

    doc.papers = {}

    if not papers_dir:
        pf.debug("No 'papers' metadata found, skipping papers filter.")
        return

    pf.debug(f"Loading papers items from directory: {papers_dir}")
    papers_files = [f for f in os.listdir(papers_dir) if f.endswith('.md')]
    for papers_file in papers_files:
        paper_path = os.path.join(papers_dir, papers_file)
        data = pathlib.Path(paper_path).read_text(encoding='utf-8')
        md = markdown.Markdown(extensions=['meta'])
        md.convert(data)

        assert 'selected' in md.Meta, f"Missing 'selected' metadata in {papers_file}"
        if md.Meta['selected'][0].lower() != 'true':
            continue

        assert 'venue' in md.Meta, f"Missing 'venue' metadata in {papers_file}"
        venue = md.Meta['venue'][0]
        assert 'year' in md.Meta, f"Missing 'year' metadata in {papers_file}"
        year = md.Meta['year'][0]
        
        assert 'title' in md.Meta, f"Missing 'title' metadata in {papers_file}"
        title = md.Meta['title']
        if "|" in title[0]:
            title = clean(title[1])
        else:
            title = clean(title[0])

        assert 'authors' in md.Meta, f"Missing 'authors' metadata in {papers_file}"
        authors = md.Meta['authors']
        authors = [clean(a) for a in authors if a.strip()]
        
        assert 'category' in md.Meta, f"Missing 'category' metadata in {papers_file}"
        category = md.Meta['category'][0]

        link = papers_dir + "/" + os.path.splitext(papers_file)[0] + '.html' 

        paper_info = {
            'title': title,
            'authors': authors,
            'venue': venue,
            'year': year,
            'link': link,
        }

        doc.papers.setdefault(category, []).append(paper_info)

    # Sort papers by category and then by year
    for category, papers in doc.papers.items():
        papers.sort(key=lambda x: (x['year'], x['title']))

def action(elem, doc):
    match elem:
        case pf.Header(identifier='selected-publications', level=1):
            div = pf.Div(elem, classes=['publications'])
            for category, papers in doc.papers.items():
                div.content.append(pf.Header(pf.Str(category), level=2))
                # make a table with two columns: venue and title
                rows = []
                for paper in papers:
                    venue = pf.Str(f"{paper['venue']} '{paper['year'][-2:]}")
                    venue = pf.Plain(pf.Link(venue, url=paper['link']))
                    title = pf.Plain(pf.Str(paper['title']))
                    rows.append(pf.TableRow(
                        pf.TableCell(venue),
                        pf.TableCell(title)
                    ))
                div.content.append(pf.Table(pf.TableBody(*rows)))

            return div

def finalize(doc):
    pass

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()