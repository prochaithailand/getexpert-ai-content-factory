# Sprint 4 Plan - Client Delivery & Content Pack MVP

แผนการดำเนินงานของ Sprint 4 สำหรับโครงการ **GetExpert AI Content Factory**

## เป้าหมายของ Sprint (Sprint Goal)
ขยายความสามารถในการผลิตคอนเทนต์จากเพียงแค่บทความบล็อก SEO ตัวเดียว ให้กลายเป็น **Content Pack** ครบวงจรที่ลูกค้านำไปใช้งานจริงได้ในช่องทางต่างๆ (Omnichannel Digital Assets) เช่น Facebook, TikTok, และ YouTube Shorts พร้อมเพิ่มช่องป้อนบริบทของแบรนด์เพื่อสร้างบทความที่แม่นยำขึ้น

---

## ขอบเขตการทำงาน (Sprint Scope)
### ขอบเขตใน Sprint 4:
1. **การเก็บและอัปเดตฟิลด์ใหม่บน Google Sheets:**
   - รองรับคอลัมน์ U ถึง AE รวมเป็น 31 คอลัมน์
   - ยืนยันความเข้ากันได้ย้อนหลัง (Backwards Compatibility) สามารถรันแถวเก่าที่มีเพียง 20 คอลัมน์ (A:T) ได้โดยระบบไม่มีการแสดงผล Error
2. **การปรับเพิ่ม Inputs และ Outputs:**
   - ช่องรับอินพุตใหม่ 4 ช่อง: Target Audience, Business Type, Content Goal, Tone
   - ชุดผลลัพธ์โซเชียลใหม่ 7 ช่อง: Facebook Post, Facebook Hashtags, TikTok Hook, TikTok Script, YouTube Shorts Script, YouTube Title, YouTube Description
3. **การขยายผลลัพธ์และตกแต่งหน้าบ้าน (Streamlit UI):**
   - เพิ่มเมนูให้ผู้ใช้งานกรอกประเด็นธุรกิจและกลุ่มเป้าหมายใน Web Form
   - จัดแสดงผลลัพธ์เป็นหน้าจอรายละเอียด Content Pack แบบ 5 แท็บแยกประเภท เพื่อให้สามารถ Copy ร่างบทความ, โพสต์ หรือสคริปต์วิดีโอไปใช้ได้สะดวก

### นอกเหนือขอบเขต Sprint 4 (ยังไม่ทำ):
- ระบบโพสต์ลงโซเชียลแบบอัตโนมัติ (Auto Posting)
- ระบบสมาชิก, การชำระเงิน หรือระบบเครดิต (Payment & Credits)
- การสร้างฐานข้อมูลระดับเซิร์ฟเวอร์ เช่น Supabase

---

## โครงสร้างคอลัมน์ตาราง Google Sheets (Sprint 4)
* **A-T:** คอลัมน์เดิม (ID, Topic, Keyword, Status, SEO Title, Meta Description, Blogger Post ID, Blogger URL, Slug, Focus Keyword, Related Keywords, Content Summary, Featured Image Prompt, Image Style, Image Concept, Retry Count, Last Error, Processed At, Created At, Updated At)
* **U (20):** `Target Audience`
* **V (21):** `Business Type`
* **W (22):** `Content Goal`
* **X (23):** `Tone`
* **Y (24):** `Facebook Post`
* **Z (25):** `Facebook Hashtags`
* **AA (26):** `TikTok Hook`
* **AB (27):** `TikTok Script`
* **AC (28):** `YouTube Shorts Script`
* **AD (29):** `YouTube Title`
* **AE (30):** `YouTube Description`
