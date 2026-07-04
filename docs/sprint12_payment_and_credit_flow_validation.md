# Sprint 12 Payment & Credit Flow Validation Report

This report documents the verification of the GetExpert AI Content Factory payment gates and credit depletion rules inside the self-hosted VPS production candidate.

---

## 1. Free Trial Depletion Audit

*   **Rule Verified:** Every new email address receives **3 free trial credits** upon initial registration.
*   **Depletion Mechanics:**
    1.  *First Generation:* Balance reduces from 3 to 2.
    2.  *Second Generation:* Balance reduces from 2 to 1.
    3.  *Third Generation:* Balance reduces from 1 to 0.
    4.  *Fourth Attempt:* Generation is blocked. The screen renders the payment instructions and locks access to strategy inputs.
*   **Verification Status:** ✅ Passed. Verified database log entries on Google Sheets `Usage Logs` columns decrement properly.

---

## 2. Paid Credit Top-up Flow Audit

*   **Rule Verified:** 99 THB = 10 Content Credits (no expiration date).
*   **Payment Gate UX:**
    - [x] QR code renders properly on mobile.
    - [x] Green HTML button **💬 เปิด LINE OA เพื่อส่งสลิป** opens direct support chat in same tab without WebView popup blocker warnings.
    - [x] Text backup container displays the verified contact link `https://lin.ee/TZgX4CD`.
*   **Admin Deposit Mechanism:**
    1.  Admin receives slip + user email in LINE OA.
    2.  Admin searches for the user email in the Admin Portal.
    3.  Admin deposits the payment, allocating **10 credits** to the balance.
    4.  *Sheet Write:* Updates `Payments` worksheet and adds a transaction entry.
*   **Verification Status:** ✅ Passed. Top-up deposits immediately reflect in the database and unlock the user's strategist UI.
