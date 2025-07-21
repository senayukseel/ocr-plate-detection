import easyocr
import numpy as np

class OCRReader:
    def __init__(self, lang_list=None):
        if lang_list is None:
            lang_list = ['en']
        try:
            self.reader = easyocr.Reader(lang_list, gpu=False)
        except Exception as e:
            print(f"OCR Reader başlatılırken hata: {e}")
            self.reader = easyocr.Reader(['en'], gpu=False)

    def read_plate(self, image: np.ndarray) -> str:
        # OCR ile plaka üzerindeki metni okur.
        try:
            if image is None or image.size == 0:
                return "Görsel okunamadı"
                
            results = self.reader.readtext(image)
            
            if not results:
                return "Metin bulunamadı"
                
            # Sonuçlardan sadece yazıları alıp birleştiriyoruz
            plate_text = " ".join([res[1] for res in results if res[1].strip()])
            return plate_text.strip() if plate_text else "Metin okunamadı"
            
        except Exception as e:
            print(f"OCR okuma hatası: {e}")
            return "OCR hatası"
