#!/usr/bin/env python3

"""
Clump profile into a div
"""

import panflute as pf

def prepare(doc):
    doc.profile_header = None

def action(elem, doc):
    match elem:
        case pf.Header(identifier='profile', level=1):
            doc.profile_header = elem

def finalize(doc):
    if doc.profile_header is None:
        pf.debug("No profile header found, skipping clumping.")
        return
    
    # find the index of the profile header in doc.content
    profile_index = next((i for i, e in enumerate(doc.content) if e == doc.profile_header), len(doc.content))
    
    # find the next header after the profile header
    next_header_index = next((i for i, e in enumerate(doc.content[profile_index + 1:], start=profile_index + 1) if isinstance(e, pf.Header)), len(doc.content))

    # create a div with the profile header and all content until the next header
    profile_content = doc.content[profile_index:next_header_index]
    profile_div = pf.Div(*profile_content, classes=['profile'])

    # delete all the doc.content between profile_index and next_header_index
    del doc.content[profile_index:next_header_index]

    # insert the profile div at the profile_index
    doc.content.insert(profile_index, profile_div)

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()