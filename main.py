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
    os.makedirs("logs", exist_ok=True)
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
    logging.info("เริ่มต้นการรันระบบ GetExpert AI Content Factory - Sprint 4")
    logging.info("==================================================")

    # 3. เริ่มต้นทำงานเปิดคลาสเซอร์วิส (Services Initialization)
    try:
        sheets_service = SheetsService()
        gemini_service = GeminiService()
        blogger_service = BloggerService()
    except Exception as e:
        logging.critical(f"ไม่สามารถเริ่มใช้งานเซอร์วิส Google/Gemini ได้: {e}")
        return

    # 4. อ่านหัวข้อรอประมวลผลจาก Google Sheets (ดึงคอลัมน์ A:AE)
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
        
        # ดึงฟิลด์ป้อนเข้าใหม่ของ Sprint 4
        target_audience = row.target_audience
        business_type = row.business_type
        content_goal = row.content_goal
        tone = row.tone
        
        logging.info(f"เริ่มประมวลผลแถวที่ {row_idx} | หัวข้อ: {topic} | คีย์เวิร์ด: {keyword}")
        if target_audience:
            logging.info(f"-> กลุ่มเป้าหมาย: {target_audience} | ธุรกิจ: {business_type} | เป้าหมาย: {content_goal} | โทน: {tone}")
        
        # 5.1 อัปเดตเปลี่ยนสถานะแถวเป็น 'Processing' ทันทีเพื่อล็อกการเขียนบทความ
        try:
            sheets_service.update_row_status(row_idx, "Processing")
        except Exception as e:
            logging.error(f"ไม่สามารถล็อกสถานะ 'Processing' ของแถวที่ {row_idx} ได้: {e}")
            continue

        try:
            import json
            try:
                blueprint_inputs = json.loads(row.blueprint_inputs_json) if row.blueprint_inputs_json else {}
            except Exception:
                blueprint_inputs = {}
                
            seo_content = gemini_service.generate_blogger_article(
                topic=topic,
                keyword=keyword,
                target_audience=target_audience,
                business_type=business_type,
                content_goal=content_goal,
                tone=tone,
                content_type=row.content_type,
                blueprint_inputs=blueprint_inputs
            )
            
            # 5.3 รวบรวมข้อมูล HTML สำหรับ Blogger (เนื้อหาหลัก + FAQ + CTA)
            # สร้าง FAQ HTML
            faq_html = ""
            if seo_content.faq:
                faq_html = "<h2>คำถามที่พบบ่อย (FAQ)</h2><ul>"
                for item in seo_content.faq:
                    faq_html += f"<li><strong>{item.question}</strong><br/>{item.answer}</li>"
                faq_html += "</ul>"
            
            # สร้าง CTA HTML
            cta_html = ""
            if seo_content.call_to_action:
                cta_html = f"<div class='cta-section' style='margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-left: 5px solid #007bff;'><p>{seo_content.call_to_action}</p></div>"
            
            # รวมโค้ด HTML ทั้งหมดที่จะส่งเข้า Blogger
            full_html = seo_content.article_html + faq_html + cta_html
            
            # 5.4 ส่งเนื้อหา HTML และชื่อหัวข้อไปอัปโหลดขึ้น Blogger แบบร่าง (Draft)
            post_result = blogger_service.create_draft_post(seo_content.title, full_html)
            
            # 5.5 อัปเดตข้อมูลผลลัพธ์ SEO, Blogger และ Social Content Pack กลับลง Google Sheets (Retry Count = 0)
            sheets_service.update_row_success(
                row_idx=row_idx,
                seo_content=seo_content,
                post_id=post_result.post_id,
                url=post_result.url,
                retry_count=0
            )
            
            # หักแต้มเครดิตผู้ใช้งานหลังจากเขียนแถวประมวลผลสำเร็จเรียบร้อย (Sprint 6)
            if row.user_email:
                try:
                    from services.credit_service import CreditService
                    credit_service = CreditService(sheets_service)
                    is_eligible, credit_type, balance, status_msg = credit_service.check_credit_eligibility(row.user_email)
                    if is_eligible:
                        credit_service.consume_credit(
                            email=row.user_email,
                            credit_type=credit_type,
                            topic=topic,
                            content_type=row.content_type,
                            blueprint_label=row.blueprint_label
                        )
                except Exception as credit_err:
                    logging.error(f"ไม่สามารถหักเครดิตสำหรับ {row.user_email} ได้: {credit_err}")
                    
            logging.info(f"ทำรายการแถวที่ {row_idx} สำเร็จลุล่วงแล้ว!")
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"การประมวลผลแถวที่ {row_idx} ล้มเหลวเนื่องจาก: {error_msg}")
            
            # 5.6 อัปเดตข้อผิดพลาดและเปลี่ยนสถานะเป็น 'Failed' ในชีต บันทึก Retry Count = 3
            try:
                sheets_service.update_row_failed(row_idx, error_msg, retry_count=3)
            except Exception as sheet_err:
                logging.error(f"การบันทึกแจ้ง Error ในแถวที่ {row_idx} ผิดพลาด: {sheet_err}")
                
            # บันทึกประวัติความล้มเหลวลงในชีต Usage Logs โดยไม่หักแต้มเครดิต (Sprint 6)
            if row.user_email:
                try:
                    from services.credit_service import CreditService
                    credit_service = CreditService(sheets_service)
                    is_eligible, credit_type, balance, status_msg = credit_service.check_credit_eligibility(row.user_email)
                    credit_service.log_failed_generation(
                        email=row.user_email,
                        credit_type=credit_type,
                        topic=topic,
                        content_type=row.content_type,
                        blueprint_label=row.blueprint_label,
                        error_msg=error_msg
                    )
                except Exception as credit_err:
                    logging.error(f"ไม่สามารถบันทึก Usage Log ล้มเหลวได้: {credit_err}")

        # เว้นวรรคการรันเพื่อเลี่ยงปัญหาความถี่ปัญญาประดิษฐ์และ API
        time.sleep(3)

    logging.info("สิ้นสุดการทำงานระบบ AI Blogger Automation รายวันประจำ Sprint 4")

if __name__ == "__main__":
    main()
