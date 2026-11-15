"""Invoice PDFs, written by hand: one page, Helvetica, WinAnsi text.

No PDF library is needed for a one-page text document, the output is byte-for-byte
deterministic (no timestamps), and text extraction (the invoice extractor in M3, or any
PDF reader) gets real text, not an image.
"""

from backroom_portals.grainline.catalog import BY_SKU
from backroom_portals.grainline.store import Invoice

SUPPLIER = "Grainline Wholesale GmbH"
SUPPLIER_ADDRESS = "Lagerstraße 12, 53111 Bonn"
CUSTOMER = "Hafer & Bohne"
CUSTOMER_ADDRESS = "Südstadt, 53113 Bonn"


def _eur(value: float) -> str:
    return f"€{value:,.2f}"


def _text(x: int, y: int, s: str, size: int = 10, bold: bool = False) -> bytes:
    escaped = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    font = "F2" if bold else "F1"
    return f"BT /{font} {size} Tf {x} {y} Td (".encode() + escaped.encode("cp1252") + b") Tj ET\n"


def invoice_pdf(invoice: Invoice) -> bytes:
    ops: list[bytes] = [
        _text(50, 790, SUPPLIER, 16, bold=True),
        _text(50, 774, SUPPLIER_ADDRESS, 9),
        _text(400, 790, "INVOICE", 16, bold=True),
        _text(400, 772, f"Invoice no.: {invoice.id}"),
        _text(400, 758, f"Date: {invoice.issued_on.isoformat()}"),
        _text(400, 744, f"Order: {invoice.order_id}"),
        _text(50, 730, "Bill to:", bold=True),
        _text(50, 716, CUSTOMER),
        _text(50, 702, CUSTOMER_ADDRESS),
        _text(50, 660, "SKU", bold=True),
        _text(150, 660, "Description", bold=True),
        _text(370, 660, "Qty", bold=True),
        _text(420, 660, "Unit price", bold=True),
        _text(500, 660, "Amount", bold=True),
    ]
    y = 640
    for line in invoice.lines:
        product = BY_SKU[line.sku]
        ops += [
            _text(50, y, line.sku),
            _text(150, y, product.name),
            _text(370, y, str(line.qty)),
            _text(420, y, _eur(line.unit_price_eur)),
            _text(500, y, _eur(round(line.qty * line.unit_price_eur, 2))),
        ]
        y -= 16
    y -= 10
    ops.append(_text(400, y, f"Net total: {_eur(invoice.net_eur)}"))
    for rate, amount in invoice.vat_eur().items():
        y -= 14
        ops.append(_text(400, y, f"VAT {rate}%: {_eur(amount)}"))
    y -= 16
    ops.append(_text(400, y, f"Total due: {_eur(invoice.gross_eur)}", 11, bold=True))
    ops.append(_text(50, 60, "Payment within 14 days. Thank you for your order.", 8))
    return _document(b"".join(ops))


def _document(content: bytes) -> bytes:
    font = "<< /Type /Font /Subtype /Type1 /BaseFont /{} /Encoding /WinAnsiEncoding >>"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>",
        font.format("Helvetica").encode(),
        font.format("Helvetica-Bold").encode(),
        f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"endstream",
    ]
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets: list[int] = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets)
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(out)
