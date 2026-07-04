# Sprint 11 Public Traffic Switch Plan

This document details the procedures to shift all public production traffic from managed Streamlit Cloud to the self-hosted Hostinger VPS candidate (`https://app.getexpert.biz`).

---

## 1. Domain Routing & DNS Setup

To switch user traffic, update your DNS registry records in your DNS manager (e.g. Cloudflare):

### Primary App Subdomain (`app.getexpert.biz`)
- [ ] **Type:** `CNAME`
- [ ] **Name:** `app`
- [ ] **Target:** Change from Streamlit Cloud alias to the Hostinger VPS IP/host domain.
- [ ] **TTL:** Set to `120 seconds` (or `Automatic` if proxied through Cloudflare).
- [ ] **Proxy Status:** `Proxied` (retaining Cloudflare DDOS protection and caching) or `DNS only` depending on TLS configurations.

### Rollback / Fallback Target (Streamlit Cloud)
Ensure the old Streamlit Cloud instance remains active and untouched:
*   **Fallback URL:** `https://getexpert-ai-content-factory1.streamlit.app/?demo=true`
*   Do not archive, delete, or suspend the Streamlit Cloud deployment project. Keep it as a hot standby.

---

## 2. Transition Checklist

- [ ] **DNS Modification:** Apply the CNAME changes in the DNS panel.
- [ ] **Propagation Check:** Run dig commands locally and verify IP resolution updates:
  ```bash
  dig +short app.getexpert.biz
  ```
- [ ] **SSL Verification:** Load `https://app.getexpert.biz` and confirm that the Let's Encrypt TLS certificate remains valid (green lock icon, no security alerts).
- [ ] **Asset Loading:** Open the browser developer console (F12) to verify all assets, CSS, images, and javascript dependencies load successfully under the new routing.
- [ ] **Websocket Status:** Confirm WebSocket connection upgrades successfully (Status 101) through Nginx.
