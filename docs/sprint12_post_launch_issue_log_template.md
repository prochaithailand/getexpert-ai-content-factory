# Sprint 12 Post-Launch Issue Log Template

This document provides a template for capturing, prioritizing, tracking, and resolving technical or usability issues reported by real users after the public launch.

---

## 1. Active Issue Log Table

| Issue ID | Date | Reporter / Device | Issue Description & Details | Severity | Status | Resolution / Action Taken |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ISSUE-001**| *04/Jul*| *test@gmail.com / iOS LINE* | *Example: WebSocket disconnects after 45s during long Content Pack build.* | *High* | *Resolved* | *Increased proxy_read_timeout in Nginx to 600s.* |
| **ISSUE-002**| - | - | - | - | - | - |
| **ISSUE-003**| - | - | - | - | - | - |

---

## 2. Severity Classification Definitions

To prioritize bug fixes, classify issues using the following definitions:

*   **Critical:**
    *   *Definition:* Causes app crash, server memory exhaustion (OOM), database lockups, or prevents users from loading the URL or registering.
    *   *Action:* Revert immediately to Streamlit Cloud using the Rollback Plan and investigate VPS.
*   **High:**
    *   *Definition:* A core feature fails (e.g. Gemini generation locks, LINE redirect fails, or payment slips cannot be deposited).
    *   *Action:* Resolve within 12–24 hours on VPS candidate.
*   **Medium:**
    *   *Definition:* Visual rendering flaws on specific mobile devices (e.g. QR code overflows screen margins, or tab layout horizontal swipe sticks).
    *   *Action:* Schedule patch during next minor update cycle.
*   **Low:**
    *   *Definition:* Typos, small spelling corrections in captions, or request for additional blueprint styles.
    *   *Action:* Group with upcoming sprint features.
