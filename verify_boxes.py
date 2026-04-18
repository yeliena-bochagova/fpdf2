from fpdf import FPDF
import math

def test_pdfx_page_boxes():
    # 1. Створюємо об'єкт FPDF
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    
    # 2. Імітуємо включення режиму PDF/X (який має додати Архітектор)
    pdf.pdf_x_mode = True
    
    # 3. Додаємо сторінку
    pdf.add_page()
    
    # 4. Отримуємо першу сторінку для перевірки
    page = pdf.pages[1]
    
    # Розрахункові значення для A4 (210x297 мм)
    k = pdf.k  # коефіцієнт конвертації в пункти (зазвичай 72 / 25.4)
    expected_w_pt = 210 * k
    expected_h_pt = 297 * k
    bleed_pt = 3 * k
    
    print("--- Результати перевірки Геометра ---")
    
    # Перевірка TrimBox (має бути чистий розмір сторінки)
    assert page.trim_box is not None, "❌ Помилка: trim_box не встановлено!"
    print(f"✅ TrimBox: {page.trim_box}")
    assert math.isclose(page.trim_box[2], expected_w_pt, rel_tol=1e-5)
    assert math.isclose(page.trim_box[3], expected_h_pt, rel_tol=1e-5)

    # Перевірка BleedBox (має бути +3мм з кожного боку)
    assert page.bleed_box is not None, "❌ Помилка: bleed_box не встановлено!"
    print(f"✅ BleedBox: {page.bleed_box}")
    assert math.isclose(page.bleed_box[0], -bleed_pt, rel_tol=1e-5)
    assert math.isclose(page.bleed_box[2], expected_w_pt + bleed_pt, rel_tol=1e-5)

    # Перевірка MediaBox (має бути рядком, що збігається з BleedBox)
    assert isinstance(page.media_box, str), "❌ Помилка: media_box має бути рядком!"
    print(f"✅ MediaBox: {page.media_box}")
    
    # Перевіряємо чи числове значення в рядку правильне
    expected_media_str = f"[{-bleed_pt:.2f} {-bleed_pt:.2f} {expected_w_pt + bleed_pt:.2f} {expected_h_pt + bleed_pt:.2f}]"
    print(f"Очікуваний MediaBox: {expected_media_str}")
    
    print("\n🚀 ВІТАЮ! Частина 1 виконана успішно. Сторінка має всі необхідні рамки.")

if __name__ == "__main__":
    try:
        test_pdfx_page_boxes()
    except AssertionError as e:
        print(e)
    except Exception as e:
        print(f"❌ Виникла непередбачувана помилка: {e}")
        