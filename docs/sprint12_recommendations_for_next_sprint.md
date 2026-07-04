# Sprint 12 Future Technical Recommendations

This document outlines the recommendations and architectural path for subsequent sprints based on lessons learned from the VPS migration and real user onboarding.

---

## Proposed Roadmap for Next Sprints

```
┌─────────────────────────────────┐
│            Sprint 13            │
│  Backend REST API (FastAPI)     │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│            Sprint 14            │
│  Custom Frontend (React / SPA)  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│            Sprint 15            │
│   Automated Billing / Top-up    │
└─────────────────────────────────┘
```

### Recommendation 1: Backend API Extraction (Sprint 13)
*   **Goal:** Extract business logic from the Streamlit file [`web_app.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/web_app.py) into a **FastAPI** web server (`api.getexpert.biz`).
*   **Why it is needed:**
    *   *Security:* Encapsulates Google Sheet credentials, Blogger OAuth tokens, and Gemini API keys behind stateless endpoints. Clients never access database code directly.
    *   *Modularity:* Decouples data query wrappers from UI components, preparing the architecture for a custom React/Next.js frontend.
    *   *Scalability:* Permits clustering multiple API container worker threads easily.

### Recommendation 2: Custom Customer Web App (Sprint 14)
*   **Goal:** Replace the Streamlit frontend with a custom single-page application (SPA) built with **React** or **Next.js** (`app.getexpert.biz`).
*   **Why it is needed:**
    *   *User Experience:* Removes Streamlit's full-top-down rerun model, reducing rendering latency on mobile browsers.
    *   *State Persistence:* Retains authentication details (JWT) and user data cache locally inside the browser.
    *   *Mobile UX Design:* Fully control HTML grid structures and layouts, resolving overflow blocks.

### Recommendation 3: Automated Payment QR Integration (Sprint 15)
*   **Goal:** Integrate automated payment gateways (e.g., PromptPay QR slip verification API or GB Prime Pay).
*   **Why it is needed:**
    *   *Operations:* Removes manual admin validation. Credits are top-up automatically within 10 seconds of scanning, increasing sales conversion.
