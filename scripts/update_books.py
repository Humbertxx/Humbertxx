#!/usr/bin/env python3
import re
import sys
import os

import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from html import escape
from config import FEED, HEADERS, START, END, README



def main():
    missing = [name for name in ("USER_ID", "SHELF") if not os.getenv(name, "").strip()]
    if missing:
        raise SystemExit("Missing required settings: " + ", ".join(missing)
            + ". Configure them as GitHub Actions repository secrets.")

    try:
        books = parse(fetch(FEED))
    except (urllib.error.URLError, ET.ParseError) as exc:
        print(f"could not refresh shelf: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    
    current = README.read_text()
    updated = splice(current, render(books))
    
    if updated == current:
        print("no change")

    README.write_text(updated)
    print(f"updated with {len(books)} book(s)")

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def parse(xml):
    books = []
    for item in ET.fromstring(xml).findall("./channel/item"):
        text = lambda tag: (item.findtext(tag) or "").strip()
        title = text("title")
        if not title:
            continue

        book_id = text("book_id")
        link = f"https://www.goodreads.com/book/show/{book_id}" if book_id else text("link")
        books.append(
            {
                "title": title,
                "author": text("author_name"),
                "link": link,
                "cover": text("book_medium_image_url"),
            }
        )
    return books


def render(books):
    if not books:
        return "_Nothing on the nightstand right now._"

    lines = []
    for b in books:
        title = escape(b["title"])
        linked = f'<a href="{escape(b["link"])}">{title}</a>' if b["link"] else title
        cover = (
            f'<img src="{escape(b["cover"])}" alt="" align="left" height="90" hspace="10" />'
            if b["cover"]
            else ""
        )
        author = f"<br /><sub>{escape(b['author'])}</sub>" if b["author"] else ""
        lines.append(f"{cover}<strong>{linked}</strong>{author}<br clear=\"left\" />")
    return "\n<br />\n".join(lines)


def splice(readme, block):
    pattern = re.compile(
        f"({re.escape(START)})(.*?)({re.escape(END)})", re.DOTALL
    )
    if not pattern.search(readme):
        raise SystemExit(f"markers {START} / {END} not found in README.md")
    return pattern.sub(lambda m: f"{m.group(1)}\n{block}\n{m.group(3)}", readme)





if __name__ == "__main__":
    main()
