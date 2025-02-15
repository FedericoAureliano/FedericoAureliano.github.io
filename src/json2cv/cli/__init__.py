# SPDX-FileCopyrightText: 2024-present Federico Mora <fmorarocha@gmail.com>
#
# SPDX-License-Identifier: MIT
import click

from json2cv.__about__ import __version__

import os
import re
import json
import inspect

from typing import Dict, List
from datetime import datetime
from pybtex.database import parse_file, Person


# for printing with colours
class bcolors:
    SUCCESS = "\033[92m"
    OKCYAN = "\033[96m"
    OKBLUE = "\033[94m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="json2cv")
@click.option("-d", "--data", type=str, default="data", help="set the data directory (default: \"data\")")
@click.option("-o", "--output", type=str, default="docs", help="set the output directory (default: \"docs\")")
@click.option("-t", "--templates", type=str, default="templates", help="set the templates directory (default: \"templates\")")
@click.option("-v", "--verbosity", type=int, default=0, help="set the output verbosity (default: 0)")
@click.option("--cv", is_flag=True, help="generate a curriculum vitae in LaTeX too")
def json2cv(data, output, templates, verbosity, cv):

    def cleanup():
        for f in [
            f"{output}/index.html",
            f"{output}/news.html",
            f"{output}/pubs.html",
            f"{output}/main.css",
        ]:
            try:
                os.remove(f)
            except Exception as _:
                pass

    # Helper functions
    def status(msg: str, priority=1):
        if priority <= verbosity:
            if priority == 0:
                divider = "*" * len(msg)
                msg = f"{divider}\n{msg}\n{divider}"
                print(f"{bcolors.BOLD}{bcolors.OKBLUE}{msg}{bcolors.ENDC*2}")
            elif priority == 1:
                print(f"{bcolors.BOLD}{bcolors.OKCYAN}{msg}{bcolors.ENDC*2}")
            else:
                print(f"{bcolors.OKCYAN}{msg}{bcolors.ENDC}")


    def success(msg: str):
        msg = f"SUCCESS: {msg}"
        divider = "*" * len(msg)
        msg = f"{divider}\n{msg}\n{divider}"

        print(f"{bcolors.SUCCESS}{msg}{bcolors.ENDC}")


    def warning(msg: str):
        msg = f"WARNING: {msg}"
        divider = "*" * len(msg)
        msg = f"{divider}\n{msg}\n{divider}"

        print(f"{bcolors.WARNING}{msg}{bcolors.ENDC}")


    def error(msg: str):
        msg = f"ERROR: {msg}"
        divider = "*" * len(msg)
        msg = f"{divider}\n{msg}\n{divider}"

        print(f"{bcolors.ERROR}{msg}{bcolors.ENDC}")
        cleanup()
        exit(1)


    def warn_if_not(cond: bool, msg: str):
        if not cond:
            warning(msg)


    def fail_if_not(cond: bool, msg: str):
        if not cond:
            error(msg)


    def fill_if_missing(json: Dict[str, str], field: str, default=""):
        if not field in json:
            json[field] = default

        return json


    def is_federicos(name):
        return name == "Federico Mora Rocha"


    def check_tracker(tracker):
        status("- Sanity check on tracker script")

        fail_if_not(
            "federicoaureliano" not in tracker,
            f"Please use your own tracker in {data}/meta.json",
        )


    def check_cname():
        status("- Sanity check on CNAME")

        path = os.path.join(output, "CNAME")
        try:
            with open(path) as f:
                cname = f.read()
        except Exception as _:
            status(f"  - Couldn't load CNAME---treating it as empty.", 1)
            cname = ""

        fail_if_not(
            "federico.morarocha.ca" != cname, f"Please use your own CNAME at {path}"
        )


    def read_data(json_file_name: str, optional: bool):
        path = os.path.join(data, json_file_name)
        try:
            with open(path) as f:
                status(f"- loading {path}")
                dataf = json.load(f)
        except Exception as _:
            fail_if_not(
                optional,
                f"Failed to parse {path}. Check your commas, braces, and if the file exists.",
            )
            # fail_if_not will exit if needed so the code below will only run if this data is optional
            status(f"Failed to load {path}---treating it as empty.", 0)
            dataf = {}

        return dataf


    def read_template(template_file_name: str, optional: bool):
        path = os.path.join(templates, template_file_name)
        try:
            with open(path) as f:
                status(f"- loading {path}")
                dataf = f.read()
        except Exception as _:
            fail_if_not(optional, f"Failed to read {path}. Does it exist?")
            # fail_if_not will exit if needed
            status(f"Couldn't load {path}---treating it as empty.", 0)
            dataf = ""

        return dataf


    def write_file(file_name: str, contents: str):
        path = os.path.join(output, file_name)
        if contents == "":
            return

        with open(path, "w") as target:
            status(f"- writing {path}")
            target.write(contents)


    def replace_placeholders(text: str, map: Dict[str, str]):
        newtext = text

        for k in map:
            newtext = newtext.replace(k + "-placeholder", map[k])

        return newtext


    # Define functions for website pieces


    def header(has_dark):
        if has_dark:
            button = f"""<label class="switch-mode">
    <input type="checkbox" id="mode">
    <span class="slider round"></span>
</label>
"""
        else:
            button = ""

        out = '<div id="scroller"></div>\n%s' % button
        out += f'<script>{scroller_js}</script>\n'
        out += f'<script>{mode_js}</script>\n' if has_dark else ""
        out = f"<header>{out}</header>\n"
        return out


    def build_news(news: List[Dict[str, str]], count: int, standalone: bool):
        if count > len(news):
            count = len(news)

        if count <= 0:
            return ""

        status("\nAdding news:")
        news_list = ""

        for n in news[:count]:
            status("- " + n["date"])
            news_map = {
                "news-date": n["date"],
                "news-text": n["text"],
            }
            news_list += replace_placeholders(news_item_html, news_map)

        news_html = '<div class="section">\n'

        if count != len(news):
            link = '<a href="./news.html">see all</a>'
            news_html += (
                '<h1>Recent News <span class="more">(%s)</span></h1>\n'
                % link
            )
        elif standalone:
            link = '<a href="./index.html">%s</a>' % meta_json["name"]
            news_html += (
                '<h1>News <span class="more">%s</span></h1>\n'
                % link
            )
        else:
            news_html += "<h1>News</h1>\n"

        news_html += '<div class="hbar"></div>\n'
        news_html += '<div id="news">\n'
        news_html += news_list
        news_html += "</div>\n"  # close news
        news_html += "</div>\n"  # close section

        return news_html


    # Helper function to decide what publication sections to include
    def get_pub_titles(pubs, full: bool):
        titles = set()
        for p in pubs.entries.values():
            if p.fields["build_selected"] == "true" or full:
                titles.add(p.fields["build_keywords"])

        return sorted(list(titles))


    def some_not_selected(pubs):
        for p in pubs.entries.values():
            if not p.fields["build_selected"] == "true":
                return True

        return False


    def build_authors(authors, mentoring_json: List[Dict[str, str]]):
        item = ""

        authors_split = []
        for a in authors:
            entry = "%s%s%s" % (
                " ".join(a.first_names)[0] + ". ",
                " ".join(a.middle_names)[0] + ". " if len(a.middle_names) > 0 else "",
                " ".join(a.last_names),
            )

            name = " ".join(a.first_names)
            name += "" if len(a.middle_names) == 0 else " " + " ".join(a.middle_names)
            name += " " + " ".join(a.last_names)
            if name in auto_links_json:
                entry = '<a href="%s">%s</a>' % (auto_links_json[name], entry)
            else:
                status(f"-- {name} is not in auto_links.json", 3)
            if name in [e["name"] for e in mentoring_json]:
                entry = f"<span class=\"mentee\">{entry}</span>"

            authors_split.append(entry)

        for i in range(len(authors_split)):
            entry = authors_split[i]
            if i < len(authors_split) - 2:
                entry += ",\n"
            if i == len(authors_split) - 2:
                entry += " and\n"
            authors_split[i] = entry

        authors_text = str(authors)
        authors_text = authors_text.replace("[", "").replace("]", "").replace("'", "").replace("(", "").replace(")", "").replace("Person", "")
        if len(authors_text) > 100:
            status(f"Splitting authors: {authors_text}", 3)
            authors_split.insert((len(authors_split) // 2) + 1, '<br class="bigscreen">')
        item += "".join(authors_split)
        return item


    def build_icons(p):
        item = ""
        item += (
            '<a href="'
            + p.fields["build_link"]
            + '" alt="[PDF] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>'
            % (style_json["light"]["paper-img"], style_json["dark"]["paper-img"])
            if p.fields["build_link"]
            else ""
        )
        item += (
            '<a href="'
            + p.fields["build_extra"]
            + '" alt="[Extra] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>'
            % (style_json["light"]["extra-img"], style_json["dark"]["extra-img"])
            if p.fields["build_extra"]
            else ""
        )
        item += (
            '<a href="'
            + p.fields["build_slides"]
            + '" alt="[Slides] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>'
            % (style_json["light"]["slides-img"], style_json["dark"]["slides-img"])
            if p.fields["build_slides"]
            else ""
        )
        item += (
            '<a href="'
            + p.fields["build_bibtex"]
            + '" alt="[Bibtex] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>'
            % (style_json["light"]["bibtex-img"], style_json["dark"]["bibtex-img"])
            if p.fields["build_bibtex"]
            else ""
        )
        return item


    def build_pubs_inner(pubs, mentoring_json: List[Dict[str, str]], title: str, full: bool):
        if title == "":
            return ""

        pubs_list = ""

        for p in pubs.entries.values():
            if title == p.fields["build_keywords"] and (p.fields["build_selected"] == "true" or full):
                status("- " + p.fields["title"])

                paper_conference = p.fields["build_short"] + " '" + p.fields["year"][-2:]
                if len(paper_conference) > 8:
                    paper_conference = f'<div class="bigscreen"><small>{paper_conference}</small></div><div class="smallscreen">{paper_conference}</div>'

                title_split = p.fields["title"].split()
                if len(p.fields["title"]) > 70:
                    status(f"Splitting title: {p.fields['title']}", 3)
                    title_split.insert((len(title_split) // 2) + 1, '<br class="bigscreen">')
                paper_title = " ".join(title_split)

                paper_map = {
                    "paper-title": paper_title,
                    "paper-authors": build_authors(p.persons['author'], mentoring_json),
                    "paper-conference": paper_conference,
                    "paper-icons": build_icons(p),
                }
                pubs_list += replace_placeholders(paper_html, paper_map)

        pubs_html = '<h2 id="%spublications">%s</h2>' % (title, title)
        pubs_html += pubs_list

        return pubs_html


    def build_pubs(pubs, mentoring_json: List[Dict[str, str]], full: bool):
        if len(pubs.entries) == 0:
            return ""

        status("\nAdding publications:")

        pubs_html = '<div class="section">\n'

        if some_not_selected(pubs) and not full:
            pubs_html += '<h1>Selected Publications <span class="more">(<a href="./pubs.html">see all</a>)</span></h1>'
        elif full:
            link = '<a href="./index.html">%s</a>' % meta_json["name"]
            pubs_html += (
                '<h1>Publications <span class="more">%s</span></h1>\n'
                % link
            )
        else:
            pubs_html += '<h1>Publications</h1>'
        

        pubs_html += '<div class="hbar"></div>\n'
        pubs_html += '<span class="legend">(undergraduate mentees underlined)</span>\n'
        pubs_html += '<div id="publications">\n'

        titles = get_pub_titles(pubs, full)

        for i in range(len(titles)):
            title = titles[i]
            pubs_html += build_pubs_inner(pubs, mentoring_json, title, full)

        pubs_html += "</div>\n"  # close pubs
        pubs_html += "</div>\n"  # close section

        return pubs_html


    def build_profile(profile: Dict[str, str]):
        profile_html = '<div class="profile">\n'
        profile_html += (
            '<img class="headshot" src="%s" alt="Headshot"/>\n' % profile["headshot"]
        )
        profile_html += "<p>" + "</p><p>".join(profile["about"].split("\n")) + "</p>"
        if "research" in profile and profile["research"] != "":
            profile_html += "<p>" + "</p><p>".join(profile["research"].split("\n")) + "</p>"
        if "contact" in profile and profile["contact"] != "":
            profile_html += "<p>" + "</p><p>".join(profile["contact"].split("\n")) + "</p>"
        if "announcement" in profile and profile["announcement"] != "":
            profile_html += '<div class="announcement">\n'
            profile_html += profile["announcement"]
            profile_html += "</div>\n"  # close announcement
        profile_html += "</div>\n"  # close profile

        return profile_html


    def add_notes(html: str, notes: Dict[str, str]):
        status("\nAdding notes:", 2)

        toreplace = sorted(notes.keys(), key=len, reverse=True)

        for name in toreplace:
            pos = html.find(name)
            while pos != -1:
                prefix = html[:pos]
                suffix = html[pos:]

                open = html[:pos].count("<abbr title=")
                close = html[:pos].count("</abbr>")

                status(f"- {name} {pos} {open} {close}", 2)
                target = name + " "
                if pos >= 0 and open == close:
                    target = '<abbr title="%s">%s</abbr>' % (notes[name], name)
                    suffix = suffix.replace(name, target, 1)
                    html = prefix + suffix

                start = (len(prefix) - len(name)) + len(
                    target
                )  # we got rid of name and replaced it with target
                tmp = html[start:].find(name)
                pos = tmp + start if tmp >= 0 else tmp

        return html


    def add_links(html: str, links: Dict[str, str]):
        status("\nAdding links:", 2)

        toreplace = sorted(links.keys(), key=len, reverse=True)

        for name in toreplace:
            pos = html.find(name)
            while pos != -1:
                prefix = html[:pos]
                suffix = html[pos:]

                open = html[:pos].count("<a href=")
                close = html[:pos].count("</a>")

                status(f"- {name} {pos} {open} {close}", 2)
                target = name + " "
                if pos >= 0 and open == close:
                    target = '<a href="%s">%s</a>' % (links[name], name)
                    suffix = suffix.replace(name, target, 1)
                    html = prefix + suffix

                start = (len(prefix) - len(name)) + len(
                    target
                )  # we got rid of name and replaced it with target
                tmp = html[start:].find(name)
                pos = tmp + start if tmp >= 0 else tmp

        return html


    def build_index(
        profile_json: Dict[str, str],
        news_json: List[Dict[str, str]],
        pubs_bibtex,
        mentoring_json: List[Dict[str, str]],
        links: Dict[str, str],
        notes: Dict[str, str],
        has_dark: bool,
    ):
        body_html = "<body>\n"
        body_html += header(has_dark)
        body_html += '<div class="content">\n'
        body_html += build_profile(profile_json)
        body_html += build_news(news_json, 5, False)
        body_html += build_pubs(pubs_bibtex, mentoring_json, False)
        body_html += "</div>\n"
        body_html += footer_html
        body_html += "</body>\n"

        index_page = "<!DOCTYPE html>\n"
        index_page += '<html lang="en">\n'
        index_page += head_html + "\n\n"
        index_page += add_notes(add_links(body_html, links), notes)
        index_page += "</html>\n"

        return inspect.cleandoc(index_page)


    def build_news_page(
        news_json: List[Dict[str, str]],
        links: Dict[str, str],
        notes: Dict[str, str],
        has_dark: bool,
    ):
        content = build_news(news_json, len(news_json), True)

        if content == "":
            return ""

        body_html = "<body>\n"
        body_html += header(has_dark)
        body_html += '<div class="content">\n'
        body_html += content
        body_html += "</div>\n"
        body_html += footer_html
        body_html += "</body>\n"

        news_html = "<!DOCTYPE html>\n"
        news_html += '<html lang="en">\n'
        news_html += head_html + "\n\n"
        news_html += add_notes(add_links(body_html, links), notes)
        news_html += "</html>\n"

        return inspect.cleandoc(news_html)


    def build_pubs_page(
        pubs_bibtex,
        mentoring_json: List[Dict[str, str]],
        links: Dict[str, str],
        notes: Dict[str, str],
        has_dark: bool,
    ):
        content = build_pubs(pubs_bibtex, mentoring_json, True)

        if content == "":
            return ""

        body_html = "<body>\n"
        body_html += header(has_dark)
        body_html += '<div class="content">\n'
        body_html += content
        body_html += "</div>\n"
        body_html += footer_html
        body_html += "</body>\n"

        pubs_html = "<!DOCTYPE html>\n"
        pubs_html += '<html lang="en">\n'
        pubs_html += head_html + "\n\n"
        pubs_html += add_notes(add_links(body_html, links), notes)
        pubs_html += "</html>\n"

        return inspect.cleandoc(pubs_html)


    def build_cv(
        meta_json: Dict[str, str],
        profile_json: Dict[str, str],
        education_json: Dict[str, str],
        pubs_bibtex,
    ):
        cv_tex = r"\documentclass{federico_cv}" + "\n"
        cv_tex += r"\frenchspacing" + "\n"
        cv_tex += r"\usepackage[backend=biber,style=numeric,refsection=section,maxbibnames=99,sorting=none,defernumbers=true]{biblatex}" + "\n"
        cv_tex += r"\bibliography{cv}" + "\n"
        cv_tex += r"\begin{document}" + "\n\n\n"

        cv_tex += f"\\contact{{{meta_json['name']}}}\n"
        cv_tex += f"{{\\link{{{profile_json['website']}}}{{{profile_json['website']}}}}}\n"
        cv_tex += f"{{\\link{{mailto:{profile_json['email']}}}{{{profile_json['email']}}}}}\n\n\n"

        cv_tex += "\\section{Research Interests}\n"
        cv_tex += f"{profile_json['research']}\n\n\n"

        cv_tex += r"\begin{tblSection}{Education}{0.1}{0.85}" + "\n"
        for edu in education_json:
            cv_tex += "\\degree\n"
            cv_tex += f"{{{edu['year']}}}\n"
            cv_tex += f"{{{edu['degree']}}}\n"
            cv_tex += f"{{{edu['note']}}}\n"
            cv_tex += f"{{{edu['institution']}}}\n\n"
        cv_tex += r"\end{tblSection}" + "\n\n\n"

        cv_tex += r"\nocite{*}" + "\n"
        sections = []
        for pub in pubs_bibtex.entries.values():
            sections.append(pub.fields["build_keywords"])
        sections = sorted(list(set(sections)))
        for section in sections:
            cv_tex += f"\\printbibliography[keyword={{{section}}},title={{{section}}},resetnumbers=true]\n"
        cv_tex += "\n\n\n"

        cv_tex += r"\end{document}"
        return cv_tex

    cleanup()

    # Load json files
    status("Loading json files:")

    meta_json = read_data("meta.json", optional=False)
    fail_if_not("name" in meta_json, f'Must include a "name" in {data}/meta.json!')
    fail_if_not(
        "description" in meta_json, f'Must include a "description" in {data}/meta.json!'
    )
    fail_if_not("favicon" in meta_json, f'Must include a "favicon" in {data}/meta.json!')
    fill_if_missing(meta_json, "tracker")

    style_json = read_data("style.json", optional=False)

    # must have a "light" theme
    fail_if_not(
        "light" in style_json, f'Must include a "light" theme in {data}/style.json!'
    )
    has_dark = "dark" in style_json

    # if there is no dark theme, then the light theme will be used for both
    if not has_dark:
        style_json["dark"] = style_json["light"]

    # for each key in style_json, check its format
    for key in style_json:
        fail_if_not(
            "primary-color" in style_json[key], f'Must include a "primary-color" for {key} in {data}/style.json!'
        )
        fail_if_not(
            "secondary-color" in style_json[key], f'Must include a "secondary-color" for {key} in {data}/style.json!'
        )
        fail_if_not(
            "tertiary-color" in style_json[key], f'Must include a "tertiary-color" for {key} in {data}/style.json!'
        )
        fail_if_not(
            "quaternary-color" in style_json[key], f'Must include a "quaternary-color" for {key} in {data}/style.json!'
        )
        fail_if_not(
            "divider-width" in style_json[key],
            f'Must include a "divider-width" for {key} in {data}/style.json!',
        )
        fail_if_not(
            "underline-width" in style_json[key],
            f'Must include a "underline-width" for {key} in {data}/style.json!',
        )
        fail_if_not(
            "paper-img" in style_json[key], f'Must include a "paper-img" for {key} in {data}/style.json!'
        )
        fail_if_not(
            "extra-img" in style_json[key], f'Must include a "extra-img" for {key} in {data}/style.json!'
        )
        fail_if_not(
            "slides-img" in style_json[key], f'Must include a "slides-img" for {key} in {data}/style.json!'
        )
        fail_if_not(
            "bibtex-img" in style_json[key], f'Must include a "bibtex-img" for {key} in {data}/style.json!'
        )

    profile_json = read_data("profile.json", optional=False)
    fail_if_not(
        "headshot" in profile_json,
        f'Must include a "headshot" field in {data}/profile.json!',
    )
    fail_if_not(
        "about" in profile_json,
        f'Must include a "about" field in {data}/profile.json!',
    )

    # These next four can be empty
    news_json = read_data("news.json", optional=True)
    for news in news_json:
        fail_if_not(
            "date" in news,
            f'Must include a "date" field for each news in {data}/news.json!',
        )
        fail_if_not(
            "text" in news,
            f'Must include a "text" field for each news in {data}/news.json!',
        )

    dates = [datetime.strptime(n["date"], "%m/%Y") for n in news_json]
    warn_if_not(
        dates == sorted(dates, reverse=True),
        f"The dates in {data}/news.json are not in order.",
    )

    mentoring_json = read_data("mentoring.json", optional=True)
    for mentoring in mentoring_json:
        fail_if_not(
            "name" in mentoring,
            f'Must include a "name" field for each mentoring in {data}/mentoring.json!',
        )

    pubs_bibtex = parse_file(f"{data}/publications.bib") if os.path.exists(f"{data}/publications.bib") else []
    for pub in pubs_bibtex.entries.values():
        fail_if_not(
            "title" in pub.fields,
            f'Must include a "title" field for each pub in {data}/publications.json!',
        )
        fail_if_not(
            "journal" in pub.fields or "booktitle" in pub.fields,
            f'Must include a "journal" or "booktitle" field for each pub in {data}/publications.json!',
        )
        fail_if_not(
            len(pub.persons['author']) > 0,
            f'Must include an "author" field for each pub in {data}/publications.json!',
        )
        fail_if_not(
            "build_short" in pub.fields,
            f'Must include a "build_short" subfield for each pub venue in {data}/publications.json!',
        )

        pub.fields["build_link"] = "" if "build_link" not in pub.fields else pub.fields["build_link"]
        pub.fields["build_extra"] = "" if "build_extra" not in pub.fields else pub.fields["build_extra"]
        pub.fields["build_slides"] = "" if "build_slides" not in pub.fields else pub.fields["build_slides"]
        pub.fields["build_bibtex"] = "" if "build_bibtex" not in pub.fields else pub.fields["build_bibtex"]

        fail_if_not(
            "build_keywords" in pub.fields,
            f'Must include a "build_keywords" field for each pub in {data}/publications.json!',
        )
        fail_if_not(
            "build_selected" in pub.fields,
            f'Must include a "build_selected" field for each pub in {data}/publications.json!',
        )

    education_json = read_data("education.json", optional=True)
    for education in education_json:
        fail_if_not(
            "year" in education,
            f'Must include a "year" field for each education in {data}/education.json!',
        )
        fail_if_not(
            "degree" in education,
            f'Must include a "degree" field for each education in {data}/education.json!',
        )
        fill_if_missing(education, "note")
        fail_if_not(
            "institution" in education,
            f'Must include a "institution" field for each education in {data}/education.json!',
        )

    auto_links_json = read_data("auto_links.json", optional=True)
    auto_notes_json = read_data("auto_notes.json", optional=True)

    # Sanity checks
    if not is_federicos(meta_json["name"]):
        status("\nPerforming sanity checks:")
        check_cname()
        check_tracker(meta_json["tracker"])

    # Load templates
    status("\nLoading template files:")
    main_css = read_template("main.css", optional=False)
    light_css = read_template("light.css", optional=False)
    dark_css = read_template("dark.css", optional=True)
    dark_css = light_css if dark_css == "" else dark_css
    head_html = read_template("head.html", optional=False)
    footer_html = read_template("footer.html", optional=False)
    paper_html = read_template("paper.html", optional=False)
    news_item_html = read_template("news-item.html", optional=False)
    mode_js = read_template("mode.js", optional=False)
    scroller_js = read_template("scroller.js", optional=False)

    if is_federicos(meta_json["name"]):
        footer_html = """\n<footer>\n<p>Feel free to <a href="https://github.com/FedericoAureliano/FedericoAureliano.github.io">use this website template</a>.</p>\n</footer>\n"""
    else:
        footer_html = "\n" + footer_html

    # Create HTML and CSS
    head_html = replace_placeholders(head_html, meta_json)
    footer_html = replace_placeholders(footer_html, meta_json)
    light_css = replace_placeholders(light_css, style_json["light"])
    if has_dark:
        dark_css = replace_placeholders(dark_css, style_json["dark"])
    news_page = build_news_page(news_json, auto_links_json, auto_notes_json, has_dark)
    pubs_page = build_pubs_page(pubs_bibtex, mentoring_json, auto_links_json, auto_notes_json, has_dark)
    index_page = build_index(profile_json, news_json, pubs_bibtex, mentoring_json, auto_links_json, auto_notes_json, has_dark)

    # Write to files
    status("\nWriting website:")
    write_file("index.html", index_page)
    write_file("news.html", news_page)
    write_file("pubs.html", pubs_page)
    write_file("main.css", main_css)
    write_file("light.css", light_css)
    write_file("dark.css", dark_css)

    # Got to here means everything went well
    success(f"Open {output}/index.html in your browser to see your website!")

    if not cv:
        exit(0)
    
    status("Generating Curriculum Vitae Latex:")
    write_file(f"{output}/cv/cv.tex", build_cv(meta_json, profile_json, education_json, pubs_bibtex))
    
    # remove all the entries in pubs_bibtex that start with build_
    for key in list(pubs_bibtex.entries.keys()):
        for field in list(pubs_bibtex.entries[key].fields.keys()):
            if field == "build_keywords":
                pubs_bibtex.entries[key].fields["keywords"] = pubs_bibtex.entries[key].fields["build_keywords"]
                pubs_bibtex.entries[key].fields.pop(field)
            elif field.startswith("build_"):
                pubs_bibtex.entries[key].fields.pop(field)

    # make the your name bold in cv
    for key in list(pubs_bibtex.entries.keys()):
        authors = pubs_bibtex.entries[key].persons["author"]
        for name in meta_json["name"].split():
            authors = [Person(str(author).replace(name, r"\textbf{" + name + "}")) for author in authors]
        pubs_bibtex.entries[key].persons["author"] = authors

    pubs_bibtex.to_file(f"{output}/cv/cv.bib")


    # Got to here means everything went well
    success(f"Navigate to {output}/cv and do `make view` to see your curriculum vitae!")
    exit(0)