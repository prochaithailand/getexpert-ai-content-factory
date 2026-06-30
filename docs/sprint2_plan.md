# Sprint 2 Plan - SEO, Retry & Image Prompt

แผนการดำเนินงานของ Sprint 2 สำหรับโครงการ **GetExpert AI Content Factory**

## เป้าหมายของ Sprint (Sprint Goal)
ยกระดับขีดความสามารถการเขียนบทความของระบบให้มีประสิทธิภาพดียิ่งขึ้น โดยเน้น 3 เรื่องหลัก:
1. **SEO Enhancement:** เพิ่มฟิลด์รายละเอียด SEO และหัวข้อประกอบเชิงลึก เช่น SEO Title, Slug, คีย์เวิร์ดรอง, สรุปใจความบทความ และคำถามที่พบบ่อย (FAQ)
2. **Retry Logic / Error Handling:** เพิ่มความเสถียรและความทนทานต่อความเสียหาย (Fault Tolerance) ในระดับแถวข้อมูล โดยระบบต้องสามารถทำงานแถวถัดไปต่อได้แม้ว่ามีบางแถวเกิดข้อขัดข้องชั่วคราว พร้อมมีกลไก Retry อัตโนมัติ 3 ครั้ง
3. **Featured Image Prompt:** ป้อนข้อมูลแนะนำองค์ประกอบและสร้าง Prompt สำหรับวาดรูปปกด้วย AI (Midjourney/DALL-E)

---

## รายละเอียดขอบเขตการทำงาน (Sprint Scope)
### ขอบเขตใน Sprint 2:
* ขยายโครงสร้างคอลัมน์ใน Google Sheets เป็น 20 คอลัมน์ (A:T)
* ปรับ Pydantic Data Models ให้ครอบคลุมฟิลด์ SEO และ Prompt รูปภาพหน้าปก
* ปรับปรุง prompt การเรียกปัญญาประดิษฐ์ให้ได้ข้อมูล SEO ครบถ้วน (คืนค่า JSON ตามโมเดล)
* สร้างโมดูล Retry `@retry` และติดตั้งเพื่อสยบปัญหาการสื่อสารขัดข้องชั่วคราว (Network Timeout / Rate Limit)
* รันการรันงานแบบ Row-by-Row Fault Tolerance (หากพัง ให้เปลี่ยนเป็นสถานะ `Failed` บันทึก Retry Count และ Last Error แล้วรันแถวต่อไปได้)

### นอกเหนือขอบเขต Sprint 2 (ยังไม่ทำ):
* การเชื่อมต่อโซเชียลเน็ตเวิร์ก (Facebook, LINE OA)
* บริการโพสต์อัตโนมัติบน WordPress
* บริการตั้งเวลาการรันงานผ่าน Scheduler System
* ฐานข้อมูลนอกเหนือจาก Google Sheets
* การยิงเจนรูปภาพจริง

---

## โครงสร้างคอลัมน์ตาราง Google Sheets (Sprint 2)
ตารางจะเรียงลำดับคอลัมน์ A ถึง T ดังนี้:
* **A:** `ID`
* **B:** `Topic`
* **C:** `Keyword`
* **D:** `Status` (Waiting / Processing / Drafted / Failed / Error)
* **E:** `SEO Title`
* **F:** `Meta Description`
* **G:** `Blogger Post ID`
* **H:** `Blogger URL`
* **I:** `Slug Suggestion`
* **J:** `Focus Keyword`
* **K:** `Related Keywords`
* **L:** `Content Summary`
* **M:** `Featured Image Prompt`
* **N:** `Image Style`
* **O:** `Image Concept`
* **P:** `Retry Count`
* **Q:** `Last Error`
* **R:** `Processed At`
* **S:** `Created At`
* **T:** `Updated At`

---

## รายละเอียดกลไก Retry Policy
* **สิทธิ์การลองรอบใหม่ (Max Retries):** พยายามรันซ้ำ 3 ครั้งหากพบปัญหา
* **การหน่วงเวลาระหว่างรอบ (Retry Delays):**
  - ล้มเหลวครั้งที่ 1: หน่วงเวลา 2 วินาที ก่อนรันรอบถัดไป
  - ล้มเหลวครั้งที่ 2: หน่วงเวลา 5 วินาที ก่อนรันรอบถัดไป
  - ล้มเหลวครั้งที่ 3: หน่วงเวลา 10 วินาที ก่อนรันรอบถัดไป
  - ล้มเหลวครั้งที่ 4 (ครบโควตา): ถือว่างานเสียหายจริง ส่งข้อผิดพลาดออกไปยังสคริปต์หลักเพื่อทำเครื่องหมายเป็น `Failed`
