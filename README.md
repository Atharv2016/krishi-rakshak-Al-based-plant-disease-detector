<<<<<<< HEAD
# Krishi Rakshak — AI-Based Plant Disease Detector

A bilingual (English/Marathi) web application for AI-assisted screening of tomato, potato and grape leaf images. Stack: HTML/CSS/JavaScript, Python/Flask, TensorFlow/Keras MobileNetV2 and optional Firebase Firestore.

> **Important:** This is an educational screening project, not a confirmed diagnosis. The model can be wrong, especially on real field photos. Do not make pesticide or treatment decisions from the prediction alone. Ask a qualified agricultural expert to confirm the condition.

## What is included

- Responsive bilingual frontend (English / मराठी)
- Image upload and mobile camera capture, file validation and preview
- Flask API with image validation and an 8 MB upload limit
- MobileNetV2 transfer-learning script, filtered to Tomato, Potato and Grape PlantVillage classes
- Confidence score, general symptoms and non-prescriptive advice
- Local scan history in the browser
- Optional Firebase anonymous authentication + Firestore cloud copy of scan history
- Health endpoint and basic API tests

The trained model weights are **not included** in this source bundle. Training creates `model/plant_disease_model.keras`, `model/class_names.json` and `model/training_report.json`.

## 1. Requirements

- Python 3.10–3.12 recommended; check TensorFlow's current compatibility for your OS and Python version.
- Internet connection for installing packages, downloading ImageNet weights during training, and optionally Firebase.
- Google Colab with a GPU is recommended for training. The web app itself can run on CPU.
- A PlantVillage dataset folder downloaded from a legitimate dataset provider.

## 2. Get the source and dataset

1. Extract the project ZIP.
2. Download PlantVillage using the [TensorFlow Datasets PlantVillage documentation](https://www.tensorflow.org/datasets/catalog/plant_village) or the [Mendeley Data dataset page](https://data.mendeley.com/datasets/tywbtsjrjv/1). Check the provider's terms and citation requirements.
3. Arrange the image folders like this (folder names are important):

```text
Krishi-Rakshak/
  dataset/
    PlantVillage/
      Grape___Black_rot/
        image_001.jpg
      Grape___healthy/
      Grape___Esca_(Black_Measles)/
      Potato___Early_blight/
      Potato___Late_blight/
      Potato___healthy/
      Tomato___Early_blight/
      Tomato___Late_blight/
      Tomato___healthy/
      ... other Tomato, Potato and Grape classes ...
```

The training script reads class subfolders immediately inside `dataset/PlantVillage` and keeps folders whose names begin with `Tomato___`, `Potato___` or `Grape___`. Some dataset copies have an extra wrapper folder. If yours does, set `KRISHI_DATA_DIR` to the directory that directly contains the class folders.

## 3. Create the Python environment (Windows PowerShell)

Open PowerShell in the `Krishi-Rakshak` folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

If PowerShell blocks activation, use this for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If TensorFlow does not install for your OS/Python version, use Google Colab for training or choose a Python version supported by the current TensorFlow installation guide. Do not install random unofficial TensorFlow builds.

## 4. Train the model

### Recommended: Google Colab

1. Upload this project folder or the `model/train_model.py` script and dataset to Google Drive / Colab.
2. In Colab, install the packages from `backend/requirements.txt` (or at minimum TensorFlow, NumPy and Pillow).
3. Set `KRISHI_DATA_DIR` to the directory containing the crop class folders, then run `python model/train_model.py` from the project root.
4. When training completes, copy these generated files back into your local project `model/` folder:
   - `plant_disease_model.keras`
   - `class_names.json`
   - `training_report.json` (optional but useful for your report)

### Run locally

```powershell
$env:KRISHI_DATA_DIR = "$PWD\dataset\PlantVillage"
python model\train_model.py
```

Optional settings:

```powershell
$env:KRISHI_BATCH_SIZE = "16"
$env:KRISHI_HEAD_EPOCHS = "8"
$env:KRISHI_FINE_EPOCHS = "3"
python model\train_model.py
```

Training may take from several minutes to hours depending on the dataset, computer, and GPU. The script creates a random per-class training/validation split. Its reported validation accuracy is **not** a guarantee of field performance. For a stronger college evaluation, reserve a separate test set and test on photos from real local farms that were not used for training or validation.

## 5. Start the web application

After the model files exist, in the project root:

```powershell
.\.venv\Scripts\Activate.ps1
python backend\app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. Keep the terminal running. Upload a clear JPG, PNG or WEBP leaf image and select English or Marathi.

Check API/model readiness at [http://127.0.0.1:5000/api/health](http://127.0.0.1:5000/api/health). If `model_ready` is `false`, read `model_message`; the UI and API are intentionally not going to invent a prediction without a trained model.

## 6. Firebase setup (optional)

The app works locally without Firebase. By default, scan history is stored in the current browser's local storage. Firebase adds an optional cloud copy for an anonymous user.

1. Create a project at [Firebase Console](https://console.firebase.google.com/).
2. Add a Web App and copy its web configuration into `frontend/firebase-config.js`.
3. In Firebase Authentication, enable **Anonymous** sign-in.
4. Create a Firestore database.
5. Publish the rules from `firebase/firestore.rules` in Firestore Rules.
6. Serve the frontend through Flask (recommended) or another HTTP server. Firebase web SDK modules generally should not be opened via `file://`.

The supplied Firestore rules restrict users to their own `users/{uid}/scans` path and disallow updates/deletes. The current interface keeps its visible history in browser local storage and writes a cloud copy after a successful prediction; it does not yet sync cloud records back into the history list. Never place Firebase Admin SDK service-account credentials in frontend files. Configure API restrictions and production rules before public deployment.

## 7. API reference

### `GET /api/health`

Returns status and whether the trained model can be loaded.

### `POST /api/predict`

Multipart form fields:

- `image`: JPG, JPEG, PNG or WEBP file (max 8 MB)
- `language`: `en` or `mr`

Successful response example:

```json
{
  "class_name": "Tomato___Early_blight",
  "crop": "Tomato",
  "disease": "Early blight",
  "confidence": 96.2,
  "info": {
    "title": "Tomato — Early blight",
    "symptoms": "...",
    "advice": "..."
  },
  "disclaimer": "AI screening only; verify with an agricultural expert before making treatment decisions."
}
```

Confidence is the model's top class score, not a calibrated probability that a diagnosis is correct.

## 8. Testing

With the virtual environment active and the API running in another terminal:

```powershell
python -m unittest discover -s tests -v
```

The tests verify API health response shape and invalid upload handling. Add real-image tests and a held-out evaluation set before submitting results or claiming an accuracy figure.

## 9. Deployment outline

- **Frontend + API together:** deploy this Flask app to a Python-capable host such as a container service or a Python web service. Add a production WSGI server (for example Gunicorn on Linux) and set the start command to `gunicorn backend.app:app` from the project root. Confirm the host has enough RAM for TensorFlow and include the model files in the deployed artifact or download them securely at startup.
- **Frontend on Firebase Hosting:** deploy only `frontend/` as static files and set `window.KRISHI_API_BASE` in `frontend/app.js` to your deployed API base URL. Configure `KRISHI_ALLOWED_ORIGINS` on the API to your exact frontend origin, not `*`, for production.
- **Firebase Hosting alone does not execute Flask/TensorFlow.** The Python API needs a Python-capable service or a separately implemented supported serverless inference endpoint.
- Do not use Flask's debug server in production. Set secrets and environment variables through the host's configuration panel.

## 10. Suggested college project report sections

1. Abstract and problem statement
2. Objectives and scope
3. Literature review / existing system and proposed system
4. Requirements and system architecture
5. Dataset description and class distribution
6. Preprocessing and MobileNetV2 transfer learning
7. Training setup, validation/test methodology and metrics
8. UI screenshots and API design
9. Testing, limitations, privacy and ethical considerations
10. Future scope: farmer login, local crop support, offline inference, expert referrals and verified regional-language guidance

## Troubleshooting

- **Model not ready:** train the model and ensure both model files are in `model/`.
- **TensorFlow install issue:** use a compatible Python version/OS or train on Google Colab.
- **No class folders found:** set `KRISHI_DATA_DIR` to the folder that directly contains class directories.
- **Browser says server unavailable:** run `python backend/app.py`, then open the app through `http://127.0.0.1:5000`.
- **Poor results on field photos:** the model may have learned dataset-specific backgrounds. Collect diverse, correctly labeled local images and evaluate on a separate real-world test set.
=======
# krishi-rakshak-Al-based-plant-disease-detector
This project will detect the disease.
>>>>>>> 1aac5e6220474fcbebf90c07d6a1e30e7ba94577
