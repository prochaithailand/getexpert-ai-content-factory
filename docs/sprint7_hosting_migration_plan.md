# Sprint 7 Hosting Migration Plan: GetExpert AI Content Factory

This document provides a risk assessment, a recommended 6-phase roadmap, a minimum safe first step, and a freeze list to transition the application away from Streamlit Cloud to self-hosted infrastructure.

---

## 1. Migration Risk Assessment

Migrating a production application from a managed PaaS like Streamlit Cloud to a self-hosted VPS introduces risks that must be managed:

| Risk Area | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **State Management Loss** | Streamlit manages state server-side dynamically. Custom frontend/backends require manual token, cookie, and Session validation. | Design JWT token structures for stateless FastAPI requests; use Web Storage (localStorage/sessionStorage) in the custom JS frontend. |
| **API Endpoint Vulnerability** | Currently, database (Google Sheets) and Gemini APIs run completely server-side, safe from client inspection. Creating FastAPI endpoints exposes them to the public internet. | Implement secure API keys and rate-limiting on FastAPI routes. Require user authentication headers for content requests. |
| **Increased Server Admin Overhead** | Moving to VPS means Nginx updates, Docker container failures, let's encrypt cron certificate renewals, and memory leaks are self-managed. | Implement Docker healthchecks, automatic restart policies (`restart: always`), and configure uptimerobot monitors. |
| **Cross-Browser & Mobile Compatibility** | Streamlit provides a responsive viewport out of the box. Building a custom HTML portal requires thorough CSS responsive layout design. | Use standard responsive CSS frameworks or CSS Flexbox/Grid with mobile-first media queries; test on simulated iOS/Android screens. |

---

## 2. Recommended Migration Phases

To ensure production stability, we propose a 6-phase migration roadmap:

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│         Phase 1         │     │         Phase 2         │     │         Phase 3         │
│   Audit & Doc (S7)      ├────>│   Dockerize Streamlit   ├────>│   Self-Host Streamlit   │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
                                                                             │
┌─────────────────────────┐     ┌─────────────────────────┐     ┌────────────▼────────────┐
│         Phase 6         │     │         Phase 5         │     │         Phase 4         │
│   Traffic Migration     │<────┤   Build Custom UI App   │<────┤  Extract FastAPI APIs   │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

*   **Phase 1: Documentation and Audit (Sprint 7):** Research current modules, plan folder structures, and alignment.
*   **Phase 2: Dockerize Current Streamlit App:** Package the current Streamlit app, dependencies, and queue worker into a multi-container Docker setup. Verify it runs locally on a dev machine.
*   **Phase 3: Self-Host Streamlit on VPS:** Deploy the Docker container on a Hostinger VPS behind Nginx with Let's Encrypt SSL. *This immediately solves the Streamlit Cloud limits and removes the Streamlit Cloud viewer header/footer toolbar by serving the app via a custom domain proxy.*
*   **Phase 4: Extract Backend Logic (FastAPI):** Build FastAPI routing wrappers around `services/` and `models/`. Convert `main.py` into a background daemon container. Test all JSON API endpoints.
*   **Phase 5: Build Custom Frontend:** Build a clean Landing Page (`getexpert.biz`) and a customer React/Vue/Vanilla JS App (`app.getexpert.biz`) communicating with `api.getexpert.biz`.
*   **Phase 6: Move Production Traffic Gradually:** Keep both hosting environments running in parallel. Direct 10% of new traffic to the new custom web app, monitor Google Sheets entries, and eventually shift 100% DNS records.

---

## 3. Minimum Safe First Step

The recommended first step is **Phase 2 & Phase 3 (Dockerizing and Self-hosting the current Streamlit app on the VPS)**.

*   **Why it is safe:** It requires **zero changes** to the existing Python code, credit gates, payment rules, or database logic. It merely changes *where* the application is run.
*   **What it achieves:**
    1.  Resolves Streamlit Cloud memory limits.
    2.  Removes the native Streamlit cloud toolbar/deploy header that confuses mobile users (by serving Streamlit behind Nginx proxy with custom CSS headers injected or query string toggles like `?embed=true`).
    3.  Validates Nginx routing, Docker networks, and SSL setups on the new Hostinger VPS before writing any new code.

---

## 4. Files to Avoid Changing Now (Freeze List)

During the planning and Dockerization stage, keep a strict code freeze on the following components to prevent production regression:

1.  **Orchestrator Logic:** [`web_app.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/web_app.py) (Indentation structure, form submission blocks).
2.  **Core Services:**
    - [`services/sheets_service.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/services/sheets_service.py) (Google API client sheets parsing, retry limits, referral commission logging).
    - [`services/credit_service.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/services/credit_service.py) (Payment validation logic, credit gate balances).
3.  **Database Schemas:**
    - [`models/content_models.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/models/content_models.py)
    - [`models/credit_models.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/models/credit_models.py)
4.  **Worker Engine:** [`main.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/main.py) (Polling loops, Gemini generation steps).
