# Streamlit Cloud vs. Self-hosted VPS Comparison

This document provides a comparative analysis between the managed Streamlit Cloud service and the self-hosted Docker/Nginx VPS environment.

---

## 1. Feature & UX Comparison

| Feature / UI Element | Managed Streamlit Cloud | Self-hosted Hostinger VPS |
| :--- | :--- | :--- |
| **Streamlit Deploy Header** | ❌ **Visible.** Floating buttons and deploy menus are visible on mobile and can confuse users. |  **Hidden.** Nginx proxy filters and query parameters (`?embed=true` or `.streamlit/config.toml` configurations) hide headers completely. |
| **RAM & Compute Limits** | ❌ **1 GB Limit.** Frequent OOM (Out Of Memory) container restarts during heavy concurrent operations. |  **Scalable.** Memory limits depend on VPS specs. Automatic container restarts handled via Docker policies. |
| **Viewer Watermark** | ❌ **Visible.** "Made with Streamlit" watermark cannot be permanently removed. |  **Removed.** Clean interface without default Streamlit branding. |
| **WebSocket Timeout** | ❌ **Fixed.** Streamlit Cloud times out websocket threads, causing page disconnect reloads. |  **Customizable.** Nginx configuration supports increased timeouts (`proxy_read_timeout 600s`), maintaining stable sessions. |
| **Domain & SSL Control** | ❌ **Limited.** Bound to `*.streamlit.app` domains. |  **Full Control.** Custom domain mapping (`app.getexpert.biz`) and SSL setup via Certbot Let's Encrypt. |

---

## 2. Conclusion on Production Readiness

The self-hosted Hostinger VPS deployment is **stable, secure, and ready to become the production environment candidate**. 

*   **Branding Cleanliness:** It removes all Streamlit-branded menus and deploy headers, which solves the mobile UX issue reported by users.
*   **Websocket Stability:** Upgraded WebSocket headers through Nginx eliminate connection drops, allowing long-running content strategy generations (often taking up to 30-45 seconds) to execute smoothly.
