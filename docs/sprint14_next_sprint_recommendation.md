# Sprint 14 Next Sprint Recommendations

This document provides recommendations for the next sprint based on visual audits, user feedback, and operational findings during the no-Streamlit-logo user trials.

---

## 1. Identified Technical Priorities

Based on the Sprint 14 trial feedback:
*   **Willingness to Purchase:** Reconfirmed. The professional look (custom domains and hidden logos) makes users highly comfortable with manual QR transfers.
*   **Feature Request (Niche Blueprints):** The most common request was **adding E-commerce, Instagram Carousel, and localized Maps SEO articles blueprints**.
*   **Stiffness Fixes:** Minor Android swipe lag was reported when sliding through the output cards.

---

## 2. Proposed Next Sprint (Sprint 15)

### Option A (Recommended): Content Blueprints Expansion & Mobile UX Polish
*   **Goal:** Expand the available blueprints and apply minor CSS tweaks to resolve scroll/swipe lag on mobile.
*   **Scope:**
    1.  Add new blueprint categories inside `services/blueprint_service.py` (Instagram Carousel, Google Maps local store profile optimization, and E-commerce description prompts).
    2.  Polish mobile card layout CSS parameters (add `-webkit-overflow-scrolling: touch` properties to result tabs).
    3.  Correct the Blogger draft insert spelling typos.
*   **Impact:** Directly addresses user feature requests, improves immediate mobile UX, and builds conversion value before starting backend API refactoring.

### Option B: Backend REST APIs & FastAPI Extraction
*   **Goal:** Extract Sheets service, credit verifier, and Gemini interfaces into FastAPI endpoints.
*   **Impact:** Good for code safety, but does not add immediate business value or new features to users.
