import cv2
import pytesseract
import os
from PIL import Image

# Directory
data_dir = "data"
output_dir = "extracted_data"
os.makedirs(output_dir, exist_ok=True)

# Function to extract text from map
def extract_map_text(image_path):
    # Load image
    img = cv2.imread(image_path)
    # Convert to grayscale (improves OCR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply threshold to clean up (adjust as needed)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    # OCR
    text = pytesseract.image_to_string(thresh)
    return text

# Process maps
map_files = ["6824010.jpeg", "10800000.jpeg"]
map_data = {}

for map_file in map_files:
    map_path = os.path.join(data_dir, map_file)
    text = extract_map_text(map_path)
    map_data[map_file] = text
    # Save extracted text
    output_path = os.path.join(output_dir, f"{map_file}_text.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Extracted text from {map_file} saved to {output_path}")

# Print results
for map_file, text in map_data.items():
    print(f"\nText from {map_file}:\n{text[:200]}...")  # First 200 chars