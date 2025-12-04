import re
import pdfplumber
from PIL import Image
import io

class InputHandler:
    def parse_pdf(self, file_bytes):
        """
        Path A: Extracts Metadata AND renders the PDF as an image for analysis.
        """
        data = {
            "weight": None,
            "size": None,
            "diagnosis": "Normal",
            "image_bytes": None  # Changed from 'image' to 'image_bytes'
        }

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if not pdf.pages:
                return data
            
            first_page = pdf.pages[0]
            text = first_page.extract_text() or ""

            # --- 1. Regex Extraction (Metadata) ---
            # Weight
            weight_match = re.search(r"(?i)Poids\s*:\s*(\d+)", text)
            if weight_match:
                data["weight"] = float(weight_match.group(1))

            # Size
            size_match = re.search(r"(?i)Pointure\s*:\s*(\d+)", text)
            if size_match:
                data["size"] = int(size_match.group(1))

            # Diagnosis
            if "SUPINATION" in text.upper():
                data["diagnosis"] = "Supination"
            elif "PRONATION" in text.upper():
                data["diagnosis"] = "Pronation"

            # --- 2. Image Extraction (The Fix) ---
            # Instead of finding embedded objects, we render the whole page 
            # as an image. This guarantees we capture the visual heatmap.
            try:
                # Render page to PIL Image (resolution=150 is good balance)
                pil_image = first_page.to_image(resolution=150).original
                
                # Convert PIL to Bytes for the Vision Engine
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='PNG')
                data["image_bytes"] = img_byte_arr.getvalue()
            except Exception as e:
                print(f"Error rendering PDF image: {e}")

        return data

    def validate_inputs(self, weight, size):
        if not weight or not size:
            raise ValueError("Missing critical data")
        return float(weight), int(size)