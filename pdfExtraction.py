import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import spacy

# Convert PDF to images (first 2 pages for simplicity)
pdf_path = "data/6824010_inventionoflitho00sene_bw.pdf"
pages = convert_from_path(pdf_path, dpi=300)[10:200]  # Limit to 2 pages

# OCR setup
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Update path if needed

# Extract text from each page
text_data = []
for i, page in enumerate(pages):
    text = pytesseract.image_to_string(page)
    text_data.append({"page_number": i+1, "text": text})

# Save raw text for reference
with open("pdf_raw_text.txt", "w", encoding="utf-8") as f:
    for entry in text_data:
        f.write(f"Page {entry['page_number']}:\n{entry['text']}\n\n")

# Load NLP model for entity extraction
nlp = spacy.load("en_core_web_sm")  # Ensure this model is installed: python -m spacy download en_core_web_sm

# Extract entities from text
entities = []
for entry in text_data:
    doc = nlp(entry["text"])
    for ent in doc.ents:
        entities.append({"entity": ent.text, "type": ent.label_, "value": ent.text, "page_number": entry["page_number"]})

# Filter for relevant types (e.g., GPE: locations, DATE: years)
filtered_entities = [e for e in entities if e["type"] in ["GPE", "DATE", "EVENT"]]

# Save to DataFrame and CSV
pdf_df = pd.DataFrame(filtered_entities)
pdf_df.to_csv("pdf_entities.csv", index=False)

print("PDF preprocessing complete. Entities saved to pdf_entities.csv")