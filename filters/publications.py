#!/usr/bin/env python3

"""
Add selected publications to the end of the document.
"""

import panflute as pf
import os
from pybtex.database import parse_file, Person

def clean_venue(text: str) -> str:
    """
    "Annual Conference on Neural Information Processing Systems (NeurIPS)" -> "NeurIPS"
    "International Conference on Computer-Aided Verification (CAV)" -> "CAV" 
    """
    return text.split("(")[-1].strip(")")

def prepare(doc):
    bib_file = doc.get_metadata('papers')
    pubs_bibtex = parse_file(bib_file).entries.values() if os.path.exists(bib_file) else []

    doc.papers = []

    for pub in pubs_bibtex:
        pf.debug(f"\t- {pub.key}")

        selected = pub.fields['selected'].lower() == 'true' if 'selected' in pub.fields else False
        link = pub.fields["url"] if 'url' in pub.fields else ""

        if "booktitle" in pub.fields:
            venue = clean_venue(pub.fields['booktitle'])
        elif "journal" in pub.fields:
            venue = clean_venue(pub.fields['journal'])
        else:
            assert False, f"Missing 'booktitle' or 'journal' metadata in {pub.key}"

        assert 'year' in pub.fields, f"Missing 'year' metadata in {pub.key}"
        year = pub.fields['year']
        assert 'title' in pub.fields, f"Missing 'title' metadata in {pub.key}"
        title = pub.fields['title']

        paper_info = {
            'title': title,
            'venue': venue,
            'year': year,
            'selected': selected,
            'link': link,
        }

        doc.papers.append(paper_info)

    doc.papers.sort(key=lambda x: (x['year'], x['venue']), reverse=True)

def action(elem, doc):
    match elem:
        case pf.Header(identifier=name, level=1) if "publications" in name:
            div = pf.Div(elem, classes=['publications'])
            toggle_link = pf.Link(
                pf.Str("(show all)"),
                url=f"#{name}",
                classes=["toggle-publications"]
            )
            elem.content += [pf.Space(), toggle_link]
            rows = []
            for paper in doc.papers:
                venue = pf.Str(f"{paper['venue']} '{paper['year'][-2:]}")
                venue = pf.Plain(pf.Link(venue, url=paper['link']))
                title = pf.Plain(pf.Str(paper['title']))
                rows.append(pf.TableRow(
                    pf.TableCell(venue),
                    pf.TableCell(title),
                    classes=["selected" if paper['selected'] else "not-selected"]
                ))
            div.content.append(pf.Table(pf.TableBody(*rows)))
            return div

def finalize(doc):
    pass

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()