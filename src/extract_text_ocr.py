from pathlib import Path
from pdf2image import convert_from_path
import pytesseract

# Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Poppler binary path (IMPORTANT)
POPPLER_PATH = r"C:\poppler-25.12.0\Library\bin"

pdf_path = Path("data/manuals/DSME_H4132.pdf")
output_path = Path("data/extracted_text/dsme_refrigeration.txt")

pages = convert_from_path(
    pdf_path,
    dpi=300,
    poppler_path=POPPLER_PATH
)

all_text = []

for i, page in enumerate(pages, start=1):
    text = pytesseract.image_to_string(page, lang="eng")
    if text.strip():
        all_text.append(f"\n--- Page {i} ---\n")
        all_text.append(text)

output_path.write_text("\n".join(all_text), encoding="utf-8")

print("STEP 1B complete: OCR text extraction finished.")
