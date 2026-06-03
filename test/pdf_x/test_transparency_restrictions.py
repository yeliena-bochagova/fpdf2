import pytest

from fpdf import FPDF
from fpdf.drawing_primitives import DeviceCMYK, DeviceGray
from fpdf.errors import FPDFException


def test_pdfx_rejects_alpha_gray_color():
    pdf = FPDF()
    pdf.pdf_x_mode = True

    with pytest.raises(FPDFException, match="does not allow transparency"):
        pdf.set_fill_color(DeviceGray(0.5, a=0.5))


def test_pdfx_rejects_alpha_cmyk_color():
    pdf = FPDF()
    pdf.pdf_x_mode = True

    with pytest.raises(FPDFException, match="does not allow transparency"):
        pdf.set_fill_color(DeviceCMYK(0, 1, 1, 0, a=0.5))


def test_pdfx_rejects_local_context_fill_opacity():
    pdf = FPDF()
    pdf.pdf_x_mode = True
    pdf.add_page()

    with pytest.raises(FPDFException, match="does not allow transparency"):
        with pdf.local_context(fill_opacity=0.5):
            pass


def test_pdfx_rejects_local_context_stroke_opacity():
    pdf = FPDF()
    pdf.pdf_x_mode = True
    pdf.add_page()

    with pytest.raises(FPDFException, match="does not allow transparency"):
        with pdf.local_context(stroke_opacity=0.5):
            pass


def test_pdfx_rejects_non_normal_blend_mode():
    pdf = FPDF()
    pdf.pdf_x_mode = True
    pdf.add_page()

    with pytest.raises(FPDFException, match="Normal blend mode"):
        with pdf.local_context(blend_mode="Multiply"):
            pass


def test_pdfx_allows_opaque_local_context():
    pdf = FPDF()
    pdf.pdf_x_mode = True
    pdf.add_page()

    with pdf.local_context(fill_opacity=1, stroke_opacity=1, blend_mode="Normal"):
        pdf.rect(10, 10, 20, 20)
