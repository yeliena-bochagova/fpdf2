"""Utilities for building deterministic XMP metadata blocks."""

from html import escape as _html_escape
from typing import Sequence


class XMPManager:
    """
    Build XMP payloads for PDF/X identification metadata.

    The generated XMP string is intended to be passed to
    ``FPDF.set_xmp_metadata()`` and therefore does not include xpacket wrapping.
    """

    DEFAULT_PDFX_MODE = "PDF/X-1a:2001"
    SUPPORTED_PDFX_MODES = (DEFAULT_PDFX_MODE,)

    def __init__(
        self,
        *,
        pdf_x_mode: str = DEFAULT_PDFX_MODE,
        creator_tool: str = "fpdf2",
        title: str = "",
        description: str = "",
        creator: str | Sequence[str] = (),
        keywords: str | Sequence[str] = (),
        producer: str = "",
    ) -> None:
        if pdf_x_mode not in self.SUPPORTED_PDFX_MODES:
            supported = ", ".join(self.SUPPORTED_PDFX_MODES)
            raise ValueError(
                f"Unsupported PDF/X mode {pdf_x_mode!r}. Supported modes: {supported}"
            )
        self.pdf_x_mode = pdf_x_mode
        self.creator_tool = creator_tool
        self.title = title
        self.description = description
        self.creator = creator
        self.keywords = keywords
        self.producer = producer

    @staticmethod
    def _esc(value: object) -> str:
        escaped = _html_escape("" if value is None else str(value), quote=True)
        return escaped.replace("&#x27;", "&apos;").replace("'", "&apos;")

    @staticmethod
    def _as_list(value: str | Sequence[str]) -> list[str]:
        if isinstance(value, str):
            return [value] if value else []
        return [item for item in value if item]

    def build_xmp(self) -> str:
        creators = self._as_list(self.creator)
        keywords = self._as_list(self.keywords)
        parts = [
            '<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="fpdf2">',
            "  <rdf:RDF",
            '    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"',
            '    xmlns:dc="http://purl.org/dc/elements/1.1/"',
            '    xmlns:xmp="http://ns.adobe.com/xap/1.0/"',
            '    xmlns:pdf="http://ns.adobe.com/pdf/1.3/"',
            '    xmlns:pdfxid="http://www.npes.org/pdfx/ns/id/">',
            '    <rdf:Description rdf:about=""',
        ]
        if self.creator_tool:
            parts.append(f'        xmp:CreatorTool="{self._esc(self.creator_tool)}"')
        if self.producer:
            parts.append(f'        pdf:Producer="{self._esc(self.producer)}"')
        if keywords:
            parts.append(f'        pdf:Keywords="{self._esc(",".join(keywords))}"')
        parts.append("      >")
        parts.append(
            f"      <pdfxid:GTS_PDFXVersion>{self._esc(self.pdf_x_mode)}</pdfxid:GTS_PDFXVersion>"
        )
        if self.title:
            parts += [
                "      <dc:title><rdf:Alt>",
                '        <rdf:li xml:lang="x-default">'
                + self._esc(self.title)
                + "</rdf:li>",
                "      </rdf:Alt></dc:title>",
            ]
        if self.description:
            parts += [
                "      <dc:description><rdf:Alt>",
                '        <rdf:li xml:lang="x-default">'
                + self._esc(self.description)
                + "</rdf:li>",
                "      </rdf:Alt></dc:description>",
            ]
        if creators:
            parts.append("      <dc:creator><rdf:Seq>")
            for name in creators:
                parts.append(f"        <rdf:li>{self._esc(name)}</rdf:li>")
            parts.append("      </rdf:Seq></dc:creator>")
        parts += [
            "    </rdf:Description>",
            "  </rdf:RDF>",
            "</x:xmpmeta>",
        ]
        return "\n".join(parts)

    def build_xpacket(self) -> str:
        return (
            f'<?xpacket begin="{chr(0xFEFF)}" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
            f"{self.build_xmp()}\n"
            '<?xpacket end="w"?>\n'
        )

    def build_xpacket_bytes(self) -> bytes:
        return self.build_xpacket().encode("utf-8")
