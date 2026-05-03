import pytest
from fpdf import FPDF
from fpdf.errors import FPDFException


def test_pdfx_blocks_core_font():
    """Verify that Helvetica (Core font) is blocked in PDF/X mode."""
    pdf = FPDF()
    pdf.pdf_x_mode = True

    # This should trigger your new FPDFException
    with pytest.raises(
        FPDFException, match="PDF/X mode requires all fonts to be embedded"
    ):
        pdf.set_font("helvetica", size=12)


def test_pdfx_allows_core_font_when_mode_off():
    """Verify that Helvetica is allowed if PDF/X mode is disabled."""
    pdf = FPDF()
    pdf.pdf_x_mode = False

    # This should work fine
    pdf.set_font("helvetica", size=12)
    assert pdf.font_family == "helvetica"


def test_pdfx_blocks_core_font_at_output_stage():
    """Verify that PDF/X mode prevents export if a core font was somehow included."""
    pdf = FPDF()
    pdf.pdf_x_mode = False

    pdf.add_page()

    pdf.set_font("helvetica", size=12)

    pdf.pdf_x_mode = True

    with pytest.raises(
        FPDFException, match="PDF/X export failed: font 'helvetica' is not embedded"
    ):
        pdf.output()
