#!/usr/bin/env python3

"""
CV filter for generating curriculum vitae with detailed publication information.
Includes author lists in publications, unlike the index.py filter.
Also standardizes table column widths for consistent formatting.
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

def format_author_list(authors, students=None) -> list:
    """
    Format a list of authors from pybtex Person objects into a list of panflute elements.
    Student names will be made bold.
    
    Args:
        authors: List of pybtex Person objects
        students: Set of student names to make bold (optional)
    
    Returns:
        List of panflute elements (Str, Strong, etc.) for the author list
    """
    if students is None:
        students = set()
    
    author_elements = []
    author_names = []
    
    for author in authors:
        # Get the full name in "First Last" format
        first = " ".join(author.first_names)
        last = " ".join(author.last_names)
        if first:
            full_name = f"{first} {last}"
        else:
            full_name = last
        author_names.append(full_name)
    
    if len(author_names) == 0:
        return []
    
    for i, name in enumerate(author_names):
        # Check if this author is a student
        if name in students:
            # Make the name bold
            author_elements.append(pf.Strong(pf.Str(name)))
        else:
            author_elements.append(pf.Str(name))
        
        # Add appropriate separator
        if i < len(author_names) - 2:
            # Not the last or second-to-last, add ", "
            author_elements.append(pf.Str(", "))
        elif i == len(author_names) - 2:
            # Second-to-last, add ", and " or " and " depending on count
            if len(author_names) > 2:
                author_elements.append(pf.Str(", and "))
            else:
                author_elements.append(pf.Str(" and "))
    
    return author_elements

def prepare(doc):
    """Load publications from bibtex file"""
    bib_file = doc.get_metadata('papers')
    if not bib_file:
        pf.debug("  no papers")
    pubs_bibtex = parse_file(bib_file).entries.values() if (bib_file and os.path.exists(bib_file)) else []
    pf.debug(f"  bib → {bib_file}")

    # Load student names from metadata
    students_list = doc.get_metadata('students', [])
    doc.students = set(students_list) if students_list else set()

    doc.papers = []
    # Track whether we've seen the first top-level section
    doc.first_section_seen = False

    for pub in pubs_bibtex:
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
        author_elements = format_author_list(authors, doc.students)

        paper_info = {
            'title': title,
            'venue': venue,
            'year': year,
            'selected': selected,
            'link': link,
            'author_elements': author_elements,
        }

        doc.papers.append(paper_info)

    doc.papers.sort(key=lambda x: (x['year'], x['venue']), reverse=True)
    pf.debug(f"  papers → {len(doc.papers)}")

def action(elem, doc):
    """Handle publications header and standardize table column widths"""
    match elem:
        case pf.Header(identifier=name) if "publications" in name:
            # Mark this header so we can find the section later
            doc.publications_header = elem
            # Store the parent for later reference
            if not hasattr(doc, 'current_section'):
                doc.current_section = None
            pf.debug(f"  header → {name}")
        case pf.Table():
            # Standardize column widths for 2-column tables
            if len(elem.colspec) == 2:
                # Set first column to fixed width (0.15 of line width ≈ 1 inch), right-aligned
                # Set second column to remaining width (0.85), left-aligned
                elem.colspec = [
                    ('AlignRight', 0.15),
                    ('AlignLeft', 0.85)
                ]
            
            # Collapse multirow cells and remove empty continuation rows
            # When a cell has rowspan > 1, Pandoc creates continuation rows
            # We merge the content and remove those empty continuation rows
            for body in elem.content:
                if isinstance(body, pf.TableBody):
                    rows_to_keep = []
                    skip_next = 0
                    
                    for i, row in enumerate(body.content):
                        if skip_next > 0:
                            skip_next -= 1
                            continue
                            
                        # Check if any cell in this row has rowspan > 1
                        max_rowspan = max(cell.rowspan for cell in row.content)
                        
                        if max_rowspan > 1:
                            # Merge content from continuation rows into this row
                            for cell_idx, cell in enumerate(row.content):
                                if cell.rowspan > 1:
                                    # Collect content from continuation rows
                                    for row_offset in range(1, cell.rowspan):
                                        if i + row_offset < len(body.content):
                                            continuation_row = body.content[i + row_offset]
                                            # Check if continuation row has enough cells
                                            if cell_idx < len(continuation_row.content):
                                                continuation_cell = continuation_row.content[cell_idx]
                                                # Append continuation cell content to current cell
                                                cell.content.extend(continuation_cell.content)
                                    # Set rowspan to 1 now that content is merged
                                    cell.rowspan = 1
                            
                            # Mark continuation rows to skip
                            skip_next = max_rowspan - 1
                        
                        rows_to_keep.append(row)
                    
                    body.content = rows_to_keep
            
            return elem

def finalize(doc):
    """Add the publications table at the end of the publications section"""
    if not hasattr(doc, 'publications_header') or doc.publications_header is None:
        pf.debug("  finalize -> no publications header; skipping table insertion")
        return
    
    # Build the publications table
    rows = []
    for paper in doc.papers:
        # Create venue cell with year (no link)
        venue = pf.Str(f"{paper['venue']} '{paper['year'][-2:]}")
        venue = pf.Plain(venue)

        # Create title and authors cell with link on title, authors on same line
        title_str = pf.Str(paper['title'])
        if paper['link']:
            title_with_link = pf.Link(title_str, url=paper['link'])
        else:
            title_with_link = title_str

        title_content = [title_with_link]
        if paper['author_elements']:
            # Add separator and authors on same line, with italics
            title_content.append(pf.Str(" · "))
            title_content.append(pf.Emph(*paper['author_elements']))
        title_cell = pf.Plain(*title_content)

        rows.append(pf.TableRow(
            pf.TableCell(venue),
            pf.TableCell(title_cell)
        ))
    
    # Build table and enforce same formatting as other tables
    table = pf.Table(pf.TableBody(*rows))
    # Right-align first column, left-align second; set widths to 0.15/0.85
    table.colspec = [('AlignRight', 0.15), ('AlignLeft', 0.85)]
    
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
                
                # Insert vertical space and the table before the next header or at the end
                vspace = pf.RawBlock('\\vspace{1em}', format='latex')
                if next_header_index is not None:
                    elem.content.insert(next_header_index, vspace)
                    elem.content.insert(next_header_index + 1, table)
                    # insertion index detail redundant; omit
                else:
                    elem.content.append(vspace)
                    elem.content.append(table)
                    pf.debug("  insert → end")
    
    doc.walk(add_table_to_section)
    pf.debug("  insert → done")

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()
