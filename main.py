import os
import time
import logging
from config.settings import Settings
from services.sheets_service import SheetsService
from services.gemini_service import GeminiService
from services.blogger_service import BloggerService

def setup_logging():
    """
    ตั้งค่าระบบการบันทึกประวัติการทำงาน (Logging) 
    บันทึกลงไฟล์ logs/app.log และแสดงผลใน Terminal พร้อมกัน
    """
    # สร้างโฟลเดอร์ logs หากไม่มี
    os.makedirs("logs", exist_ok=True)
    
    # อ่านค่า Log Level จากคอนฟิก
    log_level_str = Settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/app.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def main():
    # 1. โหลดข้อมูลและตรวจสอบตัวแปรคอนฟิกใน .env
    try:
        Settings.validate()
    except ValueError as e:
        print(f"ข้อผิดพลาดในการตั้งค่าคอนฟิก: {e}")
        return

    # 2. เริ่มทำงานการตั้งค่า Log
    setup_logging()
    logging.info("==================================================")
    logging.info("เริ่มต้นการรันระบบ GetExpert AI Content Factory - Sprint 1")
    logging.info("==================================================")

    # 3. เริ่มต้นทำงานเปิดคลาสเซอร์วิส (Services Initialization)
    try:
        sheets_service = SheetsService()
        gemini_service = GeminiService()
        blogger_service = BloggerService()
    except Exception as e:
        logging.critical(f"ไม่สามารถเริ่มใช้งานเซอร์วิส Google/Gemini ได้: {e}")
        return

    # 4. อ่านหัวข้อรอประมวลผลจาก Google Sheets
    try:
        waiting_rows = sheets_service.read_waiting_rows()
    except Exception as e:
        logging.error(f"การดึงข้อมูลจากตารางชีตล้มเหลว: {e}")
        return

    if not waiting_rows:
        logging.info("ไม่พบหัวข้อคำขอที่อยู่ในสถานะรอสร้างคอนเทนต์ ('Waiting')")
        return

    # 5. วนรอบประมวลผลทีละรายการตามลำดับ (Sequential Processing)
    for row in waiting_rows:
        row_idx = row.row_idx
        topic = row.topic
        keyword = row.keyword
        
        logging.info(f"เริ่มประมวลผลแถวที่ {row_idx} | หัวข้อ: {topic} | คำสำคัญ: {keyword}")
        
        # 5.1 อัปเดตเปลี่ยนสถานะแถวเป็น 'Processing' ทันทีเพื่อล็อกการเขียนบทความ
        try:
            sheets_service.update_row_status(row_idx, "Processing")
        except Exception as e:
            logging.error(f"ไม่สามารถล็อกสถานะ 'Processing' ของแถวที่ {row_idx} ได้: {e}")
            continue

        try:
            # 5.2 ส่งหัวข้อและคำสำคัญไปแต่งผ่าน Gemini API (Structured Output)
            article = gemini_service.generate_blogger_article(topic, keyword)
            
            # 5.3 ส่งเนื้อหา HTML และชื่อหัวข้อไปอัปโหลดขึ้น Blogger แบบร่าง (Draft)
            post_result = blogger_service.create_draft_post(article.title, article.html_content)
            
            # 5.4 อัปเดตข้อมูลผลลัพธ์ลง Google Sheets ปรับสถานะเป็น 'Drafted'
            sheets_service.update_row_success(
                row_idx=row_idx,
                title=article.title,
                meta=article.meta_description,
                post_id=post_result.post_id,
                url=post_result.url
            )
            logging.info(f"ทำรายการแถวที่ {row_idx} สำเร็จลุล่วงแล้ว!")
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"การประมวลผลแถวที่ {row_idx} ล้มเหลวเนื่องจาก: {error_msg}")
            
            # 5.5 อัปเดตข้อผิดพลาดและเปลี่ยนสถานะเป็น 'Error' ในชีต
            try:
                sheets_service.update_row_error(row_idx, error_msg)
            except Exception as sheet_err:
                logging.error(f"การบันทึกแจ้ง Error ในแถวที่ {row_idx} ผิดพลาด: {sheet_err}")

        # เว้นวรรคการรันเพื่อเลี่ยงปัญหาความถี่ปัญญาประดิษฐ์และ API
        time.sleep(3)

    logging.info("สิ้นสุดการทำงานระบบ AI Blogger Automation รายวันประจำ Sprint 1")

if __name__ == "__main__":
    main()
