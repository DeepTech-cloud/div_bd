# DivineAI Backend

Scalable backend for the DivineAI application.

## Tech Stack
- FastAPI
- PostgreSQL
- Celery + Redis
- OpenCV
- Cloudinary
- Gemini API

## Setup

1. Copy `.env.example` to `.env` and fill the variables.
2. Run `docker-compose up --build`
3. Access API docs at `http://localhost:8000/docs`
uvicorn main:app --reload