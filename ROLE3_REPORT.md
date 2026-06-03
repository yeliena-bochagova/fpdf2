# Role 3 Final Report: PDF/X Color and Transparency Compliance

## 1. Project Context

This work is part of the larger PDF/X-1a support effort in `fpdf2`.
My assigned role was Role 3: QA/DevOps Engineer. In this part of the
project, I focused on the first practical strict-mode checks for PDF/X color
and transparency behavior.

The work in this report does not complete full PDF/X-1a compliance. It adds a
focused validation layer for colors and transparency when PDF/X mode is enabled.

## 2. Role Responsibility and Research Plan Alignment

According to the research plan, Role 3 includes color management, compliance
validation, Strict Mode for colors, blocking RGB and transparency, and pytest
tests. My completed work directly covers the Strict Mode and pytest-testing
part of this plan.

The main goal was to prevent some PDF features that are not suitable for
PDF/X-1a print workflows. In this branch, the implemented checks reject RGB
colors and transparency-related settings when `pdf.pdf_x_mode = True`.

## 3. Completed Scope

The completed work includes:

- RGB color rejection in PDF/X mode.
- CMYK and grayscale color allowance in PDF/X mode.
- Alpha transparency rejection in colors.
- Rejection of `fill_opacity` below 1 in `local_context`.
- Rejection of `stroke_opacity` below 1 in `local_context`.
- Rejection of non-normal blend modes, for example `"Multiply"`.
- Preservation of normal non-PDF/X behavior.
- Pytest tests for the implemented color and transparency behavior.

## 4. Files Changed

### File: `fpdf/graphics_state.py`

This file manages the current graphics state of the PDF document. It stores
values such as draw color, fill color, and text color.

Changes made:

- Imported `FPDFException` so the code can raise a clear error when PDF/X
  color rules are violated.
- Added `_validate_pdfx_color()`.
- Connected the validation helper to `draw_color`, `fill_color`, and
  `text_color`.

### File: `fpdf/fpdf.py`

This file contains the main `FPDF` class. It handles many high-level PDF
operations, including `local_context()`.

Changes made:

- Imported `BlendMode`.
- Added PDF/X checks inside `_start_local_context()`.
- Rejected transparent fill and stroke opacity values in PDF/X mode.
- Rejected non-normal blend modes in PDF/X mode.

### File: `test/pdf_x/test_color_compliance.py`

This new test file checks color behavior in PDF/X mode.

Changes made:

- Added tests for RGB rejection.
- Added tests for grayscale and CMYK allowance.
- Added a test to confirm that regular non-PDF/X PDFs still allow RGB colors.

### File: `test/pdf_x/test_transparency_restrictions.py`

This new test file checks transparency restrictions in PDF/X mode.

Changes made:

- Added tests for alpha transparency in colors.
- Added tests for `fill_opacity` and `stroke_opacity`.
- Added tests for blend mode restrictions.
- Added a test confirming that fully opaque local context settings are allowed.

## 5. Implementation Details

The main color validation logic is in `_validate_pdfx_color()` in
`fpdf/graphics_state.py`.

When a color is set, the value is first converted into one of the internal
device color classes: `DeviceRGB`, `DeviceGray`, or `DeviceCMYK`. After that,
the validation helper checks the color only if `pdf_x_mode` is enabled.

If the color is `DeviceRGB`, the code raises an `FPDFException`. This is needed
because PDF/X-1a print workflows should use print-oriented color spaces instead
of RGB.

If the color is `DeviceGray` or `DeviceCMYK`, it is accepted. These color
spaces are suitable for the strict-mode behavior implemented in this branch.

The same helper also checks whether the color has alpha transparency. If the
alpha value is lower than 1, the code raises an `FPDFException`. This prevents
transparent colors from being used in PDF/X mode.

The opacity and blend mode checks are implemented in `_start_local_context()` in
`fpdf/fpdf.py`. This is the method used when code enters a block such as:

```python
with pdf.local_context(fill_opacity=0.5):
    ...
```

In PDF/X mode, `fill_opacity` and `stroke_opacity` must be fully opaque. The
implemented guard allows values such as `1` and `1.0`, but rejects values below
1.

The code also checks `blend_mode`. In this scope, only `blend_mode="Normal"` is
allowed. A non-normal blend mode such as `"Multiply"` is rejected because it
creates compositing behavior that is not suitable for this strict-mode PDF/X
layer.

Normal PDF behavior remains unchanged because all new checks are protected by
`pdf_x_mode`. If PDF/X mode is not enabled, RGB colors and normal transparency
features continue to work as before.

## 6. Test Coverage

### Test File: `test/pdf_x/test_color_compliance.py`

- `test_pdfx_rejects_rgb_fill_color` checks that RGB fill color is rejected in
  PDF/X mode.
- `test_pdfx_allows_grayscale_fill_color` checks that grayscale fill color is
  accepted in PDF/X mode.
- `test_pdfx_allows_cmyk_fill_color` checks that CMYK fill color is accepted in
  PDF/X mode.
- `test_regular_pdf_still_allows_rgb_colors` checks that normal PDFs still
  allow RGB colors when PDF/X mode is not enabled.

### Test File: `test/pdf_x/test_transparency_restrictions.py`

- `test_pdfx_rejects_alpha_gray_color` checks that grayscale colors with alpha
  transparency are rejected.
- `test_pdfx_rejects_alpha_cmyk_color` checks that CMYK colors with alpha
  transparency are rejected.
- `test_pdfx_rejects_local_context_fill_opacity` checks that transparent fill
  opacity is rejected in PDF/X mode.
- `test_pdfx_rejects_local_context_stroke_opacity` checks that transparent
  stroke opacity is rejected in PDF/X mode.
- `test_pdfx_rejects_non_normal_blend_mode` checks that a non-normal blend mode,
  such as `"Multiply"`, is rejected in PDF/X mode.
- `test_pdfx_allows_opaque_local_context` checks that fully opaque local context
  settings are still allowed.

These tests are important because they check both rejected and accepted
behavior. They also confirm that the new strict-mode rules do not change normal
PDF behavior.

## 7. Validation Results

The validation command used was:

```bash
pytest -o addopts= test/pdf_x/test_color_compliance.py test/pdf_x/test_transparency_restrictions.py -q
```

Result:

```text
10 passed, 1 warning
```

The warning is about `qpdf` not being available locally. It is not related to
the implemented PDF/X color or transparency logic.

## 8. Notes for Future Improvements

This strict-mode layer can later be extended with ICC and OutputIntent support,
image validation, VeraPDF validation, and CI/CD validation.

## 9. Commits

- `Add: Enforce PDF/X color compliance`
- `Add: Restrict PDF/X transparency`

## 10. Summary

My contribution implements the first practical Role 3 compliance layer for
PDF/X color and transparency validation. The branch now rejects RGB colors and
transparent settings in PDF/X mode, allows grayscale and CMYK colors, keeps
normal PDF behavior unchanged, and includes automated pytest coverage for the
implemented behavior.
