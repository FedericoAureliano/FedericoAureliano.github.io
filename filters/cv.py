#!/usr/bin/env python3

"""
CV filter for generating curriculum vitae with detailed publication information.
Includes author lists in publications, unlike the index.py filter.
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

def format_author_list(authors) -> str:
    """
    Format a list of authors from pybtex Person objects into a string.
    Example: "Smith, John and Doe, Jane and Johnson, Bob"
    """
    author_names = []
    for author in authors:
        # Get the full name in "First Last" format
        first = " ".join(author.first_names)
        last = " ".join(author.last_names)
        if first:
            author_names.append(f"{first} {last}")
        else:
            author_names.append(last)
    
    if len(author_names) == 0:
        return ""
    elif len(author_names) == 1:
        return author_names[0]
    elif len(author_names) == 2:
        return f"{author_names[0]} and {author_names[1]}"
    else:
        # Join all but the last with ", " and add ", and " before the last
        return ", ".join(author_names[:-1]) + f", and {author_names[-1]}"

def prepare(doc):
    """Load publications from bibtex file"""
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
        
        # Extract and format authors
        authors = pub.persons.get('author', [])
        author_list = format_author_list(authors)

        paper_info = {
            'title': title,
            'venue': venue,
            'year': year,
            'selected': selected,
            'link': link,
            'authors': author_list,
        }

        doc.papers.append(paper_info)

    doc.papers.sort(key=lambda x: (x['year'], x['venue']), reverse=True)

def action(elem, doc):
    """Handle publications header and mark it for table insertion"""
    match elem:
        case pf.Header(identifier=name) if "publications" in name:
            # Mark this header so we can find the section later
            doc.publications_header = elem
            # Store the parent for later reference
            if not hasattr(doc, 'current_section'):
                doc.current_section = None

def finalize(doc):
    """Add the publications table at the end of the publications section"""
    if not hasattr(doc, 'publications_header') or doc.publications_header is None:
        return
    
    # Build the publications table
    rows = []
    for paper in doc.papers:
        # Create venue cell with year (no link)
        venue = pf.Str(f"{paper['venue']} '{paper['year'][-2:]}")
        venue = pf.Plain(venue)
        
        # Create title and authors cell with link on title
        title_str = pf.Str(paper['title'])
        if paper['link']:
            title_with_link = pf.Link(title_str, url=paper['link'])
        else:
            title_with_link = title_str
        
        title_content = [title_with_link]
        if paper['authors']:
            # Add a line break and authors
            title_content.extend([
                pf.LineBreak(),
                pf.Emph(pf.Str(paper['authors']))
            ])
        title_cell = pf.Plain(*title_content)
        
        rows.append(pf.TableRow(
            pf.TableCell(venue),
            pf.TableCell(title_cell)
        ))
    
    table = pf.Table(pf.TableBody(*rows))
    
    # Walk the document to find the publications section and append table at the end
    def add_table_to_section(elem, doc):
        if isinstance(elem, pf.Doc):
            # Find the publications header index
            pub_index = None
            for i, child in enumerate(elem.content):
                if child is doc.publications_header:
                    pub_index = i
                    break
            
            if pub_index is not None:
                # Find the next header (any level) or end of document
                next_header_index = None
                for i in range(pub_index + 1, len(elem.content)):
                    if isinstance(elem.content[i], pf.Header):
                        next_header_index = i
                        break
                
                # Insert the table before the next header or at the end
                if next_header_index is not None:
                    elem.content.insert(next_header_index, table)
                else:
                    elem.content.append(table)
    
    doc.walk(add_table_to_section)

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()
