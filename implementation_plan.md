# Migrate from PostgreSQL to Firebase

This plan outlines the steps to replace the current PostgreSQL database with Firebase, utilizing Firebase Storage for images and Firestore for settings.

## User Review Required

> [!WARNING]
> This change completely removes PostgreSQL and replaces it with Firebase. 
> You will need to provide a Firebase Admin SDK credentials JSON file (or equivalent environment variables) for the backend to authenticate with Firebase.

## Open Questions

> [!IMPORTANT]
> 1. **Authentication:** How would you like to pass the Firebase credentials? We can pass a path to a service account JSON file via the `FIREBASE_CREDENTIALS_PATH` environment variable, or pass the JSON content directly in a base64 encoded environment variable. 
> 2. **Firebase Storage Bucket:** We will need the name of your Firebase Storage bucket (e.g., `your-project.appspot.com`). We will add a `FIREBASE_STORAGE_BUCKET` env var for this.
> 3. **Are you okay with removing the local PostgreSQL container from `docker-compose.yml`?**

## Proposed Changes

### Configuration and Dependencies
- Remove `sqlalchemy` and `psycopg2-binary` from `requirements.txt`.
- Add `firebase-admin` to `requirements.txt`.
- Remove the PostgreSQL database service from `docker-compose.yml` and `README.md`.
- Update `app/core/config.py` to remove DB settings and add Firebase settings (`FIREBASE_CREDENTIALS_PATH`, `FIREBASE_STORAGE_BUCKET`).

### Core Initialization
- Delete `app/core/db.py` and `app/core/models.py`.
- Create a new file `app/core/firebase.py` to initialize the Firebase Admin SDK using the provided credentials.
- Update `app/main.py` to call the Firebase initialization instead of `init_db`, and remove the `/static/{image_id:path}` route (as images will be served directly from Firebase Storage URLs).

### Storage Integration
- Refactor `app/storage/local_storage.py` (which currently saves bytes to PostgreSQL) to upload files directly to Firebase Storage. We will rename this file to `app/storage/firebase_storage.py` to reflect its new behavior.
- The `save_image` function will upload the bytes to the Firebase bucket and return the public URL.
- The `delete_image` function will delete the object from the Firebase bucket.

### API Updates
- Update `app/api/routers/settings.py` to read and write settings directly to a Firestore collection (e.g., `settings`).
- Update `app/api/routers/history.py` and `app/api/routers/upload.py` to import from the renamed `firebase_storage.py`.

## Verification Plan

### Automated Tests
- Run backend linting and syntax checks to ensure the `firebase-admin` integration is correct.

### Manual Verification
- Start the server using `docker-compose up --build`.
- Upload an image via the `/upload` endpoint and verify it appears in your Firebase Storage bucket and a valid public URL is returned.
- Update settings via the `/settings` endpoint and verify the changes are reflected in Firestore.
