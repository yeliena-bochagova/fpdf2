# Final Report: PDF/X API and XMP Metadata Architecture

This report summarizes the Lead Software Architect contribution for GitHub issue #573,
"Support for PDF/X".

The work focused on creating the architectural foundation for PDF/X support in
`fpdf2`: public export API design, PDF/X identification XMP generation,
integration with the existing output flow, lifecycle safety, documentation, and
focused tests.

This work does not claim full PDF/X-1a compliance. It provides the first staged
layer that later compliance work can build on.

## Goals of the Project

PDF/X Export API Foundation - Define a simple, backward-compatible way for
users to request PDF/X export through `FPDF.output()`.

PDF/X-1a Mode Selection - Support a default PDF/X mode through `pdf_x=True` and
an explicit mode through `pdf_x_mode="PDF/X-1a:2001"`.

XMP Metadata Generation - Add a dedicated component that generates deterministic
PDF/X identification metadata.

Output Flow Integration - Connect PDF/X mode selection to the existing metadata
and serialization path without rewriting the PDF writer.

Mode Lifecycle Safety - Ensure that enabling PDF/X for one output call does not
leak PDF/X metadata into later normal output calls.

Architecture Documentation - Document the design, integration points,
responsibility boundaries, and future extension areas.

Focused Test Coverage - Add tests for XMP generation, API behavior, output
integration, unsupported modes, custom XMP handling, and no state leakage.

PR Readiness - Prepare a focused pull request description and reviewer checklist
so the work can be reviewed as an architecture and metadata foundation.

## Completed Goals from the 7-Week Plan

All major goals assigned to the Lead Software Architect role were completed.

Week 1 - Define Final PDF/X Export API

- Designed the public API for enabling PDF/X export:
  - `pdf.output("file.pdf", pdf_x=True)`
  - `pdf.output("file.pdf", pdf_x_mode="PDF/X-1a:2001")`
- Defined validation rules for unsupported and contradictory options.
- Documented that normal `pdf.output()` behavior must remain unchanged.
- Recorded future integration points for XMP, OutputIntents, validation, page
  boxes, color checks, and font checks.

Week 2 - Implement XMP Block Generator

- Added `XMPManager` in `fpdf/xmp.py`.
- Centralized PDF/X identification XMP generation in one component.
- Defined `PDF/X-1a:2001` as the default supported mode.
- Added validation so unsupported modes raise `ValueError`.
- Added XML escaping for metadata values.

Week 3 - Integrate XMP into Export Flow

- Connected `pdf.output(pdf_x=True)` to XMP generation.
- Reused the existing `set_xmp_metadata()` and `OutputProducer` metadata path.
- Added behavior for user-supplied XMP:
  - compatible PDF/X XMP is preserved;
  - custom XMP without PDF/X identification is rejected instead of being merged
    unsafely.

Week 4 - Design and Document Internal Structure

- Documented the internal architecture in `docs/pdfx_architecture.md`.
- Added UML and sequence diagrams.
- Defined responsibility boundaries between `FPDF`, `XMPManager`, and
  `OutputProducer`.
- Listed future extension points for the other project roles.

Week 5 - Support Export Mode Lifecycle

- Scoped PDF/X mode to the specific `output()` call.
- Prevented PDF/X metadata from remaining attached to the live `FPDF` instance
  after export.
- Added logic so repeated output calls remain deterministic while normal output
  stays normal.

Week 6 - Prepare Clean Commits for Transfer

- Organized the work into a clear commit stack.
- Kept the commits separated by responsibility: API design, XMP generation,
  output integration, documentation, lifecycle safety, tests, and PR materials.
- Verified that the feature remains focused and does not broaden into full
  compliance work.

Week 7 - Final Documentation and Review Preparation

- Finalized architecture documentation.
- Added `PULL_REQUEST.md` with a summary, test instructions, limitations, and a
  reviewer checklist.
- Clearly documented that full PDF/X-1a compliance is future work.

## Work Completed

### Public API

The implemented public API allows users to request PDF/X identification metadata
at export time.

Simple mode:

```python
pdf.output("file.pdf", pdf_x=True)
```

Explicit mode:

```python
pdf.output("file.pdf", pdf_x_mode="PDF/X-1a:2001")
```

Normal output remains unchanged:

```python
pdf.output("regular.pdf")
```

Contradictory input is rejected:

```python
pdf.output("file.pdf", pdf_x=False, pdf_x_mode="PDF/X-1a:2001")
```

This raises `ValueError` because the call both disables PDF/X and requests a
specific PDF/X mode.

### XMP Metadata Generation

The new `XMPManager` component generates deterministic XMP metadata containing
the PDF/X identification field:

```xml
<pdfxid:GTS_PDFXVersion>PDF/X-1a:2001</pdfxid:GTS_PDFXVersion>
```

The core PDF/X identification value is:

```text
pdfxid:GTS_PDFXVersion = PDF/X-1a:2001
```

This is the "identity marker" that tells PDF/X-aware tools which PDF/X standard
the file is declaring.

### Output Flow Integration

`FPDF.output()` now normalizes the PDF/X request before serialization.

The simplified flow is:

1. User calls `pdf.output(..., pdf_x=True)`.
2. `FPDF.output()` calls `_normalize_pdf_x_request(...)`.
3. `pdf_x=True` resolves to `PDF/X-1a:2001`.
4. A temporary output copy is prepared for serialization.
5. `_ensure_pdfx_xmp_metadata(...)` checks whether compatible XMP already
   exists.
6. If needed, `set_pdfx_xmp_metadata(...)` creates PDF/X XMP through
   `XMPManager`.
7. The existing metadata output flow serializes the XMP into the final PDF.

This design avoids duplicating the existing PDF metadata pipeline.

### Mode Lifecycle Safety

PDF/X mode is output-scoped. This means that a PDF/X export does not permanently
change the live `FPDF` object.

Example:

```python
pdf.output("pdfx.pdf", pdf_x=True)
pdf.output("normal.pdf")
```

The second output remains a normal PDF and does not accidentally include
`pdfxid:GTS_PDFXVersion`.

This behavior is important because the same `FPDF` object can be used for
multiple output calls during tests or application workflows.

### Custom XMP Behavior

The implementation handles custom XMP conservatively.

- If no XMP is set, PDF/X XMP is generated automatically.
- If custom XMP already contains the required PDF/X identification field, it is
  preserved.
- If custom XMP exists but does not contain the required PDF/X identification,
  `pdf.output(pdf_x=True)` raises `ValueError`.

This avoids unsafe XML merging and keeps the behavior predictable.

## Key Components Added

### `XMPManager`

Location: `fpdf/xmp.py`

Responsibilities:

- generate deterministic PDF/X identification XMP;
- expose the default mode `PDF/X-1a:2001`;
- validate supported PDF/X modes;
- escape XML values safely;
- provide helpers such as `build_xmp()`, `build_xpacket()`, and
  `build_xpacket_bytes()`.

`XMPManager` does not write PDF objects and does not perform full compliance
validation. Its scope is metadata generation only.

### `pdf_x` and `pdf_x_mode`

Location: `fpdf/fpdf.py`

Responsibilities:

- `pdf_x=True` enables the default PDF/X mode;
- `pdf_x_mode="PDF/X-1a:2001"` requests an explicit supported mode;
- unsupported modes raise `ValueError`;
- contradictory options raise `ValueError`.

### `FPDF.set_pdfx_xmp_metadata()`

Location: `fpdf/fpdf.py`

Responsibilities:

- create an `XMPManager`;
- generate PDF/X XMP;
- store the result through the existing `set_xmp_metadata()` method.

This keeps PDF/X metadata generation separate from low-level PDF serialization.

### Output Integration Helpers

Location: `fpdf/fpdf.py`

New internal responsibilities include:

- `_normalize_pdf_x_request(...)` - validates and normalizes PDF/X parameters;
- `_ensure_pdfx_xmp_metadata(...)` - ensures required PDF/X XMP is present;
- `_xmp_metadata_includes_pdfx_mode(...)` - checks whether existing XMP already
  includes the requested PDF/X mode;
- `_bufferize_output(...)` - serializes through a temporary copy when needed so
  PDF/X state does not leak into the live document.

## Architecture Overview

### UML Class Diagram

``` mermaid
classDiagram
      class FPDF {
         +output(..., pdf_x=None, pdf_x_mode=None)
         +set_xmp_metadata(xmp_metadata)
         +set_pdfx_xmp_metadata(...)
         +_normalize_pdf_x_request(pdf_x, pdf_x_mode)
         +_ensure_pdfx_xmp_metadata(pdf_x_mode)
         +_xmp_metadata_includes_pdfx_mode(pdf_x_mode)
         xmp_metadata: str | None
      }

      class XMPManager {
         +DEFAULT_PDFX_MODE
         +SUPPORTED_PDFX_MODES
         +build_xmp()
         +build_xpacket()
         +build_xpacket_bytes()
      }

      class OutputProducer {
         +bufferize()
         +_add_xmp_metadata()
      }

      class PDFXmpMetadata

      class PDFXComplianceValidator <<future>>
      class OutputIntentManager <<future>>
      class ColorCompliance <<future>>
      class FontCompliance <<future>>
      class PageBoxCompliance <<future>>

      FPDF --> XMPManager : creates PDF/X XMP
      FPDF --> OutputProducer : output_producer_class
      FPDF --> PDFXmpMetadata : stores inner XMP string
      OutputProducer --> PDFXmpMetadata : wraps xpacket for serialization
      FPDF ..> PDFXComplianceValidator : future validation hook
      OutputProducer ..> OutputIntentManager : future catalog/output-intent hook
      FPDF ..> ColorCompliance : future color checks
      FPDF ..> FontCompliance : future font checks
      FPDF ..> PageBoxCompliance : future page-box checks
```

### Sequence Diagram

``` mermaid
sequenceDiagram
      actor User
      participant FPDF
      participant XMPManager
      participant OutputProducer
      participant PDFXmpMetadata

      User->>FPDF: output(pdf_x=True)
      FPDF->>FPDF: _normalize_pdf_x_request(True, None)
      FPDF->>FPDF: resolve default mode PDF/X-1a:2001
      FPDF->>FPDF: _ensure_pdfx_xmp_metadata("PDF/X-1a:2001")

      alt no existing XMP metadata
            FPDF->>FPDF: set_pdfx_xmp_metadata(pdf_x_mode="PDF/X-1a:2001")
            FPDF->>XMPManager: __init__(pdf_x_mode="PDF/X-1a:2001", ...)
            XMPManager-->>FPDF: build_xmp() with pdfxid:GTS_PDFXVersion
            FPDF->>FPDF: set_xmp_metadata(xmp_metadata)
      else existing compatible PDF/X XMP
            FPDF-->>FPDF: reuse current xmp_metadata
      end

      FPDF->>OutputProducer: bufferize()
      OutputProducer->>OutputProducer: _add_xmp_metadata()
      OutputProducer->>PDFXmpMetadata: wrap xpacket + XML stream
      PDFXmpMetadata-->>OutputProducer: metadata object
      OutputProducer-->>User: PDF bytes
```

## Files Changed or Added

`docs/pdfx_architecture.md`

- Final architecture and project report.
- API design.
- diagrams.
- limitations.
- future work.
- reviewer instructions.

`mkdocs.yml`

- Documentation navigation entry for the PDF/X architecture page.

`fpdf/xmp.py`

- New `XMPManager` implementation.
- PDF/X XMP generation.
- supported-mode validation.
- XML escaping.

`fpdf/__init__.py`

- Exports `XMPManager` from the package API.

`fpdf/fpdf.py`

- Adds `pdf_x` and `pdf_x_mode` parameters to `FPDF.output()`.
- Adds request normalization and lifecycle handling.
- Adds `set_pdfx_xmp_metadata()`.
- Integrates PDF/X XMP generation into the existing output path.

`test/metadata/test_pdfx_xmp.py`

- Focused tests for XMP generation and PDF/X output behavior.

`PULL_REQUEST.md`

- PR summary.
- reviewer checklist.
- test instructions.
- limitations and future work.

## Key Commits

`1d90f9eb` - Add: Define PDF/X export API architecture

- Defined public API shape.
- Documented expected behavior and non-goals.
- Established backward compatibility requirements.

`d4a767a6` - Add: Generate PDF/X identification XMP metadata

- Added `XMPManager`.
- Generated the `pdfxid:GTS_PDFXVersion` field.
- Added initial tests for XMP generation.

`a1f808c5` - Add: Integrate PDF/X XMP metadata into output flow

- Connected `pdf.output(pdf_x=True)` to XMP generation.
- Reused the existing metadata serialization path.
- Added tests for automatic output insertion.

`0192f55a` - Add: Document PDF/X export architecture flow

- Added architecture diagrams.
- Documented integration points and responsibility boundaries.

`9cdd184c` - Add: Support PDF/X output mode lifecycle

- Prevented PDF/X metadata from leaking into later normal outputs.
- Added mode lifecycle behavior and tests.

`528f94c2` - Add: Strengthen PDF/X XMP output tests

- Expanded test documentation and coverage expectations.

`d62a1279` - Add: Finalize PDF/X architecture review documentation

- Completed the architecture review material.
- Clarified limitations and future work.

`2d295eb7` - Add: PR description and reviewer checklist for PDF/X architecture

- Added PR summary and review checklist.
- Listed local test command and known limitations.

## Tests Added or Strengthened

Primary test file:

```text
test/metadata/test_pdfx_xmp.py
```

Covered behavior:

- `XMPManager` output contains `GTS_PDFXVersion`;
- generated XMP contains `PDF/X-1a:2001`;
- generated XMP is deterministic;
- XML values are escaped correctly;
- unsupported PDF/X modes raise `ValueError`;
- `pdf.output(pdf_x=True)` inserts PDF/X XMP automatically;
- `pdf.output(pdf_x_mode="PDF/X-1a:2001")` works;
- normal `pdf.output()` does not include PDF/X metadata;
- `pdf_x=False` does not include PDF/X metadata;
- contradictory options are rejected;
- repeated output does not leak PDF/X state into later normal output;
- compatible custom PDF/X XMP is preserved;
- unsafe custom XMP merge is rejected.

Recommended local validation command:

```bash
pytest test/metadata/test_pdfx_xmp.py test/metadata/test_info.py test/test_output.py -q
```

Recorded local result in the PR notes:

```text
22 passed, 1 warning
```

The warning was related to `qpdf` not being available locally, not to the
PDF/X implementation itself.

## What Was Intentionally Not Implemented

The Lead Software Architect scope did not include full PDF/X-1a compliance.

The following items remain out of scope for this contribution:

- ICC profile embedding;
- OutputIntents;
- CMYK/RGB color validation;
- transparency restrictions;
- font embedding checks;
- TrimBox, BleedBox, and other page-box handling;
- image compliance checks;
- VeraPDF CI integration;
- full ISO 15930 conformance validation.

This is intentional. The goal of this role was to create the API, metadata, and
architecture foundation. The remaining items require graphics, color management,
font handling, page serialization, and CI validation work, which belong to later
phases or other project roles.

## Future Work

OutputIntents and ICC Profiles

- Add an `OutputIntentManager`.
- Embed the required ICC profile.
- Attach output intents to the PDF catalog.

Color Compliance

- Enforce CMYK or grayscale requirements for PDF/X-1a.
- Reject RGB colors in strict PDF/X mode.
- Reject transparency when it violates PDF/X-1a.

Font Compliance

- Ensure all fonts are embedded.
- Reject standard non-embedded fonts in PDF/X mode.
- Add user-friendly error messages for font compliance failures.

Page Boxes

- Add support for TrimBox, BleedBox, and related page boundaries.
- Integrate page-box values into page object serialization.

External Validation

- Add VeraPDF validation to tests or CI.
- Use external validation as the final proof of full PDF/X compliance.

Future PDF/X Modes

- Extend supported modes beyond `PDF/X-1a:2001` when the architecture is ready.
- Keep the existing `pdf_x_mode` API stable.

## Reviewer Checklist

- Confirm `XMPManager` generates `GTS_PDFXVersion`.
- Confirm the generated mode value is `PDF/X-1a:2001`.
- Confirm `pdf.output(pdf_x=True)` inserts PDF/X XMP.
- Confirm `pdf.output(pdf_x_mode="PDF/X-1a:2001")` works.
- Confirm unsupported modes raise `ValueError`.
- Confirm contradictory options raise `ValueError`.
- Confirm normal `pdf.output()` remains unchanged.
- Confirm PDF/X mode does not leak into later normal output calls.
- Confirm custom XMP behavior is conservative and predictable.
- Confirm the documentation does not claim full PDF/X-1a compliance.

## Summary of Contribution

The Lead Software Architect work created the first structured PDF/X support
layer in `fpdf2`. The contribution introduced an opt-in export API, a dedicated
`XMPManager`, automatic PDF/X identification metadata insertion, lifecycle-safe
output handling, focused tests, and final architecture documentation.

The most important user-facing result is that a document can now be exported
with PDF/X identification metadata using:

```python
pdf.output("file.pdf", pdf_x=True)
```

or:

```python
pdf.output("file.pdf", pdf_x_mode="PDF/X-1a:2001")
```

The implementation adds the required identification field:

```text
pdfxid:GTS_PDFXVersion = PDF/X-1a:2001
```

At the same time, the work carefully avoids claiming full PDF/X-1a compliance.
It leaves ICC profiles, OutputIntents, color validation, font checks, page
boxes, and VeraPDF validation for future work. The result is a clean,
reviewable, and extensible foundation for the next stages of PDF/X support.
