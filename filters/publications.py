#!/usr/bin/env python3

"""
Add selected publications to the end of the document.
"""

import panflute as pf
from pybtex.database import parse_file

def prepare(doc):
    bib_data = parse_file('data/publications.bib')
    doc.papers = {}
    
    for entry in bib_data.entries.values():
        fields = entry.fields
        if fields['build_selected'] == 'true':
            category = fields.get('build_keywords', 'Uncategorized')
            if category not in doc.papers:
                doc.papers[category] = []

            doc.papers[category].append({
                'title': fields.get('title', ''),
                'authors': ', '.join(str(a) for a in entry.persons.get('author', [])),
                'year': fields.get('year', ''),
                "venue": fields.get('build_short', ''),
            })

def action(elem, doc):
    match elem:
        case pf.Header(identifier='selected-publications', level=1):
            div = pf.Div(elem, classes=['publications'])
            for category, papers in doc.papers.items():
                div.content.append(pf.Header(pf.Str(category), level=2))
                div.content.append(pf.BulletList(
                    *[pf.ListItem(pf.Plain(pf.Str(paper['title'])))
                      for paper in papers]
                ))
            return div

def finalize(doc):
    pass

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()