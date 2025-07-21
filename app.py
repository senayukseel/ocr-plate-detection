from flask import Flask, render_template, request, jsonify
from ultralytics import YOLO
import numpy as np
import cv2
from PIL import Image
import io
import base64
import os

from utils.image_processing import crop_plate, preprocess_for_ocr
from utils.ocr import OCRReader

app = Flask(__name__)

# Modeli güvenli şekilde yükle
try:
    model_path = "models/best.pt"
    if os.path.exists(model_path):
        model = YOLO(model_path)
    else:
        print(f"Model dosyası bulunamadı: {model_path}")
        model = None
except Exception as e:
    print(f"Model yükleme hatası: {e}")
    model = None

# OCR okuyucuyu başlat
try:
    ocr_reader = OCRReader(lang_list=['tr', 'en'])
except Exception as e:
    print(f"OCR Reader başlatma hatası: {e}")
    ocr_reader = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'Lütfen bir resim yükleyin!'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi!'}), 400

    # Model kontrolü
    if model is None:
        return jsonify({'error': 'Model yüklenemedi!'}), 500

    # OCR kontrolü
    if ocr_reader is None:
        return jsonify({'error': 'OCR sistemi başlatılamadı!'}), 500

    try:
        # Görseli aç, RGB formatında numpy dizisine çevir
        image = Image.open(file.stream).convert('RGB')
        image_np = np.array(image)

        # Model ile tahmin yap
        results = model.predict(image_np, conf=0.5)

        if len(results[0].boxes) == 0:
            return jsonify({'error': 'Plaka bulunamadı!'}), 404

        # İlk bulunan kutuyu al (en yüksek güven skoru olabilir)
        box = results[0].boxes.xyxy[0].cpu().numpy().astype(int).tolist()

        # Plaka bölgesini kırp
        plate_img = crop_plate(image_np, box)

        # OCR için ön işlem
        plate_for_ocr = preprocess_for_ocr(plate_img)

        # OCR ile oku
        plate_text = ocr_reader.read_plate(plate_for_ocr)

        # Güven skoru
        confidence = float(results[0].boxes.conf[0].cpu().numpy() * 100)

        # Plaka kutusunu çizilmiş hali için base64 encode
        try:
            annotated_img = results[0].plot()
            _, buffer = cv2.imencode('.jpg', annotated_img)
            encoded_img = base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            print(f"Görsel encode hatası: {e}")
            # Hata durumunda orijinal görüntüyü encode et
            _, buffer = cv2.imencode('.jpg', image_np)
            encoded_img = base64.b64encode(buffer).decode('utf-8')

        # Sonucu JSON olarak dön
        return jsonify({
            'plate_text': plate_text,
            'confidence': round(confidence, 2),
            'annotated_image': f"data:image/jpeg;base64,{encoded_img}"
        })

    except Exception as e:
        print(f"Tahmin hatası: {e}")
        return jsonify({'error': f'İşlem sırasında hata oluştu: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
