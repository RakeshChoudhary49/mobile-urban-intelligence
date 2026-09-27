import cv2
import config

try:
    from paddleocr import PaddleOCR
    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False

class ANPREngine:
    def __init__(self):
        if HAS_PADDLEOCR:
            print("Initializing PaddleOCR for ANPR...")
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
        else:
            print("PaddleOCR not found. Using mock ANPR data.")
            self.ocr = None

    def read_plate(self, vehicle_crop):
        """
        Attempts to read license plate from a cropped vehicle image.
        Returns: {'plate_text': str, 'confidence': float} or None
        """
        if vehicle_crop is None or vehicle_crop.size == 0:
            return None

        if not HAS_PADDLEOCR:
            # Return mock data for demo if paddleocr is not installed
            return {'plate_text': 'RJ14CV1234', 'confidence': 0.85}

        # Grayscale the crop for better OCR
        gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
        
        # Simple contrast enhancement
        gray = cv2.equalizeHist(gray)

        result = self.ocr.ocr(gray, cls=True)
        
        if not result or not result[0]:
            return None

        best_text = ""
        best_conf = 0.0

        for line in result[0]:
            text = line[1][0]
            conf = line[1][1]
            
            text_alphanum = ''.join(e for e in text if e.isalnum())
            if len(text_alphanum) > 4 and conf > best_conf:
                best_text = text_alphanum
                best_conf = conf

        if best_conf > config.ANPR_CONF_THRESH:
            return {'plate_text': best_text, 'confidence': float(best_conf)}
        
        return None
