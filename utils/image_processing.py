import cv2
import numpy as np
from PIL import Image

def crop_plate(image: np.ndarray, bbox: list) -> np.ndarray:
    # Görüntüden bounding box (bbox) ile belirtilen bölgeyi kırpar.
    try:
        if image is None or len(image.shape) < 2:
            raise ValueError("Geçersiz görüntü")
            
        x1, y1, x2, y2 = bbox
        # Sınırların görüntü boyutunu aşmaması için kontrol et
        height, width = image.shape[:2]

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(width, x2)
        y2 = min(height, y2)

        # Geçerli bir kırpma alanı var mı kontrol et
        if x2 <= x1 or y2 <= y1:
            raise ValueError("Geçersiz kırpma alanı")

        cropped_img = image[y1:y2, x1:x2]
        
        if cropped_img.size == 0:
            raise ValueError("Kırpılan görüntü boş")
            
        return cropped_img
        
    except Exception as e:
        print(f"Görüntü kırpma hatası: {e}")
        # Hata durumunda orijinal görüntüyü döndür
        return image

def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
    # OCR için görüntüyü ön işler (gri tonlama, eşikleme vb.).
    try:
        if image is None or len(image.shape) < 2:
            raise ValueError("Geçersiz görüntü")
            
        # BGR'den RGB'ye çevir (eğer 3 kanallıysa)
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
            
        # Görüntü boyutunu kontrol et
        if gray.shape[0] < 10 or gray.shape[1] < 10:
            # Çok küçük görüntüleri büyüt
            gray = cv2.resize(gray, (gray.shape[1]*2, gray.shape[0]*2), interpolation=cv2.INTER_CUBIC)
            
        # Basit bir thresholding ile kontrast artırma
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
        
    except Exception as e:
        print(f"Görüntü ön işleme hatası: {e}")
        # Hata durumunda orijinal görüntüyü döndür
        return image if image is not None else np.zeros((100, 100), dtype=np.uint8)
