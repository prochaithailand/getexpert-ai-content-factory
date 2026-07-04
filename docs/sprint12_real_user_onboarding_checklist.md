# Sprint 12 Real User Onboarding Checklist

This document details the checklist to onboard 3–10 initial real testers to the self-hosted VPS portal, guiding them through standard operations, paid paths, and feedback loops.

---

## Onboarding Execution Checklist

### Phase 1: Pre-onboarding Setup
- [ ] Verify VPS health status and clear active logs.
- [ ] Confirm the domain CNAME `app.getexpert.biz` is pointing to the VPS.
- [ ] Prepare invitation scripts.

### Phase 2: Tester Selection & Outreach
- [ ] Invite 3–10 target testers via LINE OA.
- [ ] Provide the URL: `https://app.getexpert.biz`.
- [ ] Instruct users to register using their active work emails.

### Phase 3: Onboarding Validation Tasks
Ask users to perform the following actions:
- [ ] **First Login:** Enter email and verify that "3 free credits" display on the gate balance.
- [ ] **Content strategy build:** Input topic keywords and verify strategy pack generates.
- [ ] **Copy Result:** Open generated result card and copy outputs to their mobile device clipboard.
- [ ] **Deplete Credits:** Generate 2 more packs to exhaust free trial credits.
- [ ] **Payment QR Gate:** Confirm that the Payment Gate is displayed once credit balance is zero.

### Phase 4: Paid Flow & Verification
- [ ] Ask 1 or 2 users to simulate the 99 Baht purchase.
- [ ] User taps **💬 เปิด LINE OA เพื่อส่งสลิป** to send their slip and email to the admin.
- [ ] Admin searches email, verifies payment, and deposits credit balance.
- [ ] User refreshes `https://app.getexpert.biz` and verifies **10 Content Credits** are successfully credited.

### Phase 5: Feedback Gathering
- [ ] Send the user feedback questionnaire link via LINE OA.
- [ ] Review responses and record any bugs inside the issue logs template.
