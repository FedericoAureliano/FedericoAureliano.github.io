#!/usr/bin/env python3

"""
CV filter for generating curriculum vitae with detailed publication information.
Includes author lists in publications, unlike the index.py filter.
Also standardizes table column widths for consistent formatting.
"""

import panflute as pf
import os
import pathlib
import markdown
from pybtex.database import parse_file, Person

def clean_venue(text: str) -> str:
    """
    "Annual Conference on Neural Information Processing Systems (NeurIPS)" -> "NeurIPS"
    "International Conference on Computer-Aided Verification (CAV)" -> "CAV" 
    """
    return text.split("(")[-1].strip(")")

def extract_venue(pub) -> str:
    """Pick a display venue for a BibTeX entry."""
    if "venue" in pub.fields:
        return clean_venue(pub.fields["venue"])
    if "booktitle" in pub.fields:
        return clean_venue(pub.fields["booktitle"])
    if "journal" in pub.fields:
        return clean_venue(pub.fields["journal"])
    assert False, f"Missing venue metadata in {pub.key}"

def extract_markdown_body(data: str) -> str:
    """Extract the body from a markdown file with YAML-style frontmatter."""
    if data.startswith('---'):
        parts = data.split('---', 2)
        if len(parts) == 3:
            return parts[2].strip()
    return ""

def load_awards(doc):
    """Load awards from a directory of markdown files."""
    awards_dir = doc.get_metadata('awards')
    if not awards_dir:
        pf.debug("  no awards")
        return []

    award_files = [f for f in os.listdir(awards_dir) if f.endswith('.md')]

    awards = []
    for award_file in award_files:
        award_path = os.path.join(awards_dir, award_file)
        data = pathlib.Path(award_path).read_text(encoding='utf-8')
        md = markdown.Markdown(extensions=['meta'])
        md.convert(data)

        assert 'year' in md.Meta, f"Missing 'year' metadata in {award_file}"
        assert 'title' in md.Meta, f"Missing 'title' metadata in {award_file}"

        awards.append({
            'year': md.Meta['year'][0],
            'title': md.Meta['title'][0],
            'cv_title': md.Meta['cv_title'][0] if 'cv_title' in md.Meta else md.Meta['title'][0],
            'url': md.Meta['url'][0] if 'url' in md.Meta else "",
            'organization': md.Meta['organization'][0] if 'organization' in md.Meta else "",
            'selected': md.Meta['selected'][0].lower() == 'true' if 'selected' in md.Meta else False,
            'description': extract_markdown_body(data),
        })

    awards.sort(key=lambda x: (int(x['year']), x['title']), reverse=True)
    pf.debug(f"  awards → {len(awards)}")
    return awards

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
    doc.awards = load_awards(doc)
    # Track whether we've seen the first top-level section
    doc.first_section_seen = False

    for pub in pubs_bibtex:
        selected = pub.fields['selected'].lower() == 'true' if 'selected' in pub.fields else False
        link = pub.fields["url"] if 'url' in pub.fields else ""

        venue = extract_venue(pub)

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
        case pf.Header(identifier=name) if "awards" in name:
            doc.awards_header = elem
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

def insert_blocks_at_section_end(doc, header, blocks):
    """Insert blocks before the next top-level header after a given header."""
    if header is None:
        return

    start_index = None
    for i, child in enumerate(doc.content):
        if child is header:
            start_index = i + 1
            break

    if start_index is None:
        return

    insert_at = start_index
    while insert_at < len(doc.content) and not isinstance(doc.content[insert_at], pf.Header):
        insert_at += 1

    for offset, block in enumerate(blocks):
        doc.content.insert(insert_at + offset, block)

def build_publications_table(doc):
    """Build the publications table."""
    rows = []
    for paper in doc.papers:
        venue = pf.Plain(pf.Str(f"{paper['venue']} '{paper['year'][-2:]}"))

        title_str = pf.Str(paper['title'])
        title_with_link = pf.Link(title_str, url=paper['link']) if paper['link'] else title_str

        title_content = [title_with_link]
        if paper['author_elements']:
            title_content.append(pf.Str(" · "))
            title_content.append(pf.Emph(*paper['author_elements']))

        rows.append(pf.TableRow(
            pf.TableCell(venue),
            pf.TableCell(pf.Plain(*title_content))
        ))

    table = pf.Table(pf.TableBody(*rows))
    table.colspec = [('AlignRight', 0.15), ('AlignLeft', 0.85)]
    return table

def build_awards_table(doc):
    """Build the awards table."""
    rows = []
    for award in doc.awards:
        title = award['cv_title']
        title_inline = pf.Link(pf.Str(title), url=award['url']) if award['url'] else pf.Str(title)
        title_content = [title_inline]
        if award['organization']:
            title_content.append(pf.Str(f" ({award['organization']})"))
        if award['description']:
            title_content.extend([pf.LineBreak, pf.Emph(pf.Str(award['description']))])

        rows.append(pf.TableRow(
            pf.TableCell(pf.Plain(pf.Str(award['year']))),
            pf.TableCell(pf.Plain(*title_content))
        ))

    table = pf.Table(pf.TableBody(*rows))
    table.colspec = [('AlignRight', 0.15), ('AlignLeft', 0.85)]
    return table

def finalize(doc):
    """Add generated tables at the end of the publications and awards sections."""
    if getattr(doc, 'publications_header', None) is not None:
        insert_blocks_at_section_end(
            doc,
            doc.publications_header,
            [pf.RawBlock('\\vspace{1em}', format='latex'), build_publications_table(doc)]
        )
    else:
        pf.debug("  finalize -> no publications header; skipping table insertion")

    if getattr(doc, 'awards_header', None) is not None:
        insert_blocks_at_section_end(doc, doc.awards_header, [build_awards_table(doc)])

    pf.debug("  insert → done")

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()
