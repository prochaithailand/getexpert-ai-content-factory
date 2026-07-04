# Sprint 13 Tester Task Checklist

This checklist defines the series of user actions requested from each pilot tester to comprehensively validate the VPS application's core functions and payment paths on mobile viewports.

---

## Tester Tasks Checklist

- [ ] **Task 1: Load Webpage**
  *   Open `https://app.getexpert.biz` on your smartphone browser (Chrome/Safari) or inside the LINE chat WebView.
  *   *Audit:* Check that page load is fast and does not trigger WebSocket connection retry boxes.

- [ ] **Task 2: Interface Inspection**
  *   Scroll top-to-bottom.
  *   *Audit:* Confirm that there are no floating Streamlit deploy buttons or bottom branding watermarks.

- [ ] **Task 3: Registration & Credits Check**
  *   Enter your active work email, click **🔍 ตรวจสอบเครดิตและสิทธิ์ใช้งาน**.
  *   *Audit:* Confirm that the credit status label displays: `สิทธิ์คงเหลือ: 3 Content Credits` (or displays correct historical paid credits).

- [ ] **Task 4: Run First Strategy Pack**
  *   Select a Content Blueprint (e.g. Social Post), enter keyword topic, click form submit.
  *   *Audit:* Wait for the loader to finish. Verify that strategy tabs (Blogger, Facebook, etc.) render.

- [ ] **Task 5: Content Verification & Copying**
  *   Slide strategy tabs horizontally. Click the copy icon inside the code container.
  *   *Audit:* Verify that the text successfully copies to your phone's clipboard.

- [ ] **Task 6: Deplete Trial Balance**
  *   Generate 2 additional content strategies.
  *   *Audit:* Confirm that on the 4th attempt, the system renders the **Payment Gate** and blocks new inputs.

- [ ] **Task 7: Payment & Contact Verification**
  *   Review the payment QR instructions.
  *   *Audit:* Verify the QR image fits the mobile viewport.
  *   *Action:* Tap the green CTA button **💬 เปิด LINE OA เพื่อส่งสลิป**. Confirm it redirects directly to `https://lin.ee/TZgX4CD` and launches the LINE chat application.
