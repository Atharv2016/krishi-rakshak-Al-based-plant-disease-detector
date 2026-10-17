from pathlib import Path
import json, os
import numpy as np
from PIL import Image, UnidentifiedImageError
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = Path(os.getenv('KRISHI_MODEL_PATH', ROOT / 'model' / 'plant_disease_model.keras'))
CLASSES_PATH = Path(os.getenv('KRISHI_CLASS_NAMES_PATH', ROOT / 'model' / 'class_names.json'))
SIZE = 224
app = Flask(__name__, static_folder=str(ROOT / 'frontend'), static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
CORS(app, resources={r'/api/*': {'origins': os.getenv('KRISHI_ALLOWED_ORIGINS', '*').split(',')}})
model = None
classes = None
load_error = None

INFO = {
 'Tomato___Early_blight': {
  'en': ['Tomato — Early blight', 'Older leaves may develop brown spots with concentric rings and yellowing.', 'Avoid prolonged leaf wetness, improve airflow, remove affected debris where appropriate, and ask a local agricultural expert to confirm the diagnosis.'],
  'mr': ['टोमॅटो — अर्ली ब्लाइट (लवकर येणारा करपा)', 'जुन्या पानांवर गोलाकार तपकिरी डाग आणि पिवळेपणा दिसू शकतो.', 'पानांवर जास्त वेळ ओलावा राहू देऊ नका, हवा खेळती ठेवा आणि निदानासाठी स्थानिक कृषी तज्ज्ञांचा सल्ला घ्या.']},
 'Tomato___Late_blight': {
  'en': ['Tomato — Late blight', 'Dark, water-soaked-looking lesions may spread quickly in cool, wet conditions.', 'Inspect nearby plants, reduce leaf wetness and promptly contact an agricultural expert.'],
  'mr': ['टोमॅटो — लेट ब्लाइट (उशिराचा करपा)', 'थंड व दमट हवेत पाणचट दिसणारे काळसर डाग वेगाने पसरू शकतात.', 'जवळच्या झाडांची तपासणी करा, पानांवरील ओलावा कमी ठेवा आणि कृषी तज्ज्ञांशी संपर्क साधा.']},
 'Potato___Early_blight': {
  'en': ['Potato — Early blight', 'Brown leaf spots, sometimes with target-like rings, may occur on older leaves.', 'Remove infected debris where appropriate and verify the diagnosis with an agricultural expert.'],
  'mr': ['बटाटा — अर्ली ब्लाइट', 'जुन्या पानांवर वलयांसारखे तपकिरी डाग दिसू शकतात.', 'बाधित अवशेष योग्य पद्धतीने काढा आणि कृषी तज्ज्ञांकडून निदानाची खात्री करा.']},
 'Potato___Late_blight': {
  'en': ['Potato — Late blight', 'Dark, water-soaked lesions can enlarge rapidly; tubers may also be affected.', 'Check the crop promptly and seek local agricultural advice. Do not base treatment on this prediction alone.'],
  'mr': ['बटाटा — लेट ब्लाइट', 'काळसर, पाणचट डाग झपाट्याने वाढू शकतात; बटाट्यांनाही बाधा होऊ शकते.', 'पिकाची त्वरित तपासणी करा आणि कृषी सल्ला घ्या. केवळ या अंदाजावर उपचार ठरवू नका.']},
 'Grape___Black_rot': {
  'en': ['Grape — Black rot', 'Brown leaf lesions and dark, shriveled berries can be associated with black rot.', 'Remove affected plant material where appropriate and seek confirmation from a local viticulture expert.'],
  'mr': ['द्राक्ष — ब्लॅक रॉट (काळी कुज)', 'पानांवर तपकिरी डाग आणि काळी पडून आकसलेली द्राक्षे दिसू शकतात.', 'योग्य पद्धतीने बाधित भाग काढा आणि स्थानिक द्राक्षतज्ज्ञांचा सल्ला घ्या.']}
}

def ensure_model():
 global model, classes, load_error
 if model is not None: return True
 if load_error: return False
 if not MODEL_PATH.exists() or not CLASSES_PATH.exists():
  load_error = 'Model files are missing. Train the model first; see README.md.'
  return False
 try:
  import tensorflow as tf
  model = tf.keras.models.load_model(MODEL_PATH)
  classes = json.loads(CLASSES_PATH.read_text(encoding='utf-8'))
  if not isinstance(classes, list) or not classes: raise ValueError('class_names.json must contain a non-empty list')
  return True
 except Exception as exc:
  load_error = f'Could not load model: {exc}'
  return False

def info_for(class_name, lang):
 if class_name in INFO:
  title, symptoms, advice = INFO[class_name].get(lang, INFO[class_name]['en'])
 else:
  parts = class_name.split('___', 1)
  crop = parts[0].replace('_', ' ')
  disease = parts[1].replace('_', ' ').replace('(', '').replace(')', '') if len(parts) > 1 else class_name
  healthy = 'healthy' in disease.lower()
  if lang == 'mr':
   title = f'{crop} — {"निरोगी" if healthy else disease}'
   symptoms = 'निरोगी वर्गात वर्गीकृत.' if healthy else 'या वर्गासाठी विशिष्ट माहिती उपलब्ध नाही.'
   advice = 'पिकाचे नियमित निरीक्षण करा. शंका असल्यास स्थानिक कृषी तज्ज्ञांचा सल्ला घ्या.'
  else:
   title = f'{crop} — {disease}'
   symptoms = 'Classified as healthy.' if healthy else 'Specific information for this class is not configured.'
   advice = 'Monitor the crop and consult a local agricultural expert if symptoms persist.'
 return {'title': title, 'symptoms': symptoms, 'advice': advice}

@app.get('/')
def home(): return send_from_directory(app.static_folder, 'index.html')

@app.get('/api/health')
def health():
 ready = ensure_model()
 return jsonify({'status': 'ok', 'model_ready': ready, 'model_message': None if ready else load_error})

@app.post('/api/predict')
def predict():
 if 'image' not in request.files: return jsonify({'error': "Upload an image using the 'image' field."}), 400
 upload = request.files['image']
 if not upload.filename: return jsonify({'error': 'Choose an image file first.'}), 400
 if Path(upload.filename).suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
  return jsonify({'error': 'Unsupported file type. Use JPG, PNG, or WEBP.'}), 400
 if not ensure_model(): return jsonify({'error': load_error, 'code': 'MODEL_NOT_READY'}), 503
 try:
  image = Image.open(upload.stream); image.verify(); upload.stream.seek(0)
  image = Image.open(upload.stream).convert('RGB').resize((SIZE, SIZE))
  array = np.asarray(image, dtype=np.float32) / 127.5 - 1.0
  array = np.expand_dims(array, axis=0)
 except (UnidentifiedImageError, OSError, ValueError):
  return jsonify({'error': 'The uploaded file is not a valid image.'}), 400
 try:
  scores = np.asarray(model.predict(array, verbose=0))[0]
  if len(scores) != len(classes): return jsonify({'error': 'Model output and class_names.json do not match.'}), 500
  idx = int(np.argmax(scores)); name = classes[idx]
  lang = 'mr' if request.form.get('language', 'en').lower() == 'mr' else 'en'
  return jsonify({'class_name': name, 'crop': name.split('___', 1)[0].replace('_', ' '),
   'disease': name.split('___', 1)[1].replace('_', ' ') if '___' in name else name,
   'confidence': round(float(scores[idx]) * 100, 2), 'info': info_for(name, lang),
   'disclaimer': 'AI screening only; verify with an agricultural expert before making treatment decisions.'})
 except Exception:
  app.logger.exception('Prediction failed')
  return jsonify({'error': 'Prediction failed. Check model files and server logs.'}), 500

@app.errorhandler(413)
def too_large(_error): return jsonify({'error': 'Image is too large. Maximum upload size is 8 MB.'}), 413

if __name__ == '__main__':
 app.run(host='127.0.0.1', port=int(os.getenv('PORT', '5000')), debug=True)
