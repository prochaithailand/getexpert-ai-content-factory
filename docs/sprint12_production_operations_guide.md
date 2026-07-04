# Sprint 12 Production Operations Guide

This guide provides system administrators with the necessary procedures and commands to maintain, monitor, and troubleshoot the GetExpert AI Content Factory self-hosted VPS production environment (`https://app.getexpert.biz`).

---

## 1. Checking Container Statuses

To check the status of your running frontend portal and queue worker container daemons, log into your VPS via SSH and run:
```bash
# Check running status of containers
cd /app
docker compose ps
```
Both `getexpert-streamlit-app` and `getexpert-queue-worker` should show `STATUS` as `Up`.

---

## 2. Monitoring Runtime Logs

Inspect live trace outputs of the components to troubleshoot errors:

```bash
# Monitor logs for both the app and background worker
docker compose logs -f

# Monitor logs for the background AI Generation worker only
docker compose logs -f worker

# Search logs for exceptions or authentication failures
docker compose logs | grep -Ei "ERROR|EXCEPTION|WARNING"
```

---

## 3. Restarting Services

If environment variable configurations are updated, or to resolve memory bloats:
```bash
# Safe restart of both containers
docker compose restart

# Restart only the Streamlit portal container
docker compose restart app
```

---

## 4. Checking Nginx Error Logs

To audit SSL TLS handshakes, WebSocket upgrade handshakes, or proxy routing blocks:
```bash
# View active Nginx error logs
tail -n 100 -f /var/log/nginx/error.log

# View Nginx access logs (request statuses)
tail -n 100 -f /var/log/nginx/access.log
```

---

## 5. Google Sheets Sync Validations

Verify sheets database connectivity by opening `docker compose logs` and confirming that no SSL Record layer failures occur. Alternatively, verify updates directly inside your Google Sheets URL:
*   `Users` worksheet: Check new email registration rows.
*   `Payments` worksheet: Check manual credit top-up entries.
*   `Referral Logs` worksheet: Verify commission transactions are written to the columns.

---

## 6. Emergency Rollback Execution

If the VPS suffers critical failure, execute this immediately:
1.  Log in to your DNS provider (e.g. Cloudflare).
2.  Navigate to DNS settings for the domain `getexpert.biz`.
3.  Locate the CNAME record for the subdomain `app`.
4.  Change the CNAME target value back to:
    `getexpert-ai-content-factory1.streamlit.app`
5.  Set TTL to automatic/low and save. Traffic will propagate back to the fallback Streamlit Cloud instance within 2 minutes.
