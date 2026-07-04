# Sprint 9 Mobile UX Validation Report

This document audits the mobile user experience of the self-hosted Streamlit app, validating interface elements, WebView redirects, content copier behaviors, and referral URL tracking.

---

## 1. Browser & WebView Testing Matrix

The self-hosted deployment was tested across key mobile environments to ensure WebSocket compatibility:

| Mobile Client | OS | Status | Description |
| :--- | :--- | :--- | :--- |
| **Safari Mobile** | iOS 17.4 | ✅ Passed | Zero UI lag; rendering is fluid. |
| **Chrome Mobile** | Android 14 | ✅ Passed | Fits mobile viewport width. |
| **LINE In-App Webview** | iOS & Android | ✅ Passed | Upgrade headers resolved. No WebSocket connection loops. |
| **Facebook Webview** | iOS & Android | ✅ Passed | No security warnings or blocked pop-ups. |

---

## 2. LINE OA Button & Fallback Redirects

The custom HTML anchor button with `target="_self"` successfully bypassed pop-up blockers:

*   **Tapping "💬 เปิด LINE OA เพื่อส่งสลิป":** Automatically redirects the current mobile window to the custom LINE shortlink `https://lin.ee/TZgX4CD`.
*   **LINE Protocol Redirect:** Successfully launches the native LINE application on the mobile phone, starting the direct chat window with `@774dfect`.
*   **Fallback copy-paste block:** The styled code container `https://lin.ee/TZgX4CD` rendered cleanly. Copying works via standard long-press.

---

## 3. Referral URL Capture Validation

We validated opening the URL parameter on mobile devices:
`https://app.getexpert.biz/?ref=PROCHAIT001`

*   **Startup Stability:** The application loaded immediately without triggering Streamlit process core dumps or segmentation faults.
*   **Visual Confirmation:** The header successfully displays:
    `👋 คุณเข้าใช้งานผ่านลิงก์ผู้แนะนำ: PROCHAIT001`
    This provides confirmation to users that they have entered through a referrer link.
*   **Form Registration:** Submitting user email registers the `Referred By` column with `PROCHAIT001` on the Google Sheets `Users` worksheet.

---

## 4. History Cards & Layout Responsiveness

-   **Code Copying:** The copy button in `st.code` blocks copied text to the mobile clipboard.
-   **Output Tabs:** The five tabs (Blogger, Facebook, TikTok, YouTube, Images) dynamically resize. Users can swipe horizontally to select tabs.
-   **Blogger Redirect:** Tapping **[คลิกเปิดร่างบทความใน Blogger]** opens Blogger draft posts in a new browser tab.
