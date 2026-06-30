# GetExpert AI Content Factory — Sprint 1 Blogger MVP (Completed ✅)

> **สถานะโครงการ:** Sprint 1 Blogger MVP สำเร็จเสร็จสมบูรณ์เรียบร้อยแล้ว (Completed)
> - **Runtime Test:** ผ่านการทดสอบ (PASSED)
> - **Stability Test:** ผ่านการทดสอบ (PASSED)
> - **จำนวนบทความแบบร่างสำเร็จ (Blogger Drafts):** 4 บทความ
> - **โฟลว์การทำงาน:** Google Sheets (Waiting) → Gemini API (แต่งบทความ) → Blogger API (อัปโหลด Draft) → Google Sheets (อัปเดตเป็น Drafted)

โครงการระบบ AI Content Factory ย้ายและพัฒนาระบบ Python สำหรับการประมวลผลดึงหัวข้อจาก Google Sheets แต่งบทความด้วย Gemini API และอัปโหลดไปยัง Blogger เป็นแบบร่าง (Draft) โดยอัตโนมัติ

---

## ขั้นตอนการติดตั้งและการตั้งค่าระบบ

### 1. การติดตั้งสภาพแวดล้อม (Python Setup)
1. เปิด Command Prompt หรือ Terminal ที่พาธโครงการ:
   ```bash
   cd c:\AI Automate\getexpert-ai-content-factory
   ```
2. สร้างสภาพแวดล้อมจำลอง (Virtual Environment):
   ```bash
   python -m venv venv
   ```
3. เปิดใช้งาน venv:
   - **Windows (Command Prompt):**
     ```cmd
     venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```
4. ติดตั้งไลบรารีที่จำเป็นทั้งหมด:
   ```bash
   pip install -r requirements.txt
   ```

---

### 2. การจัดเตรียม Google OAuth Credentials (credentials.json)
โปรแกรมจำเป็นต้องใช้สิทธิ์เชื่อมต่อ Google Sheets และ Blogger ผ่านบัญชี Google ของคุณ:

1. ล็อกอินเข้าใช้งาน [Google Cloud Console](https://console.cloud.google.com/)
2. สร้างโครงการใหม่ หรือ เลือกโครงการที่มีอยู่
3. ค้นหาและคลิกเปิดใช้งาน API (Enable API) ดังต่อไปนี้ในเมนู **API Library**:
   * **Google Sheets API**
   * **Blogger API v3**
4. ไปที่เมนู **OAuth consent screen** (หน้าจอความยินยอม OAuth):
   * เลือกประเภทเป็น **External**
   * ระบุรายละเอียดโครงการ เช่น ชื่อแอปพลิเคชัน และอีเมลสำหรับติดต่อ
   * ในขั้นตอน **Scopes**: ค้นหาและเลือกสิทธิ์:
     - `.../auth/spreadsheets`
     - `.../auth/blogger`
   * ในขั้นตอน **Test users**: **สำคัญมาก! ต้องเพิ่มอีเมล Google ของคุณเป็นผู้ทดสอบ (Test User)** เพื่อให้สามารถล็อกอินขอสิทธิ์ได้
5. ไปที่เมนู **Credentials**:
   * คลิก **Create Credentials** > เลือก **OAuth client ID**
   * เลือก Application type เป็น **Desktop App**
   * คลิก Create จากนั้นกดปุ่มดาวน์โหลดไฟล์ JSON (Download OAuth Client)
6. บันทึกไฟล์ที่ดาวน์โหลดมาลงในโฟลเดอร์โครงการนี้ และเปลี่ยนชื่อไฟล์เป็น **`credentials.json`**

---

### 3. การเตรียมตารางข้อมูลใน Google Sheets
สร้างตารางข้อมูลในชีตตามโครงสร้างคอลัมน์ A ถึง K ดังต่อไปนี้ (แถวแรกเป็น Header):

| คอลัมน์ | ชื่อหัวข้อคอลัมน์ (Headers) | คำอธิบาย |
| :---: | :--- | :--- |
| **A** | `ID` | รหัสบทความ (เช่น 1, 2, 3) |
| **B** | `Topic` | หัวข้อบทความหลัก |
| **C** | `Keyword` | คำสำคัญสำหรับเน้นการทำ SEO |
| **D** | `Status` | สถานะ ให้กรอกเป็น **`Waiting`** เพื่อรอประมวลผล |
| **E** | `Generated Title` | หัวข้อบทความสุดท้าย (แต่งโดย AI) |
| **F** | `Meta Description` | ข้อความสั้นๆ สำหรับ SEO (แต่งโดย AI) |
| **G** | `Blogger Post ID` | รหัสเอกสารจาก Blogger (บันทึกโดยสคริปต์) |
| **H** | `Blogger URL` | ลิงก์ที่อยู่ของบล็อกร่าง (บันทึกโดยสคริปต์) |
| **I** | `Error Message` | ข้อความแสดงสาเหตุปัญหาเมื่อเกิดข้อผิดพลาด (บันทึกโดยสคริปต์) |
| **J** | `Created At` | วันเวลาที่สร้างเรื่องบันทึกใน Sheet |
| **K** | `Updated At` | วันเวลาที่ระบบแก้ไขล่าสุด (บันทึกโดยสคริปต์) |

---

### 4. การจัดทำไฟล์กำหนดคีย์ระบบ (.env)
1. คัดลอกไฟล์ `.env.example` ไปจัดสร้างไฟล์ใหม่ชื่อ **`.env`** ในโฟลเดอร์โครงการ:
   ```bash
   copy .env.example .env
   ```
2. เปิดไฟล์ `.env` และกำหนดตัวแปรให้ครบถ้วน:
   * `GEMINI_API_KEY`: API Key ของ Gemini (รับฟรีได้ที่ [Google AI Studio](https://aistudio.google.com/))
   * `GEMINI_MODEL`: รุ่นโมเดล แนะนำเป็น `gemini-2.5-flash`
   * `GOOGLE_SHEET_ID`: รหัสไอดีจาก URL หน้า Google Sheets ของคุณ
   * `BLOGGER_BLOG_ID`: รหัส Blog ID จาก URL หน้าคอนโซลของ Blogger

---

### 5. วิธีการทดสอบรันระบบ (Manual Execution)
1. ตรวจสอบว่าในชีต มีแถวจำลองข้อมูลที่ใส่ค่า `Status = Waiting` และมี Topic กับ Keyword เรียบร้อยแล้ว
2. รันคำสั่งหลักผ่าน Terminal:
   ```bash
   python main.py
   ```
3. **สำหรับการรันครั้งแรก:** สคริปต์จะเปิดเว็บบราวเซอร์ขึ้นมา ให้คลิกเลือกบัญชี Google ของคุณ > กด **Advanced** > คลิกลิงก์ **Go to ... (unsafe)** > กด **Allow** เพื่อตกลงยินยอมการเข้าถึงข้อมูล
4. สคริปต์จะทำการอัปโหลดโทเคนการล็อกอินเข้าระบบไว้ในไฟล์ `token.json` เพื่อใช้รันอัติโนมัติในครั้งถัดไป
5. ตรวจสอบสถานะการทำงานในหน้า Terminal:
   - สคริปต์จะสแกนหาเฉพาะแถวที่เป็น `Waiting`
   - ทำการล็อกสถานะแถวใน Sheet เป็น `Processing`
   - เรียกให้ GeminiAPI แต่งบทความ
   - นำไปบันทึกเป็น Draft ใน Blogger (ยังไม่ Publish สาธารณะ)
   - อัปเดตข้อมูลลิงก์ ผลลัพธ์ และสถานะเป็น `Drafted` กลับลงแผ่นชีต
6. คุณสามารถเปิดดูบันทึกข้อความการทำงานทั้งหมดได้ที่หน้าโฟลเดอร์โครงการในไฟล์ **`logs/app.log`**
