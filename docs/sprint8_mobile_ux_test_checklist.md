# Sprint 8 Mobile UX Testing Checklist

This checklist is used to perform Quality Assurance (QA) on mobile devices for the self-hosted Streamlit deployment, verifying UI cleanups, query param flows, and payment gate interactions.

---

## 1. UI Elements & Header Verification
- [ ] Open `https://app.getexpert.biz` on a mobile device (Safari / Chrome Mobile).
- [ ] **Streamlit Header Hidden:** Check that the top Streamlit deploy button, main menu, and viewer badges are hidden.
- [ ] **Streamlit Footer Hidden:** Scroll to the bottom and ensure the "Made with Streamlit" watermark is hidden.
- [ ] **No Floating Controls:** Check that no default streamlit floating widget icons overlay the screen.

---

## 2. In-App Mobile Browser Tests
Test page loading and WebSockets connectivity inside standard mobile social network browsers:
- [ ] **LINE In-App Browser:** Send the URL inside a LINE chat, click it to open, and check that the WebSocket does not get stuck in a "Connecting..." loop.
- [ ] **Facebook In-App Browser:** Share the link on Facebook, open it, and verify that the page renders and permits form inputs.

---

## 3. Referral URL Capture (`?ref=CODE`)
- [ ] Open the referral link on mobile:
  `https://app.getexpert.biz/?ref=PROCHAIT001`
- [ ] **No Crash:** Ensure the page loads without any `Segmentation fault` or Streamlit Cloud visual error pages.
- [ ] **Referrer Caption:** Verify that the header displays:
  `👋 คุณเข้าใช้งานผ่านลิงก์ผู้แนะนำ: PROCHAIT001`
- [ ] **Safe Verification:** Enter an email address, click **🔍 ตรวจสอบเครดิตและสิทธิ์ใช้งาน**, and confirm that the user registers under the correct referrer code inside the sheets database.

---

## 4. Payment Gate & LINE OA Button Interaction
- [ ] Verify the payment QR code fits the mobile screen width nicely (does not trigger horizontal page overflow).
- [ ] Tap the green HTML button **💬 เปิด LINE OA เพื่อส่งสลิป**:
  *   Check that the button opens `https://lin.ee/TZgX4CD`.
  *   Confirm that it does NOT get blocked by the WebView's default pop-up blocker (since it uses `target="_self"`).
- [ ] **Fallback Copy Box:** Ensure the copy-paste box displays the URL correctly. Long-press to copy the fallback URL `https://lin.ee/TZgX4CD` to verify touch interactivity.

---

## 5. My Content History Card Tests
- [ ] Tap **📚 ดูคอนเทนต์ที่เคยสร้าง** to load user history.
- [ ] Verify that history cards wrap details correctly without text clippings.
- [ ] Open a card's expander **🔍 ดูรายละเอียดผลลัพธ์ Content Pack**:
  *   Slide tabs horizontally to ensure all 5 outputs (Blogger, Facebook, TikTok, YouTube, Images) are selectable.
  *   Tap the copy button inside the code blocks (`st.code`) and verify that content is copied to the mobile clipboard.
