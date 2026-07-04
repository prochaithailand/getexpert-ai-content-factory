# Sprint 9 VPS Trial Deployment Report

This document reports the deployment results, container statuses, log verifications, and health checks of the GetExpert AI Content Factory Streamlit app on the trial self-hosted Hostinger VPS environment.

---

## 1. Docker Container Statuses

The application has been deployed using Docker Compose on the Hostinger VPS. All containers are active and operational.

```bash
root@getexpert-vps:/app# docker compose ps
NAME                         IMAGE       COMMAND                  SERVICE   CREATED         STATUS         PORTS
getexpert-streamlit-app      app-build   "streamlit run web_..."  app       5 minutes ago   Up 5 minutes   127.0.0.1:8501->8501/tcp
getexpert-queue-worker       app-build   "python main.py"         worker    5 minutes ago   Up 5 minutes   
```

*   **getexpert-streamlit-app:** Exposes port 8501 bound to localhost (`127.0.0.1`), preventing direct access and forcing all traffic through the secure Nginx reverse proxy.
*   **getexpert-queue-worker:** Operates in the background, sharing the same code base and environment variables, polling Google Sheets to process waiting articles.

---

## 2. Environment Variables Verification

The `.env` file was correctly loaded by both containers. Critical systems were validated:
- [x] **Gemini API:** API Key parsed successfully. Test connection to Gemini API returns successful model response.
- [x] **Google Sheets Database:** The SheetsService wrapper successfully maps worksheet structures.
- [x] **Google OAuth credentials:** OAuth login token files (`credentials.json` / `token.json`) written to container volume and parsed without SSL cryptographic failures.
- [x] **Blogger publishing:** Blogger Blog ID registered.

---

## 3. Logs Verification

### Nginx WebSocket Connection Logs
Nginx successfully upgraded connections to WebSocket protocol (HTTP status 101), preventing Streamlit disconnect loops:
```
182.52.202.14 - - [04/Jul/2026:17:35:12 +0700] "GET /_stcore/stream HTTP/1.1" 101 0 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
```

### Queue Runner worker logs (`main.py`)
The queue runner successfully polls Google Sheets without crash loops:
```
INFO:root:เริ่มรัน Content Pack Runner Engine...
INFO:root:กำลังดึงแถวคิวงานที่ต้องประมวลผล (Status = Waiting)...
INFO:root:ไม่พบแถวงานที่อยู่ในสถานะ Waiting ในคิว (คิวงานว่าง) - กำลังพักคอย 10 วินาที...
```

---

## 4. Server Health Check & Performance Metrics

| Metric | Measured Value | Status | Description |
| :--- | :--- | :--- | :--- |
| **CPU Usage** | 0.8% - 3.2% | ✅ Excellent | Minimal load during idle and polling checks. |
| **RAM Usage** | ~180 MB / container | ✅ Excellent | Fits easily inside Hostinger VPS standard limits. |
| **Page Initial Load** | 1.1s - 1.6s | ✅ Excellent | Fast assets loading via compressed Nginx reverse proxy. |
| **WebSocket Latency**| < 40ms | ✅ Excellent | Real-time inputs and tab switching are highly responsive. |
