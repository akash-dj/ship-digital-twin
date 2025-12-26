import pdfplumber
from pathlib import Path

pdf_path = Path("data/manuals/DSME_H4132.pdf")

with pdfplumber.open(pdf_path) as pdf:
    print("Total pages:", len(pdf.pages))

    for i, page in enumerate(pdf.pages[:5], start=1):
        text = page.extract_text()
        print(f"\n--- Page {i} text length ---")
        print(0 if text is None else len(text))
