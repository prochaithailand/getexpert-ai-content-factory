# Sprint 11 Post-Launch Monitoring Checklist

This checklist defines the operational audits, database checks, resource checks, and feedback loops to execute at the 24-hour and 72-hour milestones after switching public traffic to the self-hosted VPS app.

---

## 1. The 24-Hour Post-Launch Checklist

- [ ] **Docker Container Health:** Verify both the web app and queue worker containers are running stably:
  ```bash
  docker compose ps
  ```
- [ ] **Log File Review:** Search logs for any Python tracebacks, Google API, or Gemini API errors:
  ```bash
  docker compose logs --since 24h | grep -Ei "ERROR|EXCEPTION|WARNING"
  ```
- [ ] **CPU and Memory Load:** Confirm system footprint remains within safe VPS limits:
  ```bash
  docker stats --no-stream
  ```
- [ ] **Google Sheets Integrity:** Crosscheck recent user registrations, credit log entries, and referral records to ensure zero database synchronization locks.
- [ ] **WebView pop-up checks:** Verify there are no reports of blocked pop-ups or dead redirects from LINE WebView users tapping the LINE OA button.

---

## 2. The 72-Hour Post-Launch Checklist

- [ ] **Long-term Uptime:** Verify that neither container has restarted unexpectedly:
  ```bash
  docker compose ps --filter "status=running"
  ```
  Check the `STATUS` column (e.g. `Up 3 days` is expected).
- [ ] **Nginx Error Logs Audit:** Check `/var/log/nginx/error.log` for any 502 Bad Gateway, 504 Gateway Timeout, or upstream buffer allocation warnings.
- [ ] **Payment Flow Validation:** Confirm that manual payment logs and billing credits deposited by admin match user records.
- [ ] **Feedback Compilation:** Compile usability notes from LINE OA chat logs to verify that Streamlit logos or deploy menu issues are completely resolved.
