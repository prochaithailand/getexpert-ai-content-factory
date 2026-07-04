# Sprint 13 Technical Recommendations

This document outlines the recommendations for the upcoming sprints based on real user behaviors and conversion feedback collected during the VPS pilot.

---

## 1. Summary of Identified Priorities

Based on the pilot user survey:
1.  **High Friction (Payment Gate):** Users are willing to pay 99 THB, but manual admin credit verification creates a 10–30 minute top-up lag. **This is the primary blocker to paid scaling.**
2.  **Visual Flaws (Horizontal Scroll):** Streamlit tabs require CSS viewport optimization to improve swipe smoothness on Android devices.
3.  **Future Architecture:** To transition away from Streamlit's full-rerun latency, a decoupled backend is recommended.

---

## 2. Actionable Next Sprint Proposals

### Proposal 1: Automated QR Code & Slip Scanner API (Sprint 14)
*   **Goal:** Integrate a PromptPay slip auto-verification API (e.g., slipok.com or easy slip scanner).
*   **Workflow:**
    1.  User scans QR and transfers 99 Baht.
    2.  User uploads slip to the app.
    3.  A lightweight background routine validates the transaction hash (ref-id, amount, date) and deposits 10 credits **instantly** without admin manual oversight.
*   **Impact:** Removes checkout friction, enabling 24/7 automated sales.

### Proposal 2: Backend REST Service & FastAPI (Sprint 15)
*   **Goal:** Extract API endpoints (`api.getexpert.biz`) wrapping Gemini and Google Sheets database routines, establishing security headers.
*   **Impact:** Prepares core services to feed custom web and mobile client frontends.

### Proposal 3: Custom React Frontend App (Sprint 16)
*   **Goal:** Build a custom React/Next.js single-page application (SPA) hosted on `app.getexpert.biz`.
*   **Impact:** Completely removes Streamlit full page reruns, resolves mobile horizontal scrolling issues, and allows for custom dashboard grid designs.
