# Sprint 10 Controlled Beta Test Plan

This document outlines the testing parameters, user invitations, onboarding steps, and system logs monitoring to run a controlled beta test of the self-hosted VPS candidate with 3–5 real users.

---

## 1. Beta User Selection Criteria

For the trial, select **3 to 5 real users** who meet the following criteria:
1.  Are active users of the GetExpert AI Content Factory (with at least 2 Content Packs generated in the past).
2.  Access the application primarily using mobile devices (iOS/Safari or Android/Chrome).
3.  Have previously communicated with the LINE OA support channel.

---

## 2. Onboarding & Invitation Script

Send the following invitation template to the selected testers via LINE OA:

> **สวัสดีครับ [ชื่อผู้ใช้งาน]!** 🙏
>
> ทีมงานขอเชิญคุณเข้าร่วมทดสอบระบบ GetExpert AI Content Factory เวอร์ชันใหม่ล่าสุด (เวอร์ชันอัปเกรดเพื่อประสิทธิภาพที่ดีขึ้นบนมือถือ)
> 
> *   **ลิงก์เข้าร่วมทดสอบ:** [https://app.getexpert.biz](https://app.getexpert.biz)
> *   **จุดประสงค์การทดสอบ:** 
>     1. ทดสอบการเข้าใช้งานและความรวดเร็วในการเปิดหน้าเว็บ
>     2. ทดสอบความไหลลื่นในการแสดงผลและการดึงข้อมูลประวัติคอนเทนต์บนอุปกรณ์มือถือของคุณ
>     3. สังเกตว่าเมนูสติกเกอร์/แถบเครื่องมือของระบบเดิม (Streamlit logo หรือปุ่ม Deploy ด้านบน) ถูกซ่อนออกไปเรียบร้อยแล้วหรือไม่
> 
> หากพบปัญหาในการเชื่อมต่อ หรือปุ่มชำระเงินไม่ทำงาน สามารถแจ้งกลับแอดมินในแชทนี้ได้ทันทีเลยครับ ขอบคุณที่ร่วมช่วยพัฒนาครับ! 🚀

---

## 3. Operations & Logs Monitoring Protocol

While beta testing is active, the system administrator must perform the following monitoring steps:

### Container Runtime Inspection
Keep a live tail terminal open on the Hostinger VPS to capture runtime anomalies:
```bash
# Monitor only errors or connection timeouts
docker compose logs -f --tail=100 | grep -E "ERROR|WARNING|Exception"
```

### Database Verification
Audit Google Sheets worksheets after each user action:
- [ ] **Registration Verification:** Confirm email entry creates a row in `Users` with the correct referred-by code (if they entered via a referral link).
- [ ] **Deduction Verification:** Verify that generating a pack decreases `Paid Credits Balance` by 1 and increases `Total Generated` in the database.
- [ ] **Queue Processing:** Verify the background python worker process successfully transitions row status from `Waiting` -> `Processing` -> `Drafted`.
