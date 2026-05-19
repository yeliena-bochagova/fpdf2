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


def test_pdfx_xmp_can_be_inserted_via_existing_metadata_flow():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="pdfx xmp integration")
    pdf.set_pdfx_xmp_metadata()

    content = pdf.output()

    assert b"GTS_PDFXVersion" in content
    assert b"PDF/X-1a:2001" in content
    assert b"<?xpacket begin=" in content


def test_pdfx_output_auto_inserts_xmp_metadata():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="PDF/X XMP integration test")

    content = pdf.output(pdf_x=True)

    assert content.startswith(b"%PDF")
    assert b"<?xpacket begin=" in content
    assert b"pdfxid:GTS_PDFXVersion" in content
    assert b"PDF/X-1a:2001" in content


def test_pdfx_output_supports_explicit_mode():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="PDF/X explicit mode test")

    content = pdf.output(pdf_x_mode="PDF/X-1a:2001")

    assert b"pdfxid:GTS_PDFXVersion" in content
    assert b"PDF/X-1a:2001" in content


@pytest.mark.parametrize("kwargs", [{}, {"pdf_x": False}])
def test_pdfx_output_without_pdfx_options_remains_normal(kwargs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="normal output test")

    content = pdf.output(**kwargs)

    assert b"pdfxid:GTS_PDFXVersion" not in content
    assert b"PDF/X-1a:2001" not in content


def test_pdfx_output_mode_toggle_does_not_leak_state():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="mode toggle test")

    normal_content = pdf.output()
    assert b"pdfxid:GTS_PDFXVersion" not in normal_content
    assert pdf.xmp_metadata is None

    pdfx_content = pdf.output(pdf_x=True)
    assert b"pdfxid:GTS_PDFXVersion" in pdfx_content
    assert b"PDF/X-1a:2001" in pdfx_content
    assert pdf.xmp_metadata is None

    normal_again = pdf.output()
    assert b"pdfxid:GTS_PDFXVersion" not in normal_again
    assert b"PDF/X-1a:2001" not in normal_again
    assert normal_again != pdfx_content

    pdfx_again = pdf.output(pdf_x_mode="PDF/X-1a:2001")
    assert pdfx_again == pdfx_content


def test_pdfx_output_rejects_unsupported_mode():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="unsupported mode")

    with pytest.raises(ValueError, match="Unsupported PDF/X mode"):
        pdf.output(pdf_x_mode="PDF/X-4:2010")


def test_pdfx_output_rejects_conflicting_pdfx_request():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="conflicting request")

    with pytest.raises(ValueError, match="cannot be combined"):
        pdf.output(pdf_x=False, pdf_x_mode="PDF/X-1a:2001")


def test_pdfx_output_preserves_existing_pdfx_xmp():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="preexisting pdfx xmp")
    pdf.set_xmp_metadata("""<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="fpdf2">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description xmlns:pdfxid="http://www.npes.org/pdfx/ns/id/" rdf:about="">
            <pdfxid:GTS_PDFXVersion>PDF/X-1a:2001</pdfxid:GTS_PDFXVersion>
        </rdf:Description>
    </rdf:RDF>
</x:xmpmeta>""")

    content = pdf.output(pdf_x=True)

    assert b"pdfxid:GTS_PDFXVersion" in content
    assert b"PDF/X-1a:2001" in content


def test_pdfx_output_rejects_unsafe_custom_xmp_merge():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="unsafe custom xmp")
    pdf.set_xmp_metadata("""<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="fpdf2">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description rdf:about="">
            <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">
                <rdf:Alt>
                    <rdf:li xml:lang="x-default">custom</rdf:li>
                </rdf:Alt>
            </dc:title>
        </rdf:Description>
    </rdf:RDF>
</x:xmpmeta>""")

    with pytest.raises(ValueError, match="cannot be safely merged"):
        pdf.output(pdf_x=True)
