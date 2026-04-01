# Implementing PDF/X-1a Industry Standard in fpdf2

**Мова:** [Українська](README.uk.md) · **English** (this file)

# Commit & Repository Rules (for `pdfx-support` workflow)

## 1. Branching and where to push
- **Each team member works in their own branch** named:  
  `pdfx-support-<your-role>` (example: `pdfx-support-qa`).
- **Weekly deliverables** (finished work for the week) are pushed **only** to the shared integration branch **`pdfx-support`**.
- **`main` is reserved** for syncing with the upstream parent repository only. Do **not** push feature work directly to `main`.

## 2. What NOT to do (professional warning)
- **Do not run `git add .` and push everything** from your working tree. This was a past source of noise and accidental uploads of unrelated files.  
  - Unstaged, unrelated, or large files must **not** be included in weekly pushes.
  - If you accidentally staged unrelated files, **unstage** them before committing (see commands below).
- **Do not commit secrets, large binaries, or generated artifacts**. Use `.gitignore` or `.git/info/exclude`

## 3. Commit message rules (mandatory)
- **Language:** English only.
- **Format:** Start with a **capitalized verb** describing the action. The first word must be a verb such as `Add`, `Fix`, `Update`, `Remove`, `Refactor`, `Docs`, `Test`, `Chore`.  
  - **Structure:** `Verb(scope): short description` or `Verb: short description`  
  - **Examples:**  
    - `Add: PageBoxes support for add_page`  
    - `Fix: font embedding check for TrueType fonts`  
    - `Update: pdf.output to accept pdf_x=True`  
    - `Docs: add WorkPlan and contribution rules`
- **One logical change per commit.** Avoid mixing unrelated fixes in a single commit.

## 4. Staging and committing workflow (recommended commands)
- **Stage interactively** to avoid `git add .` mistakes:
  ```bash
  git add -p            # interactively choose hunks
  git add <file>        # add specific file(s)
  ```
- **Unstage or remove accidental files:**
  ```bash
  git restore --staged path/to/file   # unstage a file
  git rm --cached path/to/file        # stop tracking a file but keep it locally
  ```
- **Amend or squash before pushing** to keep history clean:
  ```bash
  git commit --amend --no-edit
  git rebase -i HEAD~N
  ```
- **Before pushing**, run:
  ```bash
  git status
  git diff --staged --name-only
  ```

## 5. Pull request and review rules
- **PR target:** personal branch → `pdfx-support`. Do not PR directly to `main`.
- **CI must pass** (tests + linters + pre-commit) before requesting review.
- **Keep PRs focused**: one feature/bugfix per PR. Large features can be split into multiple PRs.

## 6. Tests, linters and pre-commit
- **Run tests locally** before pushing: `pytest` (or the project test command).
- **Install and use pre-commit hooks** (if configured):  
  ```bash
  pip install pre-commit
  pre-commit install
  pre-commit run --all-files
  ```
- Fix linter/formatter issues locally; do not rely on CI to fix code style.

## 7. Files and artifacts
- **Do not commit generated files** (build artifacts, `.pyc`, virtual envs, large PDFs) — add them to `.gitignore` or `.git/info/exclude`.
- **If a generated file was accidentally committed**, remove it from history or at least from the index and commit the removal:
  ```bash
  git rm --cached path/to/generated.file
  git commit -m "Chore: remove generated artifact from repo"
  ```

## 8. Example checklist before pushing to `pdfx-support`
- [ ] I worked in `pdfx-support-<my-name>` branch.
- [ ] I staged only relevant files (`git add -p` used).
- [ ] Commit messages are in English, start with a capitalized verb, and describe the object changed.
- [ ] All tests pass locally.
- [ ] Pre-commit hooks and linters pass.
- [ ] No secrets or large binaries are included.
- [ ] PR description explains how to test and what changed.

---

**Summary (one-line):** Work in your personal `pdfx-support-<name>` branch, push weekly deliverables only to `pdfx-support`, never `git add .` blindly, write English commit messages starting with a capitalized verb (e.g., `Add:`, `Fix:`), run tests and pre-commit locally, and open focused PRs for review.

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
