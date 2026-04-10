import os
from fpdf import FPDF

OUTPUT_PDF_PATH = os.path.join(os.path.dirname(__file__), "pdfx_compliant_sample.pdf")


def generate_pdfx_document():
    pdf = FPDF()
    pdf.pdf_x_mode = True
    pdf.add_page()

    font_path = os.path.join(os.path.dirname(__file__), "fonts", "Roboto-Regular.ttf")
    pdf.add_font("Roboto", "", font_path)
    pdf.set_font("Roboto", size=14)

    pdf.cell(
        w=0,
        h=10,
        text="PDF/X Compliance Test Document",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )
    pdf.ln(10)
    pdf.set_font("Roboto", size=12)
    pdf.multi_cell(
        w=0,
        h=8,
        text="This document verifies that fpdf2 successfully enforces PDF/X standards:\n"
        "- Page Boxes (MediaBox, TrimBox, BleedBox) are correctly defined.\n"
        "- All core fonts are blocked, and only embedded TrueType fonts are allowed.",
    )

    pdf.output(OUTPUT_PDF_PATH)
    print(f" [Success] Test PDF/X document generated at: {OUTPUT_PDF_PATH}")


if __name__ == "__main__":
    generate_pdfx_document()

    if os.path.exists(OUTPUT_PDF_PATH):
        with open(OUTPUT_PDF_PATH, "rb") as f:
            pdf_bytes = f.read()

        print("\n Final check")

        font_embedded = b"MPDFAA+" in pdf_bytes

        checks = {
            "Marker version GTS_PDFXVersion": b"GTS_PDFXVersion" in pdf_bytes,
            "Vocabulary OutputIntent": b"OutputIntent" in pdf_bytes,
            "Namespace http://ns.adobe.com/pdfx/": b"http://ns.adobe.com/pdfx/"
            in pdf_bytes,
            "Imbedded font subset (MPDFAA+)": font_embedded,
        }

        all_passed = True
        for name, passed in checks.items():
            status = "FOUND" if passed else "NOT FOUND"
            if not passed:
                all_passed = False
            print(f"{name}: {status}")

        if all_passed:
            print("Structure is ready")
        else:
            print("Something is missing.")
    else:
        print(f"Error: Generated file not found at {OUTPUT_PDF_PATH}")
