"""Minimal streaming reader for one-sheet .xlsx files (stdlib only).

Enough for the Maven workbook: shared strings, numbers, first sheet. Rows stream via
iterparse, so 149k rows never sit in memory as XML.
"""

import zipfile
from collections.abc import Iterator
from typing import IO
from xml.etree.ElementTree import iterparse, parse

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _column(ref: str) -> str:
    return ref.rstrip("0123456789")


def rows(source: str | IO[bytes]) -> Iterator[dict[str, str]]:
    """Yield each data row as {header: text}; numbers stay as their XML text."""
    with zipfile.ZipFile(source) as book:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in book.namelist():
            root = parse(book.open("xl/sharedStrings.xml")).getroot()
            shared = ["".join(t.text or "" for t in si.iter(f"{_NS}t")) for si in root]
        header: dict[str, str] | None = None
        for _, el in iterparse(book.open("xl/worksheets/sheet1.xml")):
            if el.tag != f"{_NS}row":
                continue
            cells: dict[str, str] = {}
            for cell in el:
                value = cell.find(f"{_NS}v")
                if value is None or value.text is None:
                    continue
                text = shared[int(value.text)] if cell.get("t") == "s" else value.text
                cells[_column(cell.get("r", ""))] = text
            el.clear()
            if header is None:
                header = {col: name.strip() for col, name in cells.items()}
                continue
            yield {header[col]: text for col, text in cells.items() if col in header}
