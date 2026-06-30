# Sprint 1 Plan - Blogger MVP

รายละเอียดการดำเนินงานใน Sprint 1 สำหรับโครงการ **GetExpert AI Content Factory**

## เป้าหมายของ Sprint (Goal)
สร้างเครื่องมือประมวลผล Python Script ในแบบ Command Line Interface (CLI) ที่ทำงานผ่านสัญญานเรียกหลัก `python main.py` โดยทำงานครบรอบ Flow ดังนี้:
1. ดึงแถวคำสั่งที่มีสถานะ `Status = Waiting` จากตาราง Google Sheets
2. เรียกเขียนบทความภาษาไทยเชิงลึกตามหลักการทำ SEO ผ่าน Gemini API (1.5/2.5 Flash)
3. ส่งหัวข้อเรื่องและเนื้อหา HTML ไปอัปโหลดขึ้น Blogger แบบร่าง (Draft)
4. อัปเดตคอลัมน์ข้อมูลและสถานะกลับลง Google Sheets

## ขอบเขตการทำงาน (Scope)
### รวมอยู่ใน Sprint 1:
* การเชื่อมต่อและทำงานร่วมกับ Google Sheets API (อ่าน/เขียน/อัปเดต)
* การเรียกใช้ปัญญาประดิษฐ์สร้างข้อความผ่าน Gemini API (Structured JSON output ร่วมกับ Pydantic)
* การโพสต์แบบร่างใน Blogger REST API (isDraft=True)
* ระบบเก็บบันทึกประวัติและข้อความแสดงจุดบกพร่อง (Logging และ Error Handling)
* ระบบอนุญาตสิทธิ์การเข้าใช้งานผ่าน OAuth2 Consent (credentials.json และ token.json)

### คาดว่าจะพัฒนาใน Sprint ถัดไป (ยังไม่ทำใน Sprint นี้):
* ระบบเขียนคำโพสต์โซเชียลมีเดีย (Facebook, LINE OA)
* เซอร์วิสเว็บบอร์ด WordPress
* การวาดและแทรกภาพประกอบด้วย AI (AI Image Generation)
* การสร้างระบบฐานข้อมูลและการจัดการคิวงาน (Queue & Database)
* ส่วนติดต่อผู้ใช้งานประเภทเว็บแอปและแดชบอร์ด (Web Dashboard UI)

## ลำดับคอลัมน์ข้อมูลในตาราง Sheets
การจัดการระบบของแผ่นชีตจะเรียงลำดับคอลัมน์ตั้งแต่ A ถึง K ดังนี้:
* **A:** `ID` (รหัสประเด็น เช่น 1, 2, 3)
* **B:** `Topic` (หัวข้อบทความ)
* **C:** `Keyword` (คำสำคัญ)
* **D:** `Status` (สถานะงาน: `Waiting` / `Processing` / `Drafted` / `Error`)
* **E:** `Generated Title` (หัวข้อชื่อที่แต่งโดย AI)
* **F:** `Meta Description` (ย่อสรุปสำหรับทำ SEO)
* **G:** `Blogger Post ID` (รหัสโพสต์จาก Blogger)
* **H:** `Blogger URL` (ลิงก์ของบทความ)
* **I:** `Error Message` (ข้อความบอกจุดผิดพลาดหากงานขัดข้อง)
* **J:** `Created At` (เวลาบันทึกเรื่อง)
* **K:** `Updated At` (เวลาอัปเดตล่าสุด)
