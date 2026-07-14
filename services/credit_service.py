# services/credit_service.py

import logging
from datetime import datetime
from models.credit_models import UserCredit, UsageLog
from services.sheets_service import SheetsService

class CreditService:
    """
    บริการควบคุมตรวจสอบสิทธิ์และหักแต้มเครดิตการสร้าง Content Pack (Sprint 6)
    """
    
    def __init__(self, sheets_service: SheetsService = None):
        try:
            self.sheets_service = sheets_service or SheetsService()
        except Exception as e:
            logging.error(f"ไม่สามารถเริ่มใช้งาน SheetsService ใน CreditService ได้: {e}")
            self.sheets_service = None

    def get_or_create_user(self, email: str, name: str, referred_by: str = "") -> UserCredit:
        """
        ดึงข้อมูลผู้ใช้ปัจจุบันจากอีเมล หรือสร้างใหม่หากไม่พบประวัติการใช้งาน (พร้อมรองรับรหัสผู้แนะนำ Referred By)
        """
        email_clean = email.strip().lower()
        name_clean = name.strip() if name else "Anonymous User"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not self.sheets_service:
            logging.error("SheetsService ไม่ทำงาน (ไม่พร้อมเชื่อมต่อ) - ใช้ fallback ใน memory")
            return UserCredit(
                user_email=email_clean,
                user_name=name_clean,
                created_at=now_str,
                free_credits_used=0,
                paid_credits_balance=0,
                total_generated=0,
                payment_status="Free Trial",
                last_generated_at="",
                updated_at=now_str,
                referred_by=referred_by
            )
            
        try:
            result = self.sheets_service.get_user_by_email(email_clean)
            if result:
                user, row_idx = result
                # ตรวจสอบเผื่อผู้ใช้เปลี่ยนชื่อในฟอร์มหน้าบ้าน
                if name_clean and user.user_name != name_clean and name_clean != "Anonymous User":
                    user.user_name = name_clean
                    user.updated_at = now_str
                    try:
                        self.sheets_service.save_user_credit(user, row_idx)
                    except Exception as e:
                        logging.error(f"ไม่สามารถอัปเดตประวัติเครดิตได้ (บันทึกลง Users sheet ล้มเหลว): {e}")
                return user
        except Exception as e:
            logging.error(f"ไม่สามารถดึงข้อมูลผู้ใช้จาก Google Sheets ได้ (กำลังใช้ fallback ใน memory): {e}")
            return UserCredit(
                user_email=email_clean,
                user_name=name_clean,
                created_at=now_str,
                free_credits_used=0,
                paid_credits_balance=0,
                total_generated=0,
                payment_status="Free Trial",
                last_generated_at="",
                updated_at=now_str,
                referred_by=referred_by
            )
            
        # สร้างผู้ใช้ใหม่พิกัดเริ่มต้น พร้อมระบุผู้แนะนำถ้ามี
        new_user = UserCredit(
            user_email=email_clean,
            user_name=name_clean,
            created_at=now_str,
            free_credits_used=0,
            paid_credits_balance=0,
            total_generated=0,
            payment_status="Free Trial",
            last_generated_at="",
            updated_at=now_str,
            referred_by=referred_by
        )
        try:
            self.sheets_service.save_user_credit(new_user)
        except Exception as e:
            logging.error(f"ไม่สามารถจัดสร้างผู้ใช้ใหม่บน Google Sheets ได้: {e}")
        return new_user

    def check_credit_eligibility(self, email: str) -> tuple[bool, str, int, str]:
        """
        ตรวจสอบสิทธิ์การใช้งาน
        """
        if not self.sheets_service:
            logging.error("SheetsService ไม่ทำงาน (ไม่พร้อมเชื่อมต่อ) - บล็อกสิทธิ์เพื่อความปลอดภัย")
            return False, "blocked", 0, "⚠️ ระบบตรวจสอบเครดิตขัดข้องชั่วคราว (ไม่สามารถเชื่อมต่อฐานข้อมูล Google Sheets ได้) กรุณาลองใหม่อีกครั้ง"
            
        try:
            email_clean = email.strip().lower()
            result = self.sheets_service.get_user_by_email(email_clean)
            if not result:
                return False, "blocked", 0, "ไม่พบข้อมูลเครดิตของอีเมลนี้ กรุณาติดต่อ LINE OA"
                
            user, _ = result
            if not user.user_email or not user.payment_status:
                return False, "blocked", 0, "ไม่พบข้อมูลเครดิตของอีเมลนี้ กรุณาติดต่อ LINE OA"
            
            # เงื่อนไข 1: ใช้โควตาฟรีไม่ครบ 1 ครั้ง
            if user.free_credits_used < 1:
                remaining_free = 1 - user.free_credits_used
                return True, "free", remaining_free, f"คุณใช้สิทธิ์ฟรีไปแล้ว {user.free_credits_used} / 1 Content Pack"
                
            # เงื่อนไข 2: ใช้ฟรีครบแล้วแต่มีเครดิตเสียเงินคงเหลือ
            if user.paid_credits_balance > 0:
                return True, "paid", user.paid_credits_balance, f"คุณเหลือเครดิต {user.paid_credits_balance} Content Packs"
                
            # เงื่อนไข 3: ใช้ฟรีหมดและไม่มีเครดิตเงินโอนเหลือ
            return False, "blocked", 0, "คุณใช้สิทธิ์ทดลองใช้ฟรีครบแล้ว กรุณาซื้อเครดิตเพื่อสร้างคอนเทนต์ต่อ"
        except Exception as e:
            logging.error(f"ไม่สามารถตรวจสอบสิทธิ์เครดิตเนื่องจากการเชื่อมต่อชีตล้มเหลว: {e}")
            return False, "blocked", 0, "⚠️ ระบบตรวจสอบเครดิตขัดข้องชั่วคราว (ไม่สามารถเชื่อมต่อฐานข้อมูล Google Sheets ได้) กรุณาลองใหม่อีกครั้ง"

    def consume_credit(self, email: str, credit_type: str, topic: str, content_type: str, blueprint_label: str) -> tuple[bool, str]:
        """
        ทำการหักเครดิตหลังจากสั่งรันสำเร็จเรียบร้อย
        """
        if not self.sheets_service:
            return False, "ระบบเก็บข้อมูลเครดิตไม่ทำงานชั่วคราว"
            
        email_clean = email.strip().lower()
        try:
            result = self.sheets_service.get_user_by_email(email_clean)
            if not result:
                return False, "ไม่พบข้อมูลผู้ใช้งานในระบบ"
                
            user, row_idx = result
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            credits_before = 1 - user.free_credits_used if credit_type == "free" else user.paid_credits_balance
            
            if credit_type == "free":
                if user.free_credits_used >= 1:
                    return False, "สิทธิ์ทดลองใช้ฟรีของคุณหมดแล้ว"
                user.free_credits_used += 1
            elif credit_type == "paid":
                if user.paid_credits_balance <= 0:
                    return False, "เครดิตของคุณหมดแล้ว กรุณาซื้อเติมเพิ่ม"
                user.paid_credits_balance -= 1
            else:
                return False, "ประเภทเครดิตไม่ถูกต้อง"
                
            # อัปเดตเมตาข้อมูลผู้ใช้
            user.total_generated += 1
            user.last_generated_at = now_str
            user.updated_at = now_str
            if user.free_credits_used >= 1 and user.paid_credits_balance == 0:
                user.payment_status = "Credit Depleted"
            elif user.paid_credits_balance > 0:
                user.payment_status = "Active Customer"
                
            credits_after = 1 - user.free_credits_used if credit_type == "free" else user.paid_credits_balance
            
            # 1. อัปเดตข้อมูลผู้ใช้งานลง Users Sheet
            self.sheets_service.save_user_credit(user, row_idx)
            
            # 2. บันทึกประวัติลง Usage Logs Sheet
            log = UsageLog(
                timestamp=now_str,
                user_email=email_clean,
                content_type=content_type,
                blueprint_label=blueprint_label,
                topic=topic,
                credit_type_used=credit_type,
                credits_before=credits_before,
                credits_after=credits_after,
                status="Success"
            )
            try:
                self.sheets_service.add_usage_log(log)
            except Exception as e:
                logging.error(f"ไม่สามารถบันทึกล็อกประวัติการใช้งานได้: {e}")
            
            return True, "หักแต้มเครดิตและบันทึกประวัติการใช้งานสำเร็จ"
        except Exception as e:
            logging.error(f"เกิดข้อผิดพลาดขณะดำเนินการหักเครดิต: {e}")
            return False, f"ระบบเกิดข้อผิดพลาดในการเข้าถึงชีตข้อมูล: {e}"

    def log_failed_generation(self, email: str, credit_type: str, topic: str, content_type: str, blueprint_label: str, error_msg: str):
        """
        บันทึกกรณีการทำงานล้มเหลวลงชีตประวัติการใช้งาน (โดยห้ามหักคะแนนเครดิต)
        """
        if not self.sheets_service:
            return
            
        email_clean = email.strip().lower()
        try:
            result = self.sheets_service.get_user_by_email(email_clean)
            if not result:
                return
                
            user, _ = result
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            credits_current = 1 - user.free_credits_used if credit_type == "free" else user.paid_credits_balance
            
            log = UsageLog(
                timestamp=now_str,
                user_email=email_clean,
                content_type=content_type,
                blueprint_label=blueprint_label,
                topic=topic,
                credit_type_used=credit_type,
                credits_before=credits_current,
                credits_after=credits_current,
                status=f"Failed: {error_msg}"
            )
            self.sheets_service.add_usage_log(log)
        except Exception as e:
            logging.error(f"เกิดปัญหาไม่สามารถเขียนบันทึกประวัติข้อขัดข้องได้: {e}")
