#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS={
    "w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp":"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "dc":"http://purl.org/dc/elements/1.1/",
    "cp":"http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
}

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--package-dir",type=Path,required=True)
    return p.parse_args()

def visible_text(root):
    return "\n".join((n.text or "") for n in root.findall(".//w:t",NS))

def inspect_docx(path:Path):
    if not zipfile.is_zipfile(path):
        raise AssertionError(f"invalid DOCX: {path}")
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist())
        for req in ("[Content_Types].xml","word/document.xml","docProps/core.xml"):
            if req not in names:
                raise AssertionError(f"{path.name} missing {req}")
        raw=z.read("word/document.xml")
        root=ET.fromstring(raw)
        core=ET.fromstring(z.read("docProps/core.xml"))
        text=visible_text(root)
        images=root.findall(".//wp:docPr",NS)
        lnums=root.findall(".//w:lnNumType",NS)
        if b"rsid" in raw:
            raise AssertionError(f"{path.name} retains rsid identifiers")
        for fld in ("dc:creator","cp:lastModifiedBy"):
            node=core.find(fld,NS)
            if node is not None and (node.text or "").strip():
                raise AssertionError(f"{path.name} retains identifying core property {fld}")
        return text,images,lnums

def main():
    a=parse_args()
    expected={
        "main":a.package_dir/"Chapter2_JEB_Anonymous_Manuscript_V10.docx",
        "title":a.package_dir/"Chapter2_JEB_Title_Page_V10.docx",
        "si":a.package_dir/"Chapter2_JEB_Supporting_Information_V10.docx",
        "cover":a.package_dir/"Chapter2_JEB_Cover_Letter_V10.docx",
    }
    for p in expected.values():
        if not p.exists() or p.stat().st_size<1000:
            raise AssertionError(f"missing/undersized output: {p}")

    main_text,main_images,main_ln=inspect_docx(expected["main"])
    if len(main_images)!=5:
        raise AssertionError(f"anonymous main expected 5 figures, found {len(main_images)}")
    for node in main_images:
        if not node.attrib.get("descr","").startswith("Alternative text:"):
            raise AssertionError("main figure missing meaningful alt text")
    if not main_ln or any(x.attrib.get(f"{{{NS['w']}}}restart")!="continuous" for x in main_ln):
        raise AssertionError("anonymous main lacks continuous line numbering")
    for token in (
        "A young Cirsium radiation repeatedly rebuilt its reproductive head",
        "Transparency and reproducibility",
        "Generative-AI assistance was used",
        "References",
        "Figure 1.","Figure 2.","Figure 3.","Figure 4.","Figure 5.",
    ):
        if token not in main_text:
            raise AssertionError(f"main missing {token!r}")
    for bad in (
        "Figure legends","Data Availability Statement","Acknowledgements",
        "Conflict of Interest","[INSERT","github.com/zuizui0223","zuizui0223",
        "Submission-preparation notes",
    ):
        if bad.casefold() in main_text.casefold():
            raise AssertionError(f"anonymous main retains forbidden text: {bad}")

    title_text,title_images,title_ln=inspect_docx(expected["title"])
    if title_images or title_ln:
        raise AssertionError("title page should contain neither images nor line numbering")
    for token in (
        "A young Cirsium radiation repeatedly rebuilt its reproductive head",
        "Authors and affiliations","Corresponding author","Acknowledgements",
        "Funding","Conflict of Interest","Data Availability Statement","Ethical approval",
    ):
        if token not in title_text:
            raise AssertionError(f"title page missing {token!r}")
    if "{{MAIN_WORD_COUNT}}" in title_text or "{{ABSTRACT_WORD_COUNT}}" in title_text:
        raise AssertionError("title page count tokens were not materialized")
    if "Submission check" in title_text:
        raise AssertionError("internal submission checklist leaked into title page")
    if not re.search(r"Main-text word count before References:\s*\d+",title_text):
        raise AssertionError("title page missing materialized main word count")
    if not re.search(r"Abstract word count:\s*\d+",title_text):
        raise AssertionError("title page missing materialized abstract word count")

    si_text,si_images,si_ln=inspect_docx(expected["si"])
    if si_images:
        raise AssertionError("text-only SI unexpectedly contains embedded images")
    if not si_ln:
        raise AssertionError("SI should retain continuous line numbering for review")
    for token in (
        "ACTIVE V10 SUPPORTING INFORMATION",
        "Repeated state change and relative evolutionary depth",
        "Orientation transition-regime analysis",
        "Historical environmental-cause boundary",
        "Reproductive herbivory meta-analysis",
        "A young Cirsium radiation repeatedly rebuilt its reproductive head",
    ):
        if token not in si_text:
            raise AssertionError(f"SI missing {token!r}")
    if "Supporting-information audit checklist" in si_text:
        raise AssertionError("internal SI audit checklist leaked into submission SI")

    cover_text,cover_images,cover_ln=inspect_docx(expected["cover"])
    if cover_images or cover_ln:
        raise AssertionError("cover letter should have neither figures nor line numbering")
    for token in (
        "Journal of Evolutionary Biology",
        "A young Cirsium radiation repeatedly rebuilt its reproductive head",
        "double-anonymous review",
        "post-result focused hypothesis",
        "Generative-AI assistance was used",
    ):
        if token not in cover_text:
            raise AssertionError(f"cover letter missing {token!r}")

    print("chapter2_jeb_v10_docx_package: PASS")
    print("anonymous_main_figures=5")
    print("anonymous_main_line_numbering=continuous")
    print("main_title_page_separation=valid")
    print("si_v10=valid")
    print("metadata_and_rsid_scrub=valid")

if __name__=="__main__":
    main()
