# DivineAI Backend

Scalable backend for the DivineAI application.

## Tech Stack
- FastAPI
- Firebase (Firestore & Storage)
- OpenCV
- Gemini API (google-generativeai)

## Local Development Setup

1. Copy `.env.example` to `.env` and fill the variables.
2. Run `docker-compose up --build`
3. Access API docs at `http://localhost:8000/docs`

### Local `.env` example
```env
BASE_URL=http://localhost:8000
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_CREDENTIALS_PATH=./secrets/firebase-credentials.json
FIREBASE_STORAGE_BUCKET=divineai-484b1.firebasestorage.app
```

---

## Google Cloud Deployment (Cloud Run)

### Prerequisites
- Google Cloud SDK (`gcloud`) installed and authenticated.
- Firebase project setup with Firestore and Storage enabled.
- Service account JSON with Firebase Admin privileges.
- Docker image pushed to Google Container Registry (GCR) or Artifact Registry.

### 1. Build and Push the Docker Image
```bash
gcloud builds submit --tag gcr.io/divineai-504008/div_bd
```

### 2. Deploy to Cloud Run
Pass the Firebase credentials and storage bucket as environment variables:

```bash
gcloud run deploy div-bd \
  --image gcr.io/divineai-504008/div_bd \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "BASE_URL=https://YOUR_CLOUD_RUN_URL" \
  --set-env-vars "GEMINI_API_KEY=your_gemini_api_key" \
  --set-env-vars "FIREBASE_STORAGE_BUCKET=your-project.appspot.com"
```
*(Note: If using default application credentials on GCP, you may not need to pass FIREBASE_CREDENTIALS_PATH)*

### 3. Access the Deployed API
Once deployed, access the API docs at:
```
https://YOUR_CLOUD_RUN_URL/docs
```