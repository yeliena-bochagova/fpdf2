from xml.etree import ElementTree

import pytest

from fpdf import FPDF, XMPManager


def test_pdfx_xmp_generation_contains_identification_field():
    xmp = XMPManager().build_xmp()
    root = ElementTree.fromstring(xmp)

    ns = {
        "pdfxid": "http://www.npes.org/pdfx/ns/id/",
    }
    version_nodes = root.findall(".//pdfxid:GTS_PDFXVersion", ns)
    assert len(version_nodes) == 1
    assert version_nodes[0].text == "PDF/X-1a:2001"


def test_pdfx_xmp_generation_is_deterministic():
    manager = XMPManager(
        creator_tool="fpdf2-test",
        title="Deterministic title",
        description="Deterministic description",
        creator=("Alice", "Bob"),
        keywords=("foo", "bar"),
        producer="py-pdf/fpdf2",
    )

    first = manager.build_xmp()
    second = manager.build_xmp()
    assert first == second


def test_pdfx_xmp_rejects_unsupported_mode():
    with pytest.raises(ValueError, match="Unsupported PDF/X mode"):
        XMPManager(pdf_x_mode="PDF/X-4:2010")


def test_pdfx_xmp_escapes_xml_values():
    xmp = XMPManager(
        title="A < B & C",
        description='Quoted "text" and apostrophe \' demo',
        creator="Name & <tag>",
        keywords="a&b,<k>",
        producer='p"q',
    ).build_xmp()

    assert "A &lt; B &amp; C" in xmp
    assert "Quoted &quot;text&quot; and apostrophe &apos; demo" in xmp
    assert "Name &amp; &lt;tag&gt;" in xmp
    assert "a&amp;b,&lt;k&gt;" in xmp
    assert "p&quot;q" in xmp


def test_pdfx_xmp_can_be_inserted_via_existing_metadata_flow(tmp_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="pdfx xmp integration")
    pdf.set_pdfx_xmp_metadata()

    content = pdf.output()

    assert b"GTS_PDFXVersion" in content
    assert b"PDF/X-1a:2001" in content
    assert b"<?xpacket begin=" in content
