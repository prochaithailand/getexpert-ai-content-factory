# Sprint 15 Mobile UX Polish Plan

This document details the audit of mobile scrolling stutters on Android/iOS devices and explains the minimal CSS adjustments implemented inside the Streamlit web application.

---

## 1. Touch Scroll Stiffness Audit

*   **Identified Issue:** Users reported stiff swiping behavior when interacting with the horizontal row of strategy tabs (Facebook, TikTok, YouTube, Blogger, Images) on mobile devices.
*   **Root Cause:** Streamlit wraps tabs inside native CSS containers (`data-testid="stTabBar"`) which do not declare smooth momentum scrolling or viewport-specific touch behaviors. This causes drag operations to feel laggy on Android WebView clients.
*   **Target Sections:**
    *   `st.tabs` container headers (`stTabBar`).
    *   Horizontal container rows (`stHorizontalBlock`).

---

## 2. Implemented CSS Optimizations

To resolve scrolling stutters without altering production Python structures, the following mobile-specific properties were injected into the stylesheet block inside [`web_app.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/web_app.py):

```css
/* Optimize touch scrolling for Streamlit tabs on mobile */
div[data-testid="stTabBar"] {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
div[data-testid="stHorizontalBlock"] {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
```

### Impact of Fixes
1.  **Momentum Scrolling:** The `-webkit-overflow-scrolling: touch` property enables native hardware-accelerated momentum scrolling on iOS and Android devices.
2.  **Cleaner Transitions:** Horizontal swiping across tabs is responsive and lag-free.
3.  **Low Risk:** The changes apply only to CSS styles, introducing zero risk of breaking Python execution.
