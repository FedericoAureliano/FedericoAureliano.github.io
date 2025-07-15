#!/usr/bin/env python3

"""
Clump all the headers into sections, add the headshot to the profile section, and add a footer with the current date.
"""

import panflute as pf
import datetime

def emoji(char):
    return pf.Span(pf.Str(char), classes=['emoji'])

def prepare(doc):
    doc.headshot = doc.get_metadata('headshot')
    doc.headshot = pf.Div(pf.Plain(pf.Image(url=doc.headshot, title="Headshot")), classes=['headshot'])
    doc.email = doc.get_metadata('email')
    doc.email = pf.Span(emoji("✉"), pf.Space(), pf.Code(doc.email), classes=['email'])

def action(elem, doc):
    pass

def finalize(doc):
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
            section_div = pf.Div(header, doc.headshot, pf.Div(*section_content, classes=['blurb']), classes=[name])
        else:
            # Create a section with the content between the headers
            section_content = doc.content[start_index:end_index]
            section_div = pf.Div(*section_content, classes=[name])

        # Replace the content between the headers with the section div
        doc.content[start_index:end_index] = [section_div]

        # Adjust the offset for the next section
        offset += (start_index - end_index) + 1

    # Add a footer with the current date
    last_update = pf.Span(pf.Str(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d')}"), classes=['last-update'])
    footer = pf.Div(pf.Plain(doc.email), pf.Plain(last_update), classes=['footer'])
    doc.content.append(footer)

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()