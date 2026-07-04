# Sprint 11 CTA Link Audit Checklist

This audit checklist is used to verify that all primary call-to-action (CTA) buttons on the sales/marketing Landing Page (`getexpert.biz`) have been redirected to point to the new self-hosted app URL at `https://app.getexpert.biz`.

---

## 1. Landing Page CTA Audit Table

Verify each section of the main landing page (`getexpert.biz`):

| Section | CTA Button Label | Target Link URL | Audit Status |
| :--- | :--- | :--- | :--- |
| **Hero Section (Top)** | "🚀 เริ่มต้นใช้งานฟรี" | `https://app.getexpert.biz` | - |
| **Mid-Page Strategy Section**| "✨ สร้าง Content Pack แรกของคุณ" | `https://app.getexpert.biz` | - |
| **Pricing Package Section**  | "💳 สมัครใช้งานเลย" | `https://app.getexpert.biz` | - |
| **Final Call-to-Action**     | "🔥 เริ่มต้นตอนนี้" | `https://app.getexpert.biz` | - |
| **Footer Links (Bottom)**    | "Factory Portal" | `https://app.getexpert.biz` | - |

---

## 2. Validation Steps
- [ ] Open a browser in **Incognito/Private Mode** (to bypass DNS and local cache redirection errors).
- [ ] Navigate to the landing page `https://getexpert.biz`.
- [ ] Individually hover and click every button in the table above.
- [ ] Confirm that each click successfully opens `https://app.getexpert.biz` in the viewport.
- [ ] Search the landing page HTML code for any remnant references to `streamlit.app` to ensure no outdated links are left.
