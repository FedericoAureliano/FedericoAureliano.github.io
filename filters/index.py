#!/usr/bin/env python3

"""
Combined filter for index page generation.
Combines functionality from news.py, publications.py, and sections.py filters.
"""

from typing import List, Tuple
import panflute as pf
import os
import pathlib
import markdown
import datetime
from pybtex.database import parse_file, Person

# ============================================================================
# News filter functions
# ============================================================================

def load_news_items(doc):
    """Load news items from the news directory (from news.py)"""
    news_items: List[Tuple[datetime.date, str, str]] = []

    news_dir = doc.get_metadata('news')

    if not news_dir:
        pf.debug("  no news")
        return []

    pf.debug(f"  news dir → {news_dir}")
    news_files = [f for f in os.listdir(news_dir) if f.endswith('.md')]
    # files count redundant with items; omit
    for news_file in news_files:
        news_path = os.path.join(news_dir, news_file)

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
    pf.debug(f"  posts → {len(news_items)}")
    
    return [(pf.Link(pf.Str(date.strftime('%m/%Y')), url=f"{news_dir}/{name}.html"), pf.Str(title)) for (date, name, title) in news_items]

# ============================================================================
# Publications filter functions
# ============================================================================

def clean_venue(text: str) -> str:
    """
    "Annual Conference on Neural Information Processing Systems (NeurIPS)" -> "NeurIPS"
    "International Conference on Computer-Aided Verification (CAV)" -> "CAV" 
    """
    return text.split("(")[-1].strip(")")

def load_publications(doc):
    """Load publications from bibtex file (from publications.py)"""
    bib_file = doc.get_metadata('papers')
    if not bib_file:
        pf.debug("  no papers")
    pubs_bibtex = parse_file(bib_file).entries.values() if (bib_file and os.path.exists(bib_file)) else []
    pf.debug(f"  bib → {bib_file}")

    papers = []

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

        paper_info = {
            'title': title,
            'venue': venue,
            'year': year,
            'selected': selected,
            'link': link,
        }

        papers.append(paper_info)

    papers.sort(key=lambda x: (x['year'], x['venue']), reverse=True)
    pf.debug(f"  papers → {len(papers)}")
    return papers

# ============================================================================
# Sections filter functions
# ============================================================================

def emoji(char):
    """Create an emoji span (from sections.py)"""
    return pf.Span(pf.Str(char), classes=['emoji'])

def load_profile_info(doc):
    """Load profile information (from sections.py)"""
    headshot = doc.get_metadata('headshot')
    headshot_div = pf.Div(pf.Plain(pf.Image(url=headshot, title="Headshot")), classes=['headshot'])
    
    email = doc.get_metadata('email')
    email_span = pf.Span(emoji("✉"), pf.Space(), pf.Code(email), classes=['email'])
    
    return headshot_div, email_span

# ============================================================================
# Combined prepare/action/finalize functions
# ============================================================================

def prepare(doc):
    """Prepare function that combines all three filters"""
    # Load news items
    doc.news_items = load_news_items(doc)
    
    # Load publications
    doc.papers = load_publications(doc)
    
    # Load profile info
    doc.headshot, doc.email = load_profile_info(doc)

def action(elem, doc):
    """Action function that combines news and publications actions"""
    match elem:
        # Handle news/posts headers (from news.py)
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
        
        # Handle publications header (from publications.py)
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
    """Finalize function from sections.py - creates sections and adds footer"""
    header_indexes = []
    # Find all header elements and their indexes
    for idx, item in enumerate(doc.content):
        match item:
            case pf.Header(identifier=name, level=1):
                header_indexes.append((idx, name))
            case pf.Div():
                header_indexes.append((idx, None))
    header_indexes.append((len(doc.content), None))

    offset = 0
    # Adjust indexes to account for the offset caused by the replacement of sections
    for i in range(len(header_indexes) - 1):
        start_index = header_indexes[i][0] + offset
        end_index = header_indexes[i + 1][0] + offset
        name = header_indexes[i][1]

        if name is None:
            # If the header name is None, skip this section
            continue
        elif name == 'profile':
            header = doc.content[start_index]
            # Create a section with the content between the headers
            section_content = doc.content[start_index+1:end_index]
            
            # Only put the first paragraph in the blurb class
            if section_content and isinstance(section_content[0], pf.Para):
                first_para = section_content[0]
                remaining_content = section_content[1:]
                # Create profile grid with headshot and first paragraph side by side
                profile_grid = pf.Div(doc.headshot, pf.Div(first_para, classes=['blurb']), classes=['profile'])
                # Create section with profile grid, then remaining content full-width below
                section_div = pf.Div(header, profile_grid, *remaining_content, classes=[name])
            else:
                # Fallback to original behavior if no paragraphs
                section_div = pf.Div(header, doc.headshot, pf.Div(*section_content, classes=['blurb']), classes=[name])
        else:
            # Create a section with the content between the headers
            section_content = doc.content[start_index:end_index]
            section_div = pf.Div(*section_content, classes=[name])

        # Replace the content between the headers with the section div
        doc.content[start_index:end_index] = [section_div]

        # Adjust the offset for the next section
        offset += (start_index - end_index) + 1
    pf.debug("  sections → rebuilt")

    # Add a footer with the current date
    last_update = pf.Span(pf.Str(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d')}"), classes=['last-update'])
    footer = pf.Div(pf.Plain(doc.email), pf.Plain(last_update), classes=['footer'])
    doc.content.append(footer)

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()
