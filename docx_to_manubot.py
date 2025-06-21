#!/usr/bin/env python3
"""Convert a DOCX dissertation into Manubot-compatible markdown files.

Usage:
    python docx_to_manubot.py Dissertation.docx content/
"""

import re
import sys
import subprocess
from pathlib import Path


def convert_docx_to_markdown(docx_path: str) -> str:
    temp_md = Path("temp_conversion.md")
    subprocess.run([
        "pandoc",
        docx_path,
        "-t",
        "markdown",
        "--wrap=preserve",
        "-o",
        str(temp_md),
    ], check=True)
    text = temp_md.read_text(encoding="utf-8")
    temp_md.unlink()
    return text


def slugify(text: str) -> str:
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def split_markdown(markdown: str):
    lines = markdown.splitlines()
    sections = []
    current = []
    heading = "front-matter"
    for line in lines:
        if line.startswith("# "):
            if current:
                sections.append((heading, current))
                current = []
            heading = line[2:].strip()
        current.append(line)
    if current:
        sections.append((heading, current))
    return sections


def create_toc(section_lines):
    toc = []
    for line in section_lines:
        if line.startswith("##"):
            level = len(line.split(" ")[0])
            heading = line[level + 1:].strip()
            slug = slugify(heading)
            indent = "  " * (level - 2)
            toc.append(f"{indent}- [**{heading}**](#{slug})")
    if toc:
        return ["## Inhaltsverzeichnis", *toc, ""]
    return []


def write_sections(sections, out_dir: str):
    Path(out_dir).mkdir(exist_ok=True, parents=True)
    mapping = []
    for i, (title, lines) in enumerate(sections):
        prefix = f"{i:02d}"
        filename = f"{prefix}_{slugify(title)}.md"
        toc = create_toc(lines)
        content = lines[:1] + toc + lines[1:]
        Path(out_dir, filename).write_text("\n".join(content), encoding="utf-8")
        mapping.append((prefix, filename, title))
    return mapping


def write_mapping(mapping, out_dir: str):
    lines = [
        "# Mapping Tabelle",
        "",
        "| Präfix | Dateiname | Kapitelüberschrift |",
        "|-------:|-----------|-------------------|",
    ]
    for prefix, fname, title in mapping:
        lines.append(f"| {prefix} | {fname} | {title} |")
    Path(out_dir, "00_mapping.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    if len(sys.argv) != 3:
        print("Usage: python docx_to_manubot.py INPUT.docx OUTPUT_DIR")
        sys.exit(1)
    docx_path, out_dir = sys.argv[1:3]
    markdown = convert_docx_to_markdown(docx_path)
    sections = split_markdown(markdown)
    mapping = write_sections(sections, out_dir)
    write_mapping(mapping, out_dir)


if __name__ == "__main__":
    main()
