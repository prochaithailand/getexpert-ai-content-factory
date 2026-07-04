# Sprint 11 Rollback Execution Plan

This document details the step-by-step procedures to execute an emergency rollback of all public production traffic back to Streamlit Cloud if the self-hosted VPS candidate fails after the switch.

---

## 1. Hot Standby Verification
Before performing a rollback, confirm that the Streamlit Cloud instance is functional:
- [ ] Open `https://getexpert-ai-content-factory1.streamlit.app/?demo=true` in a browser.
- [ ] Verify that the page loads, database connections work, and it can access the Google Sheets backend.

---

## 2. DNS Reversion Procedure

If the VPS server crashes, Nginx fails, or SSL certificates are blocked:

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│  1. Login DNS Console   ├────>│ 2. Select app Subdomain ├────>│  3. Revert CNAME Target │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
                                                                             │
┌─────────────────────────┐     ┌─────────────────────────┐     ┌────────────▼────────────┐
│  6. End-to-End Test     │<────│   5. Clear browser      │<────│  4. Save Modifications  │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

1.  **Log in to the DNS Management Panel** (e.g. Cloudflare).
2.  Navigate to the DNS records of `getexpert.biz`.
3.  Locate the CNAME record for the `app` subdomain.
4.  **Revert Target URL:**
    *   Change the target back to: `getexpert-ai-content-factory1.streamlit.app`
    *   Set TTL to: `120 seconds` (or `Automatic` if using Cloudflare proxy).
5.  **Save Changes:** Apply updates immediately.

---

## 3. Marketing Landing Page Reversion
If the CTA links on the landing page `getexpert.biz` were updated via source code files:
- [ ] Revert the source files to the previous stable commit where the buttons pointed to the Streamlit Cloud URL:
  `https://getexpert-ai-content-factory1.streamlit.app/?demo=true`
- [ ] Push the changes to the static web host.

---

## 4. Reversion Validation
- [ ] Run DNS query to confirm propagation:
  ```bash
  dig +short app.getexpert.biz
  ```
  Confirm it returns the Streamlit Cloud alias domain.
- [ ] Open `https://app.getexpert.biz` on mobile devices.
- [ ] Verify that the app loads and displaying the default Streamlit Cloud header toolbar (indicating successful rollback).
