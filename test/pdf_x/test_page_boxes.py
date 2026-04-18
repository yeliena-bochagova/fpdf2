import pytest
import math
from fpdf import FPDF

# Testing different page formats to ensure geometric math is consistent
@pytest.mark.parametrize("page_format, width_mm, height_mm", [
    ("A4", 210.0, 297.0),
    ("A3", 297.0, 420.0),
    ("A5", 148.0, 210.0),
    ("Letter", 215.9, 279.4),
])
def test_pdfx_page_boxes_dimensions(page_format: str, width_mm: float, height_mm: float) -> None:
    """Verify MediaBox, TrimBox, and BleedBox values for various page sizes."""
    pdf = FPDF(format=page_format)

    pdf.pdf_x_mode = True 
    pdf.add_page()
    
    page = pdf.pages[1]
    k: float = pdf.k
    bleed_pt: float = 3.0 * k # Standard 3mm bleed for PDF/X
    
    expected_w_pt: float = width_mm * k
    expected_h_pt: float = height_mm * k

    # 1. Validate TrimBox (Finished page size)
    assert page.trim_box is not None
    assert math.isclose(page.trim_box[2], expected_w_pt, rel_tol=1e-3)
    assert math.isclose(page.trim_box[3], expected_h_pt, rel_tol=1e-3)

    # 2. Validate BleedBox (Size including bleed area)
    assert page.bleed_box is not None
    assert math.isclose(page.bleed_box[0], -bleed_pt, rel_tol=1e-3)
    assert math.isclose(page.bleed_box[2], expected_w_pt + bleed_pt, rel_tol=1e-3)

    # 3. Validate MediaBox (Physical medium size)
    assert isinstance(page.media_box, str)
    
    actual_values = [float(x) for x in page.media_box.strip("[]").split()]
    expected_values = [-bleed_pt, -bleed_pt, expected_w_pt + bleed_pt, expected_h_pt + bleed_pt]

    # Compare each coordinate with a small tolerance (0.02 points)
    for actual, expected in zip(actual_values, expected_values):
        assert math.isclose(actual, expected, abs_tol=0.02), f"Value {actual} deviates too much from {expected}"