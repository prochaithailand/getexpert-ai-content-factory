# Sprint 8 Self-hosted Streamlit Deployment Guide

This document outlines step-by-step instructions to build, configure, run, and monitor the GetExpert AI Content Factory Streamlit application and its background queue runner using Docker and Docker Compose.

---

## 1. Setup Local Environment File

First, prepare the environment configuration file `.env` which will contain the actual secrets. **Never commit the `.env` file to your Git repository!**

1.  Copy the example template file to a new `.env` file in the root directory:
    ```bash
    cp .env.example .env
    ```
2.  Open `.env` and fill in the required values:
    *   `GEMINI_API_KEY`: Google Gemini API Key.
    *   `GOOGLE_SHEET_ID`: Google Sheet ID (from the sheets URL).
    *   `BLOGGER_BLOG_ID`: Target Blogger Blog ID.
    *   `GOOGLE_CREDENTIALS_JSON`: The full, raw JSON content of your Google Cloud OAuth credentials file (flattened into a single inline string).
    *   `GOOGLE_TOKEN_JSON`: The full, raw JSON content of your logged-in Google token file (flattened into a single inline string).

---

## 2. Docker Image & Container Operations

### Building the Containers
Run the build command to install system libraries and pip dependencies into a new local Python image:
```bash
docker compose build
```

### Launching the Application
Launch both the frontend Streamlit portal (`app` service) and the asynchronous queue runner worker (`worker` service) in detached daemon mode:
```bash
docker compose up -d
```

### Checking Status and Health
Verify that both containers are active and running:
```bash
docker compose ps
```

### Monitoring Logs
Inspect real-time logs from both the Streamlit app and the main queue worker:
```bash
# Monitor both containers
docker compose logs -f

# Monitor only the Gemini content generation engine
docker compose logs -f worker
```

---

## 3. Stopping and Restarting

### Restarting the Services
Use this if you update environment configurations or modify source files (which requires reloading standard memory cache):
```bash
docker compose restart
```

### Stopping the Services
Tear down the containers, networks, and internal resources safely:
```bash
docker compose down
```

---

## 4. Local Verification

To verify that the self-hosted setup works locally:
1.  Open your browser and navigate to `http://localhost:8501`.
2.  Verify the app loads without crash.
3.  Fill in the email input and click **🔍 ตรวจสอบเครดิตและสิทธิ์ใช้งาน** to test Google Sheets API connection inside the Docker environment.
4.  Navigate to the background console log to verify that no `SSL RECORD_LAYER_FAILURE` or Google API exceptions are thrown.
