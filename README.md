# DivineAI Backend

Scalable backend for the DivineAI application.

## Tech Stack
- FastAPI
- PostgreSQL (Google Cloud SQL)
- SQLAlchemy
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
DATABASE_URL=postgresql://postgres:postgrespassword@db:5432/divineai
```

---

## Google Cloud Deployment (Cloud Run + Cloud SQL)

### Prerequisites
- Google Cloud SDK (`gcloud`) installed and authenticated.
- Google Cloud SQL Postgres instance created (`divineai-504008:us-central1:divineai`).
- Cloud SQL Admin API enabled on the project.
- Cloud Run service account must have **Cloud SQL Client** IAM role.
- Docker image pushed to Google Container Registry (GCR) or Artifact Registry.

### 1. Build and Push the Docker Image
```bash
gcloud builds submit --tag gcr.io/divineai-504008/div_bd
```

### 2. Deploy to Cloud Run with Cloud SQL
Use the `--add-cloudsql-instances` flag to wire the Cloud SQL socket, and pass the DB credentials as environment variables:

```bash
gcloud run deploy div-bd \
  --image gcr.io/divineai-504008/div_bd \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --add-cloudsql-instances divineai-504008:us-central1:divineai \
  --set-env-vars "DB_USER=divineai" \
  --set-env-vars "DB_PASSWORD=@Xblue07" \
  --set-env-vars "DB_HOST=divineai-504008:us-central1:divineai" \
  --set-env-vars "DB_NAME=divineai" \
  --set-env-vars "BASE_URL=https://YOUR_CLOUD_RUN_URL" \
  --set-env-vars "GEMINI_API_KEY=your_gemini_api_key"
```

> **Note:** The app auto-detects the GCP instance name in `DB_HOST` and switches to the Unix socket format:
> `postgresql+psycopg2://divineai:%40Xblue07@/divineai?host=/cloudsql/divineai-504008:us-central1:divineai`

### 3. Access the Deployed API
Once deployed, access the API docs at:
```
https://YOUR_CLOUD_RUN_URL/docs
```

### Connecting to Cloud SQL with TCP (Optional — for Admin/Migration tools)
To connect directly using `psql`, use the Cloud SQL Auth Proxy:
```bash
./cloud-sql-proxy divineai-504008:us-central1:divineai
# Then connect:
psql "host=34.72.239.130  port=5432 sslmode=disable dbname=divineai user=divineai password=@Xblue07"
```