import cv2
import numpy as np
import pytesseract
from src.rules import PATTERNS
import re
import os

# Explicitly declare the path to tesseract.exe for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ImageSanitizer:
    @staticmethod
    def sanitize_image(image_bytes: bytes) -> bytes:
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("Invalid image file payload decoded as None.")

            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            n_boxes = len(ocr_data['text'])
            for i in range(n_boxes):
                word = ocr_data['text'][i].strip()
                if not word:
                    continue

                is_sensitive = False
                for secret_type, pattern in PATTERNS.items():
                    if re.search(pattern, word):
                        is_sensitive = True
                        break

                if is_sensitive:
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]

                    cv2.rectangle(img, (x - 2, y - 2), (x + w + 2, y + h + 2), (0, 0, 0), -1)

            success, encoded_image = cv2.imencode('.png', img)
            if not success:
                raise RuntimeError("Failed to encode processed image.")

            return encoded_image.tobytes()

        except Exception as e:
            print(f"[ERROR] ImageSanitizer failed: {str(e)}")
            raise e