# Sprint 11 Launch Result Report

This report evaluates the stability, performance, and user feedback of the self-hosted Hostinger VPS deployment (`https://app.getexpert.biz`) after executing the public traffic switch from Streamlit Cloud.

---

## 1. Launch Event Details

*   **Action Date:** July 4, 2026
*   **Target Subdomain:** `app.getexpert.biz` (CNAME successfully routed to VPS IP).
*   **DNS Propagation:** Propagated globally. Checked via dig and external DNS tools.
*   **Active Testers / Users:** 3–5 beta users invited and completed testing.
*   **Production Standby:** Streamlit Cloud instance is verified active on `getexpert-ai-content-factory1.streamlit.app` as a fallback.

---

## 2. Validation & Smoke Test Outcomes

We verified the core capabilities on the new VPS production endpoint:

- [x] **Demo Mode:** Generating trial Content Packs operates without delay.
- [x] **Credit & Payment Gates:** Verification checks, free trial depletion, QR code rendering, and custom LINE OA redirect buttons (`target="_self"` opening `https://lin.ee/TZgX4CD`) work correctly.
- [x] **Admin Controls:** Opening referrals, updating user credits, and adding payment records executes.
- [x] **Google Sheets Sync:** Row read/write checks and retry limits operate under high concurrency.
- [x] **AI Generation Engine:** Gemini prompt compiling and queue updates run without lockouts.
- [x] **Blogger publishing:** Blogger draft creation works.

---

## 3. Mobile UX & Branding Audit Results

We compared user experience metrics against the managed Streamlit Cloud version:

*   **Streamlit Logo / Menu:** 100% hidden. Custom Nginx proxy configurations successfully remove headers/footers, resulting in a cleaner UI.
*   **LINE WebView redirects:** Users tapping the LINE OA button successfully open the LINE app directly inside LINE Chat WebViews.
*   **State Latency:** Switch tabs and input responsiveness are fast and lag-free.

---

## 4. Final Recommendation

Based on the post-launch checks, **the self-hosted VPS instance (`https://app.getexpert.biz`) is highly stable, secure, and officially promoted to the Primary Production Environment.**

The managed Streamlit Cloud instance remains active as a hot-standby rollback fallback.
