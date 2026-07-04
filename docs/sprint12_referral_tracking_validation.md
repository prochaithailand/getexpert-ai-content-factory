# Sprint 12 Referral Tracking Validation Report

This report documents the verification of the query parameter parsing, sanitization, UI headers rendering, and Sheets logs mapping of the referral partner system inside the self-hosted production candidate.

---

## 1. Query Parameter Interception & State Management

*   **URL Tested:** `https://app.getexpert.biz/?ref=PROCHAIT001`
*   **State Capture:** The Streamlit app successfully parses the query parameter `ref` on startup and stores it inside `st.session_state.referred_by`.
*   **Visual confirmation:** The top of the page displays a green alert box:
    `👋 คุณเข้าใช้งานผ่านลิงก์ผู้แนะนำ: PROCHAIT001`
*   **Verification Status:** ✅ Passed.

---

## 2. Sanitization Security Audit

To ensure the referral gate cannot be bypassed or exploited, sanitization rules were validated:

*   **Test Case 1 (Special Characters):** Opening `?ref=PROCH@IT001` sanitizes characters and logs `PROCHIT001` using standard regex formatting (`[^A-Za-z0-9_\-]`).
*   **Test Case 2 (SQL Injection / script blocks):** Opening `?ref=1'%20OR%20'1'='1` or `?ref=<script>` strips invalid query codes safely.
*   **Verification Status:** ✅ Passed. Sanitization blocks segmentations crashes on the VPS.

---

## 3. Google Sheets Integration Log Audit

When a user registers under a referral code:
1.  Admin verifies credit Top-up balance.
2.  Google Sheets `Users` worksheet writes `PROCHAIT001` to the **Referred By** column.
3.  Google Sheets `Referral Logs` worksheet records a commission entry allocating **20 Baht** to the referrer.
4.  **Verification Status:** ✅ Passed. No database locks were detected.
