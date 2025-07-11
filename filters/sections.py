#!/usr/bin/env python3

"""
Clump all the headers into sections and add the headshot to the profile section.
"""

import panflute as pf

def prepare(doc):
    doc.headshot = doc.get_metadata('headshot')
    doc.headshot = pf.Para(pf.Image(url=doc.headshot, title="Headshot", classes=['headshot']))

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
            # create a table with the headshot on the left and the section content on the right
            row = pf.TableRow(
                pf.TableCell(doc.headshot),
                pf.TableCell(pf.Div(*section_content))
            )
            table = pf.Table(pf.TableBody(row))
            section_div = pf.Div(header, table, classes=[name])
        else:
            # Create a section with the content between the headers
            section_content = doc.content[start_index:end_index]
            section_div = pf.Div(*section_content, classes=[name])

        # Replace the content between the headers with the section div
        doc.content[start_index:end_index] = [section_div]

        # Adjust the offset for the next section
        offset += (start_index - end_index) + 1


def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()