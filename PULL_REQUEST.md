# Add PDF/X API and XMP metadata architecture foundation

## Summary

This PR introduces the architectural foundation for PDF/X-1a support in `fpdf2`, focused on the Lead Software Architect scope: public API design, XMP metadata generation, output-flow integration, mode lifecycle handling, and final architecture documentation.

The implementation does **not** claim full PDF/X-1a compliance yet. It adds PDF/X identification metadata support and prepares the internal architecture for later compliance work.

## Related issue

Supports initial work toward:

- #573 — Support for PDF/X

## Implemented scope

### Public API

This PR introduces support for requesting PDF/X metadata generation through:

```python
pdf.output("file.pdf", pdf_x=True)

# and explicit mode selection:

pdf.output("file.pdf", pdf_x_mode="PDF/X-1a:2001")
```

Current supported mode:

- `PDF/X-1a:2001`

Unsupported modes raise `ValueError`.

Contradictory options such as:

```python
pdf.output("file.pdf", pdf_x=False, pdf_x_mode="PDF/X-1a:2001")
```

also raise `ValueError`.

### XMP metadata generation

Added `XMPManager`, which generates deterministic XMP metadata containing the PDF/X identification field:

- `pdfxid:GTS_PDFXVersion`
- `PDF/X-1a:2001`

The generated metadata is parseable XML and includes the required namespaces for the implemented XMP structure.

### Output-flow integration

`pdf.output(pdf_x=True)` now automatically inserts PDF/X identification XMP through the existing metadata/output flow.

The implementation preserves normal output behavior when PDF/X mode is not requested.

### Mode lifecycle

PDF/X mode is scoped to the requested output call.

This avoids state leakage, for example:

```python
pdf.output("pdfx.pdf", pdf_x=True)
pdf.output("normal.pdf")
```

The second output remains normal and does not accidentally retain PDF/X XMP metadata.

### Custom XMP behavior

- If user-supplied XMP already contains the required PDF/X identification field, it is preserved.
- If custom XMP does not contain the required PDF/X identification field, `pdf.output(pdf_x=True)` raises instead of trying to merge XML unsafely.

### Documentation

Added and updated `docs/pdfx_architecture.md` with:

- API design
- XMP architecture
- output-flow integration
- Mermaid UML class diagram
- Mermaid sequence diagram
- integration points
- responsibility boundaries
- mode lifecycle explanation
- testing summary
- final architecture report
- reviewer checklist
- PR/review instructions
- current limitations and future work

### Tests

Added or updated tests covering:

- `XMPManager` generation
- parseable XMP XML
- presence of `pdfxid:GTS_PDFXVersion`
- presence of `PDF/X-1a:2001`
- `pdf.output(pdf_x=True)` automatic XMP insertion
- `pdf.output(pdf_x_mode="PDF/X-1a:2001")`
- unsupported mode rejection
- contradictory mode option rejection
- normal output without PDF/X metadata
- `pdf_x=False` behavior
- repeated output stability
- no PDF/X metadata leakage into later normal outputs
- compatible/incompatible custom XMP behavior

### Validation run locally

Run:

```bash
pytest test/metadata/test_pdfx_xmp.py test/metadata/test_info.py test/test_output.py -q
```

Result: `22 passed, 1 warning` (the warning is related to `qpdf` not being available locally).

Pre-commit was also run on changed documentation/code files during the weekly commits.

## Commit stack

Recommended review/cherry-pick order:

1. `1d90f9eb` Add: Define PDF/X export API architecture
2. `d4a767a6` Add: Generate PDF/X identification XMP metadata
3. `a1f808c5` Add: Integrate PDF/X XMP metadata into output flow
4. `0192f55a` Add: Document PDF/X export architecture flow
5. `9cdd184c` Add: Support PDF/X output mode lifecycle
6. `528f94c2` Add: Strengthen PDF/X XMP output tests
7. `d62a1279` Add: Finalize PDF/X architecture review documentation

## Reviewer checklist

- Check that the public API design is consistent with existing `fpdf2` style.
- Review `XMPManager` output and XML escaping.
- Confirm `pdf.output(pdf_x=True)` inserts PDF/X identification XMP.
- Confirm `pdf.output(pdf_x_mode="PDF/X-1a:2001")` works.
- Confirm unsupported and contradictory modes raise clear `ValueError`.
- Confirm PDF/X mode does not leak into later normal outputs.
- Review custom XMP behavior.
- Review `docs/pdfx_architecture.md` diagrams and integration points.
- Confirm the PR does not claim full PDF/X-1a compliance.

## Current limitations

This PR does not implement full PDF/X-1a compliance. The following remain future work:

- ICC profile embedding
- OutputIntents
- CMYK/RGB color validation
- transparency restrictions
- font embedding checks
- TrimBox/BleedBox/page-box logic
- image compliance checks
- VeraPDF validation
- full ISO 15930 conformance testing

## Notes

This PR should be reviewed as a metadata/API architecture foundation for PDF/X support, not as a complete PDF/X-1a implementation.


Suggested short GitHub title:

```
Add PDF/X API and XMP metadata architecture foundation
```

Or more formal:

```
Add initial PDF/X-1a XMP metadata support and architecture docs
```
