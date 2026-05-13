#!/usr/bin/env python3
"""
Styled Writer Markdown -> EPUB converter.

Usage:
  python styled-writer/scripts/md_to_epub.py input.md output.epub --author "作者风格 · Codex"

Dependencies:
  pip install markdown ebooklib --break-system-packages
"""

import argparse
import os

import markdown
from ebooklib import epub


CSS = """
body {
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", serif;
    font-size: 1em;
    line-height: 1.8;
    color: #222;
    margin: 1em;
}
h1 {
    font-size: 1.65em;
    color: #111;
    margin: 1.2em 0 1em 0;
    padding-bottom: 0.35em;
    border-bottom: 1.5px solid #444;
    text-indent: 0;
}
h2 {
    font-size: 1.25em;
    color: #222;
    margin: 1.1em 0 0.5em 0;
    text-indent: 0;
}
h3 {
    font-size: 1.1em;
    color: #333;
    margin: 0.9em 0 0.4em 0;
    text-indent: 0;
}
p {
    margin: 0;
    text-indent: 2em;
}
blockquote {
    margin: 0.6em 0;
    padding: 0.4em 0.6em 0.4em 1em;
    border-left: 3px solid #666;
    color: #555;
    font-size: 0.95em;
}
blockquote p {
    text-indent: 0;
}
ul, ol {
    margin: 0.4em 0;
    padding-left: 1.5em;
}
li {
    margin: 0.2em 0;
    text-indent: 0;
}
hr {
    border: none;
    border-top: 1px solid #bbb;
    margin: 1em 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.8em 0;
    font-size: 0.9em;
}
thead th {
    background: #333;
    color: #fff;
    padding: 0.4em 0.5em;
    text-align: left;
}
tbody td {
    padding: 0.35em 0.5em;
    border-bottom: 1px solid #ccc;
}
code {
    font-family: monospace;
    background: #f6f6f6;
    padding: 0 0.2em;
    font-size: 0.9em;
}
a {
    color: #245c8a;
    text-decoration: none;
}
.title-page {
    text-align: center;
    padding: 3em 1em;
}
.title-page h1 {
    font-size: 2em;
    border: none;
    margin-bottom: 0.5em;
}
.title-page .subtitle {
    font-size: 1.05em;
    color: #777;
    margin-bottom: 1em;
}
.title-page .divider {
    width: 60%;
    margin: 1em auto;
    border: none;
    border-top: 1.5px solid #444;
}
.title-page .author {
    font-size: 0.95em;
    color: #666;
}
"""


def split_title(markdown_text):
    lines = markdown_text.splitlines()
    body_lines = []
    title = None

    for line in lines:
        if title is None and line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            continue
        body_lines.append(line)

    return title or "多风格写作文章", "\n".join(body_lines)


def md_to_epub(md_path, epub_path, author="Codex"):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    title, body_md = split_title(md_text)
    html_body = markdown.markdown(
        body_md,
        extensions=["tables", "fenced_code", "extra"],
        output_format="html5",
    )

    cover_html = f"""<div class="title-page">
<h1>{title}</h1>
<div class="subtitle">多风格写作</div>
<hr class="divider"/>
<div class="author">作者: {author}</div>
</div>"""

    book = epub.EpubBook()
    book.set_identifier(f"styled-writer-{title}")
    book.set_title(title)
    book.set_language("zh-CN")
    book.add_author(author)

    css_item = epub.EpubItem(
        uid="style",
        file_name="style/default.css",
        media_type="text/css",
        content=CSS.encode("utf-8"),
    )
    book.add_item(css_item)

    chapter = epub.EpubHtml(title=title, file_name="content.xhtml", lang="zh-CN")
    chapter.content = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-CN">
<head><title>{title}</title></head>
<body>
{cover_html}
{html_body}
</body>
</html>"""
    chapter.add_item(css_item)
    book.add_item(chapter)

    book.spine = [chapter]
    book.toc = [chapter]

    epub.write_epub(epub_path, book)
    size_kb = os.path.getsize(epub_path) / 1024
    print(f"[OK] EPUB generated: {epub_path} ({size_kb:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Styled Writer Markdown -> EPUB")
    parser.add_argument("input", help="Input Markdown path")
    parser.add_argument("output", help="Output EPUB path")
    parser.add_argument("--author", default="Codex", help="Author name")
    args = parser.parse_args()

    md_to_epub(args.input, args.output, author=args.author)


if __name__ == "__main__":
    main()
