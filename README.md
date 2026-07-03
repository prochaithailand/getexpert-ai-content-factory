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
สร้างตารางข้อมูลในชีตตามโครงสร้างคอลัมน์ A ถึง T ดังต่อไปนี้ (แถวแรกเป็น Header):

| คอลัมน์ | ชื่อหัวข้อคอลัมน์ (Headers) | คำอธิบาย |
| :---: | :--- | :--- |
| **A** | `ID` | รหัสบทความ (เช่น 1, 2, 3) |
| **B** | `Topic` | หัวข้อบทความหลัก |
| **C** | `Keyword` | คำสำคัญสำหรับเน้นการทำ SEO |
| **D** | `Status` | สถานะ ให้กรอกเป็น **`Waiting`** เพื่อรอประมวลผล |
| **E** | `SEO Title` | ชื่อหัวข้อสำหรับเสิร์ชเอนจิ้น ความยาวไม่เกิน 60 ตัวอักษร (แต่งโดย AI) |
| **F** | `Meta Description` | ข้อความสรุปสั้นขนาด 120-150 ตัวอักษรสำหรับทำ SEO (แต่งโดย AI) |
| **G** | `Blogger Post ID` | รหัสเอกสารจาก Blogger (บันทึกโดยสคริปต์) |
| **H** | `Blogger URL` | ลิงก์ที่อยู่ของบล็อกร่าง (บันทึกโดยสคริปต์) |
| **I** | `Slug Suggestion` | ส่วนท้ายลิงก์แนะนำภาษาอังกฤษคั่นด้วยขีดกลาง (แต่งโดย AI) |
| **J** | `Focus Keyword` | คีย์เวิร์ดหลักของบทความ (แต่งโดย AI) |
| **K** | `Related Keywords` | รายการคำสำคัญรอง 3-5 คำ (แต่งโดย AI) |
| **L** | `Content Summary` | สรุปเนื้อความย่อของบทความ (แต่งโดย AI) |
| **M** | `Featured Image Prompt` | Prompt ภาษาอังกฤษสำหรับใช้เจนรูปปก AI (แต่งโดย AI) |
| **N** | `Image Style` | สไตล์ภาพประกอบหน้าปกแนะนำ (แต่งโดย AI) |
| **O** | `Image Concept` | แนวคิดคอนเซ็ปต์ของภาพปก (แต่งโดย AI) |
| **P** | `Retry Count` | จำนวนรอบที่ทำการพยายามทำใหม่ (0 กรณีสำเร็จ, 3 กรณีล้มเหลว) |
| **Q** | `Last Error` | ข้อความระบุสาเหตุข้อผิดพลาดเมื่อบทความรันพัง |
| **R** | `Processed At` | วันและเวลาที่บทความประมวลผลอัปโหลดขึ้น Blogger สำเร็จ |
| **S** | `Created At` | วันเวลาที่สร้างแถวหัวข้อใน Sheet |
| **T** | `Updated At` | วันเวลาที่สคริปต์หรือผู้ใช้แก้ไขแถวล่าสุด |

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

---

### 6. วิธีการเปิดใช้งานเว็บแอป Streamlit (Web Form UI Portal)
1. ตรวจสอบให้แน่ใจว่าเปิดใช้สภาพแวดล้อมจำลอง (venv) และสั่งรันบริการเว็บแอปพลิเคชัน:
   ```bash
   streamlit run web_app.py
   ```
2. ระบบจะเปิดเว็บเบราว์เซอร์ชี้ไปที่พาธ `http://localhost:8501` โดยอัตโนมัติ
3. คุณสามารถกรอกหัวข้อ (Topic) และคำสำคัญหลัก (Keyword) และกดปุ่มเพื่อจองคิวลงชีต จากนั้นสามารถติดตามความคืบหน้าในส่วน Status Tracker หรือดูคิวงานทั้งหมดได้ในหน้าจอตารางแดชบอร์ดด้านล่างสุด

---

### 7. วิธีการใช้งานในโหมดเดโมสำหรับลูกค้า (Demo Mode / Client Trial)
1. เมื่อเปิดรันบริการเว็บแอป Streamlit เรียบร้อยแล้ว ให้เปิดลิงก์ผ่านเว็บเบราว์เซอร์และต่อท้ายพารามิเตอร์ดังนี้:
   ```text
   http://localhost:8501/?demo=true
   ```
2. หน้าจอเว็บจะปรับเป็นโหมดเดโมสำหรับลูกค้าทันที (ซ่อนส่วนตารางคิวงานและแดชบอร์ดผู้ดูแลระบบทั้งหมด)
3. เมื่อป้อนข้อมูลแบรนด์และกดปุ่ม **🚀 สร้าง Content Pack ทันที** ระบบจะใช้บริการประมวลผลทันที (Synchronous Generation) โดยเรียก Gemini API และ Blogger API เพื่อสร้างและแสดงผลบทความพร้อมโซเชียลโพสต์และสคริปต์ 5 แท็บแบบเรียลไทม์ภายใน 15-20 วินาที เพื่อการทดลองใช้ที่สะดวกรวดเร็วที่สุดครับ

---

### 8. การติดตั้งใช้งานบน Streamlit Cloud (Streamlit Secrets)
เพื่อความปลอดภัย ข้อมูลความลับ `credentials.json` และ `token.json` ต้องห้ามถูกกด Commit บันทึกขึ้นบน GitHub โดยเด็ดขาด เมื่อทำการ Deploy ระบบบน **Streamlit Cloud** ให้เข้าไปตั้งค่าข้อมูลที่ความลับระบบผ่านหน้าต่างเมนู **App settings > Secrets** และคัดลอกข้อมูลในรูปแบบดังนี้:

```toml
GEMINI_API_KEY = "ป้อน API Key ของคุณ"
GEMINI_MODEL = "gemini-2.5-flash"
GOOGLE_SHEET_ID = "ป้อน Spreadsheet ID ของคุณ"
GOOGLE_SHEET_NAME = "Sheet1"
BLOGGER_BLOG_ID = "ป้อน Blogger Blog ID ของคุณ"

# คัดลอกข้อความในไฟล์ credentials.json ทั้งหมดมาแปะในช่องนี้
GOOGLE_CREDENTIALS_JSON = """
{
  "web": {
    "client_id": "...",
    "project_id": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "...",
    "redirect_uris": ["http://localhost:59938/"]
  }
}
"""

# คัดลอกข้อความในไฟล์ token.json ทั้งหมดมาแปะในช่องนี้
GOOGLE_TOKEN_JSON = """
{
  "token": "...",
  "refresh_token": "...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "...",
  "client_secret": "...",
  "scopes": ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/blogger"],
  "universe_domain": "googleapis.com",
  "expiry": "2026-07-02T10:00:00.000000Z"
}
"""

LOG_LEVEL = "INFO"
```

---

### 9. ระบบ AI Content Blueprint (Sprint 5)
ใน Sprint 5 ระบบได้รับการยกระดับเป็น **AI Content Strategy Platform** โดยสามารถปรับฟอร์มกรอกข้อมูลและยุทธศาสตร์การเขียนของ AI ให้ต่างกันตามประเภทเนื้อหา 6 รูปแบบหลัก ได้แก่:
1. **ธุรกิจ / สินค้า (Business / Product):** เน้นเสนอคุณค่าของผลิตภัณฑ์ กระตุ้นยอดขาย (Conversion) และมีคำเชิญชวนแบบปิดการขาย (CTA)
2. **หน่วยงานราชการ (Government):** ใช้ภาษาสุภาพ เป็นทางการ เข้าใจง่าย น่าเชื่อถือ **ไม่มีการ Hard Sell เชิงพาณิชย์** เน้นส่งต่อข้อมูลสิทธิประโยชน์แก่ประชาชน
3. **โครงการเพื่อสังคม / CSR (CSR):** ปลุกใจ สร้างแรงบันดาลใจ ส่งเสริมการร่วมมือและเห็นอกเห็นใจผู้อื่น ชู Impact สังคม
4. **การศึกษา (Education):** ข้อมูลวิชาการถูกต้อง โครงสร้างลำดับขั้นตอนชัดเจน เข้าใจง่าย เหมาะกับการศึกษาแบ่งปันความรู้
5. **ประชาสัมพันธ์กิจกรรม (Event):** น้ำเสียงกระตือรือร้น เชิญชวนร่วมอีเวนต์ ชี้วันเวลาสถานที่และช่องทางจองบัตรลงทะเบียนครบถ้วน
6. **Personal Brand:** เขียนแนวเล่าเรื่อง (Storytelling) แสดงความเป็นผู้นำทางความคิด (Thought Leadership) ผ่านประสบการณ์ตรงอย่างจริงใจ

**ฟีเจอร์เด่น:**
- **Dynamic Form Fields:** แบบฟอร์มใน Streamlit จะปรับโครงสร้างช่องข้อมูลให้อัตโนมัติทันทีที่เลือกประเภทงาน
- **Dynamic UI Tabs:** แถบคำอ่านผลลัพธ์ (เช่น ข่าวประชาสัมพันธ์, สคริปต์สั้นแจ้งประชาชน) จะสลับคำอธิบายให้สอดคล้องกับยุทธศาสตร์บลูปริ้นต์
- **35 Columns Support:** Google Sheets ขยายเพิ่มเป็นช่วง `A:AI` โดยปลอดภัยต่อแถวข้อมูลเก่าของรุ่นเดิม 100%
- **Unit Tests:** ทดสอบสถาปัตยกรรมบลูปริ้นต์ได้ง่ายๆ ผ่านคำสั่ง `python -m unittest tests/test_blueprints.py`

---

### 10. ระบบจำกัดสิทธิ์เครดิตและช่องทางชำระเงิน (Sprint 6: Credit Gate & Paid Usage System)
ใน Sprint 6 ระบบได้เพิ่มระบบจำกัดจำนวนการสร้างฟรีเพื่อพร้อมสำหรับการให้บริการเชิงพาณิชย์:
- **สิทธิ์ทดลองใช้ฟรี (Free Trial):** ผู้ใช้งานสามารถสร้าง Content Pack ฟรีได้ 3 ครั้งแรก (อ้างอิงตาม Email)
- **ระบบเครดิตซื้อเพิ่ม (Paid Credits):** เมื่อใช้สิทธิ์ฟรีครบแล้ว ระบบจะสลับมาตรวจสอบเครดิตเติมเงินคงเหลือ (ครั้งละ 1 เครดิตต่อการสร้างสำเร็จ) หากไม่มีเครดิตจะแสดงหน้าจอช่องทางชำระเงิน (Payment Gate) เพื่อชำระเงินซื้อเครดิตเพิ่มเติม
- **ราคาแพ็กเกจ:** แพ็กเริ่มต้น 99 บาท ได้รับ 10 Content Credits (1 Credit = สร้าง Content Pack ครบชุด 1 ครั้ง)
- **การแจ้งชำระเงินจริง (Manual Payment):** 
  - สแกน QR Code ชำระเงินจริงจากไฟล์รูปภาพที่ [assets/payment_qr.png](file:///c:/AI%20Automate/getexpert-ai-content-factory/assets/payment_qr.png)
  - แจ้งยืนยันการโอนเงินและส่งสลิปพร้อมแจ้ง Email ในระบบมาที่ LINE OA: **@774dfect** (หรือกดลิงก์ [https://lin.ee/774dfect](https://lin.ee/774dfect))
  - แอดมินจะอัปเดตสิทธิ์เครดิตลงใน Google Sheets แผ่น `Users` เพื่อเติมโควตาเครดิตให้ลูกค้าโดยตรง
- **ความปลอดภัยโควตา:** จะไม่มีการหักแต้มเครดิตล่วงหน้า หรือ หักเครดิตซ้ำเมื่อกดเบิ้ลปุ่มสร้างคอนเทนต์ และหากสร้างผลงานไม่สำเร็จด้วยเหตุขัดข้องใดๆ จะไม่มีการหักแต้มเครดิตของผู้ใช้โดยเด็ดขาด
- **Unit Tests:** ทดสอบระบบเครดิต ความปลอดภัย และการรองรับข้อผิดพลาดต่างๆ ได้ผ่านคำสั่ง `python -m unittest tests/test_credit_gate.py`

