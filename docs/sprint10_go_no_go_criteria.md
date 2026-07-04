# Sprint 10 Go / No-Go Traffic Switch Criteria

This document defines the quantitative and qualitative requirements (quality gates) that must be met to approve switching public traffic from managed Streamlit Cloud to the self-hosted Hostinger VPS candidate.

---

## 1. Quality Gates (Go / No-Go Parameters)

| Metric / Requirement | Target Threshold | Assessment Method | Status |
| :--- | :--- | :--- | :--- |
| **System Uptime** | > 99.9% over a 48-hour period | Monitored via UptimeRobot pinging `https://app.getexpert.biz`. | - |
| **Error Rate** | 0% critical errors (Segfaults, OOMs, database write locks) | Inspection of `docker compose logs` of both frontend app and background worker. | - |
| **LINE OA WebView Redirect** | 100% success rate on tester mobile devices | Direct feedback validation from the 3–5 beta testers. | - |
| **Branding Elimination** | Streamlit deploy header and footer hidden on mobile Chrome/Safari | Visual validation and confirmation from users. | - |
| **Data Integrity** | Zero data discrepancy or missing rows | Double checking user row creations and payment credits in Google Sheets. | - |
| **DNS Rollback TTL** | TTL set to 120s or 300s (permitting rapid reversion) | Verification of active CNAME settings in Cloudflare DNS panel. | - |

---

## 2. Decision Logic

### GO Decision
If **all** requirements in Section 1 are verified as **Passed**, we proceed to change the main CTA redirection links on the primary sales website `getexpert.biz` to point to `https://app.getexpert.biz` instead of the old Streamlit Cloud URL.

### NO-GO Decision
If any criteria fails (e.g. users report websocket drops, or Nginx throws 502/504 Gateway errors during strategy generation), we enforce a **NO-GO** decision. The system remains on Streamlit Cloud, and all VPS logs are audited for corrective action.
