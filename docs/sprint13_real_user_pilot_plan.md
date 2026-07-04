# Sprint 13 Real User Pilot Plan

This document details the operational execution plan to coordinate a real user pilot with 3–10 testers, monitor production health, and track user conversion patterns.

---

## 1. Pilot Objectives & Parameters

*   **Target Size:** 3 to 10 active content strategists / creators.
*   **Target Environment:** Primary Production URL at `https://app.getexpert.biz`.
*   **Fallback Standby:** Streamlit Cloud active on `getexpert-ai-content-factory1.streamlit.app` as CNAME switch target.
*   **Focus areas:**
    *   *Stability:* WebSocket persistence under heavy network loads (e.g. cellular data 4G/5G).
    *   *User flow clarity:* Verify users understand trial gates, limits, and pricing packages.
    *   *Data Consistency:* Sheets writes must map correctly under concurrent generations.

---

## 2. Server Operations & Monitoring Routine

During the active pilot window, the administrator must run the following checks:

### tail container logs
```bash
# Monitor container logs for generation errors or API blocks
docker compose logs -f --tail=200
```

### tail Nginx gateway logs
Check for WebSocket disconnects or gateway timeouts:
```bash
tail -f /var/log/nginx/error.log | grep -Ei "timeout|failed|warn"
```

### Sheets database checks
Crosscheck registration records and transaction IDs:
- [ ] Confirm new users appear in the `Users` sheet with referred-by attributes.
- [ ] Verify that credits deduction matches the generation logs.
