# Implementing PDF/X-1a Industry Standard in fpdf2

## Project Overview
**Engineering Goal:** Extend the library's architecture to support the ISO 15930 (PDF/X-1a) standard, ensuring automatic validation (Compliance Enforcement) and color profile embedding. 
The project is divided into three main roles, 100 hours each. This ensures a formal distribution of responsibilities. The total estimated workload is 300 hours.

## Roles & Responsibilities

### Role 1: Lead Software Architect (100 Hours)
* **Focus:** Metadata, architectural design, and integration. Metaphorically, this role acts as the "Passport Office", ensuring the file officially "presents itself" as a PDF/X.
* **Tasks:**
    * Study ISO 15930/PDF-X-1a specifications and the existing `fpdf2` architecture.
    * Investigate XMP metadata structure to know which XML tags to write so professional equipment recognizes the PDF/X format.
    * Understand the PDF object model (Catalog/Info) and how internal data (dictionaries, keys) is recorded.
    * Implement the generation of the XMP block to identify PDF/X.
    * Update the `pdf.output` method to include a `pdf_x_mode` and refactor the FPDF constructor.
    * Design internal structure using UML Class Diagrams and create a comparative report "PDF vs PDF/X Architecture".
* **Useful Resources:**
    * [Adobe XMP Specification](https://www.adobe.com/products/xmp.html) (refer to the PDF section).
    * The `fpdf2` code repository, specifically the `syntax.py` file, which contains the "kitchen" of object creation.

### Role 2: Core Graphics Developer (100 Hours)
* **Focus:** Page geometry (Page Boxes) and font constraints. Metaphorically, this role is the "Geometer" with a ruler, ensuring nothing bleeds over the printing edges and all letters display correctly.
* **Tasks:**
    * Add support for Page Boxes (MediaBox, TrimBox, and BleedBox) with standard print margins in the `add_page` method.
    * Implement Font Embedding Checks to block standard PDF fonts from being used without embedding.
    * Understand how to check if a PDF "took" the font file with it, to prevent printing empty squares.
    * Develop a Sequence Diagram illustrating the page rendering process in PDF/X mode.
    * Write tests to verify that Page Boxes and font checks work properly.
* **Useful Resources:**
    * Articles covering the basics of typography regarding Bleed, Trim, and Media Box.
    * [fpdf2 Font Documentation](https://py-pdf.github.io/fpdf2/Fonts.html) to understand how fonts are added to the project.

### Role 3: QA/DevOps Engineer (100 Hours)
* **Focus:** Color management (ICC), validation, and CI/CD. Metaphorically, this is the "Colorist & Policeman" acting as a lie detector for the team and forbidding unprintable bright RGB colors.
* **Tasks:**
    * Learn how to attach ICC profiles (instruction files that tell printers how to mix inks) via `OutputIntents`.
    * Develop a "Strict Mode" to intercept and block RGB colors and transparency, allowing only CMYK or grayscale.
    * Learn to use VeraPDF, a free validation tool that determines if the file has errors or complies with the standard.
    * Write automated pytest tests to verify new features.
    * Set up a CI/CD Pipeline via GitHub Actions to automatically run tests and VeraPDF on every commit.
    * Monitor quality metrics like code coverage and PDF generation time.
* **Useful Resources:**
    * [VeraPDF Website](https://verapdf.org/) — download it and test any PDF file.
    * Search for a "CMYK vs RGB simple guide" to understand why printers hate RGB.

## The Main Resource for the Team
There is one primary source that the entire team must open at least once together:
* **PDF Reference (version 1.4 or 1.6):** This is a massive book, but you only need the specific chapters regarding OutputIntents and Page Boundaries. This is the primary source for everything.

## Engineering Components
* **1. Architectural Design (Design Phase):** Instead of immediately coding, the team creates documentation to prove a well-thought-out solution. This includes a UML Class Diagram showing how `XMPManager` and `ColorCompliance` interact with the FPDF core, and a Sequence Diagram mapping data flow to final byte writing.
* **2. Quality Assurance:** This includes code coverage metrics, generation time benchmarking, and VeraPDF integration. If the professional validator throws an error, the project is not considered finished.
* **3. Compliance Enforcement:** A key engineering task where methods like `set_draw_color`, `set_fill_color`, and `image` are modified. They must verify the color model (CMYK or Grayscale only), forbid alpha channels (transparency), and throw clear errors for users.

## Roadmap
| Phase | Tasks | Estimated Deadline |
| :--- | :--- | :--- |
| **Research & Design** | Creating UML diagrams, studying ISO, selecting ICC profiles. | Week 2 |
| **Prototype** | Implementing Page Boxes and basic metadata (without color logic). | Week 4 |
| **Core Dev** | Output Intents, embedding ICC, and color "Strict Mode". | Week 7 |
| **Automation** | Setting up the CI/CD pipeline with VeraPDF. | Week 8 |
| **Validation** | Fixing validator issues, Benchmarking. | Week 9 |
| **Final Docs** | Formatting the report, describing architectural decisions. | Week 10 |

## Risks & Mitigation
* **Font Complexity:** Font embedding is the most difficult part. Mitigation: Start by checking if `fpdf2` already embeds the chosen font; if not, output an error at initialization.
* **Version Incompatibility:** Different PDF/X versions have varying requirements. Mitigation: Strictly limit the scope to the PDF/X-1a:2001 standard only.

## Getting Started
It is recommended that each team member spends the first 5-10 hours on reverse engineering:
1. Find any valid PDF/X-1a file online.
2. Open it in a standard text editor like Notepad or Notepad++.
3. Search for the tags: `/GTS_PDFXVersion`, `/TrimBox`, and `/OutputIntents`.
4. This helps you visualize the "enemy" and understand that it is simply text you need to generate with your Python code.
