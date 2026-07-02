# แผนงาน Sprint 5: Client Delivery & AI Content Blueprint Strategy

การเปลี่ยนโฉมจากระบบผลิตบทความทั่วไป (**AI Content Generator**) สู่แพลตฟอร์มวางแผนยุทธศาสตร์คอนเทนต์ตามบริบทองค์กร (**AI Content Strategy Platform**) ผ่านนวัตกรรม **AI Content Blueprint**

## 1. วัตถุประสงค์
ปรับปรุงระบบให้รองรับผู้ใช้งานที่กว้างขวางขึ้น โดยไม่จำกัดเฉพาะผู้ค้าออนไลน์หรือธุรกิจ (SME) แต่รวมถึง:
1. **ธุรกิจ / สินค้า (Business / Product)**
2. **หน่วยงานราชการ (Government / Public Sector)**
3. **โครงการเพื่อสังคม / CSR (CSR / Social Impact)**
4. **การศึกษา (Education)**
5. **ประชาสัมพันธ์กิจกรรม (Event / Campaign PR)**
6. ** Personal Brand**

---

## 2. การเปลี่ยนแปลงสถาปัตยกรรมทางเทคนิค

### 2.1 ขยายฐานตารางข้อมูล Google Sheets (35 คอลัมน์)
ขยายช่วงคอลัมน์ A:AE (31 คอลัมน์) ออกไปเป็น **A:AI (35 คอลัมน์)** โดยต่อท้ายสุดเพื่อไม่ให้กระทบข้อมูลแถวเดิม (Backward Compatibility):
- **AF (31):** `Content Type` (เช่น `government`)
- **AG (32):** `Blueprint Label` (ป้ายชื่อภาษาไทย)
- **AH (33):** `Blueprint Inputs JSON` (ประวัติฟิลด์ไดนามิกในรูป JSON)
- **AI (34):** `Output Types` (รายการประเภทผลลัพธ์)

### 2.2 โครงสร้าง Dynamic Output Mapping
เพื่อความเข้ากันได้ย้อนหลังกับตาราง Google Sheets และ Blogger ปัจจุบัน ผลลัพธ์ทางโซเชียลมีเดียจะยังคงใช้โครงสร้าง 7 คีย์มาตรฐานของระบบหลังบ้าน (Facebook Post, Hashtags, TikTok Hook, TikTok Script, YouTube Shorts Script, Title, Description) แต่ระบบจะเปลี่ยน **ป้ายคำอธิบายบนหน้าเว็บ (UI Tab Labels) และสไตล์ภาษาของ Prompt** ให้สอดคล้องกับประเภท Blueprint นั้นๆ

### 2.3 การรีแฟกเตอร์ Master Prompt
ปรับปรุงระบบ Prompt ให้ผูก Rules, Role และ Focus Areas ของปัญญาประดิษฐ์ให้ต่างกันตามยุทธศาสตร์ของ Blueprint ที่ถูกเลือก เพื่อควบคุมไม่ให้มีการเขียนแบบ Hard Sell ในหมวดราชการ/การศึกษา/CSR

---

## 3. ขั้นตอนการดำเนินงาน (Implementation Phases)
- **Phase 1:** เพิ่ม Content Type Selector และผูก Blueprint Config
- **Phase 2:** สร้างหน้าจอกรอกข้อมูลแบบ Dynamic Forms (if/elif) บน Streamlit ทั้งใน Demo และ Standard Mode
- **Phase 3:** พัฒนา Prompt Strategy ปรับพฤติกรรมและการวาง Persona ของ Gemini API
- **Phase 4:** พัฒนาตัวปรับป้ายแถบผลลัพธ์แสดงผล (Dynamic Output Labels) ตามประเภทบลูปริ้นต์ที่เลือก
- **Phase 5:** ทดสอบการทำงานครบวงจรและตรวจเช็คความเข้ากันได้ย้อนหลัง
