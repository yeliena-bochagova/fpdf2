import pytest

from fpdf import FPDF
from fpdf.drawing_primitives import DeviceCMYK
from fpdf.errors import FPDFException


def test_pdfx_rejects_rgb_fill_color():
    pdf = FPDF()
    pdf.pdf_x_mode = True

    with pytest.raises(FPDFException, match="DeviceRGB is not allowed"):
        pdf.set_fill_color(255, 0, 0)


def test_pdfx_allows_grayscale_fill_color():
    pdf = FPDF()
    pdf.pdf_x_mode = True

    pdf.set_fill_color(128)

    assert pdf.fill_color is not None


def test_pdfx_allows_cmyk_fill_color():
    pdf = FPDF()
    pdf.pdf_x_mode = True

    pdf.set_fill_color(DeviceCMYK(0, 1, 1, 0))

    assert isinstance(pdf.fill_color, DeviceCMYK)


def test_regular_pdf_still_allows_rgb_colors():
    pdf = FPDF()

    pdf.set_fill_color(255, 0, 0)

    assert pdf.fill_color is not None
