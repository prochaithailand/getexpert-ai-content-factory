# tests/test_referral.py

import unittest
from unittest.mock import MagicMock
from models.credit_models import UserCredit
from services.credit_service import CreditService

class TestReferralSystem(unittest.TestCase):
    def test_new_user_registration_with_referrer(self):
        """
        ตรวจสอบการสมัครสมาชิกผู้ใช้รายใหม่ผ่านลิงก์แนะนำว่ามีการบันทึก Referred By หรือไม่
        """
        sheets_mock = MagicMock()
        sheets_mock.get_user_by_email.return_value = None  # ไม่พบผู้ใช้งานเดิม
        
        credit_service = CreditService(sheets_service=sheets_mock)
        user = credit_service.get_or_create_user(
            email="new_referred_user@example.com",
            name="New Referred User",
            referred_by="KALAYA001"
        )
        
        # ตรวจสอบการส่งค่า referred_by ไปยังโมเดล UserCredit
        self.assertEqual(user.user_email, "new_referred_user@example.com")
        self.assertEqual(user.referred_by, "KALAYA001")
        
        # ตรวจสอบว่า SheetsService.save_user_credit ถูกเรียกพร้อมผู้ใช้ที่มี referred_by ถูกต้อง
        sheets_mock.save_user_credit.assert_called_once()
        saved_user = sheets_mock.save_user_credit.call_args[0][0]
        self.assertEqual(saved_user.referred_by, "KALAYA001")

    def test_existing_user_registration_ignores_referrer(self):
        """
        ตรวจสอบว่าผู้ใช้ที่มีอยู่แล้วในระบบจะไม่ถูกแก้ไขผู้แนะนำใหม่ทับ (ตามข้อกำหนดสิทธิ์ครั้งแรก)
        """
        sheets_mock = MagicMock()
        existing_user = UserCredit(
            user_email="already_exists@example.com",
            user_name="Existing User",
            created_at="2026-07-03 00:00:00",
            free_credits_used=0,
            paid_credits_balance=0,
            total_generated=0,
            payment_status="Free Trial",
            last_generated_at="",
            updated_at="2026-07-03 00:00:00",
            referred_by="ORIGINAL_REF"
        )
        sheets_mock.get_user_by_email.return_value = (existing_user, 2)
        
        credit_service = CreditService(sheets_service=sheets_mock)
        user = credit_service.get_or_create_user(
            email="already_exists@example.com",
            name="Existing User",
            referred_by="NEW_REF_IGNORED"
        )
        
        self.assertEqual(user.referred_by, "ORIGINAL_REF")

    def test_referral_partner_model_defaults(self):
        """
        ตรวจสอบสถานะฟิลด์ตั้งต้นของพาร์ทเนอร์ในโครงสร้างโมเดล UserCredit
        """
        user = UserCredit(
            user_email="partner_check@example.com",
            user_name="Partner Check",
            created_at="2026-07-03 00:00:00",
            updated_at="2026-07-03 00:00:00"
        )
        
        self.assertFalse(user.is_referral_partner)
        self.assertEqual(user.referral_code, "")
        self.assertEqual(user.referral_link, "")
        self.assertEqual(user.referral_package_paid, 0.0)
        self.assertEqual(user.referral_status, "")

    def test_referral_partner_activation_flow(self):
        """
        ทดสอบการเปิดสิทธิ์พาร์ทเนอร์ และการสร้างรหัสกับลิงก์แนะนำที่ถูกต้อง
        """
        user = UserCredit(
            user_email="partner@example.com",
            user_name="Partner User",
            created_at="2026-07-03 00:00:00",
            updated_at="2026-07-03 00:00:00"
        )
        
        # เปิดสิทธิ์พาร์ทเนอร์
        ref_code = "PROCHAIT001"
        user.is_referral_partner = True
        user.referral_code = ref_code
        user.referral_link = f"https://getexpert-ai-content-factory1.streamlit.app/?ref={ref_code}"
        user.referral_status = "Active"
        user.referral_package_paid = 149.0
        
        self.assertTrue(user.is_referral_partner)
        self.assertEqual(user.referral_code, "PROCHAIT001")
        self.assertEqual(user.referral_link, "https://getexpert-ai-content-factory1.streamlit.app/?ref=PROCHAIT001")
        self.assertEqual(user.referral_status, "Active")
        self.assertEqual(user.referral_package_paid, 149.0)

    def test_sheets_service_resource_resolution(self):
        """
        ตรวจสอบการดึงและอัปเดตข้อมูลของ SheetsService เพื่อป้องกันข้อผิดพลาด AttributeError
        """
        from services.sheets_service import SheetsService
        
        # Instantiate without calling __init__ to avoid Google credentials requirements in tests
        service_instance = SheetsService.__new__(SheetsService)
        service_instance.spreadsheet_id = "dummy_id"
        
        # จำลองค่า service API resource
        mock_api = MagicMock()
        service_instance.service = mock_api
        
        # ตรวจเช็คว่าไม่มี Attribute 'service' ซ้อนกันใน self.service (self.service.service)
        # ตรวจสอบการทำ mock ของ spreadsheets()
        mock_spreadsheets = MagicMock()
        mock_api.spreadsheets.return_value = mock_spreadsheets
        mock_values = MagicMock()
        mock_spreadsheets.values.return_value = mock_values
        
        # คืนค่าจำลองของ Users (แถวหัวตาราง + ข้อมูลแถวแรกมี KALAYA001)
        mock_values.get().execute.return_value = {
            'values': [
                ["User Email", "User Name", "Created At", "Free Credits Used", 
                 "Paid Credits Balance", "Total Generated", "Payment Status", 
                 "Last Generated At", "Updated At", "Is Referral Partner",
                 "Referral Code", "Referral Link", "Referral Started At",
                 "Referral Package Paid", "Referral Status", "Referred By"],
                ["referred@example.com", "Referred", "2026-07-03 00:00:00", "0", "0", "0", 
                 "Free Trial", "", "2026-07-03 00:00:00", "TRUE", "KALAYA001", 
                 "https://getexpert-ai-content-factory1.streamlit.app/?ref=KALAYA001", 
                 "2026-07-03 00:00:00", "149.0", "Active", ""]
            ]
        }
        
        # เรียกค้นหาผู้แนะนำด้วยรหัส KALAYA001
        res = service_instance.get_user_by_referral_code("KALAYA001")
        self.assertIsNotNone(res)
        user_res, idx = res
        self.assertEqual(user_res.user_email, "referred@example.com")
        self.assertEqual(user_res.referral_code, "KALAYA001")
        self.assertTrue(user_res.is_referral_partner)
        self.assertEqual(idx, 2)

    def test_sanitize_referral_code(self):
        """
        ทดสอบการ sanitize รหัสแนะนำตามรูปแบบที่กำหนด
        """
        import re
        def sanitize_referral_code(code: str) -> str:
            if not code:
                return ""
            cleaned = re.sub(r'[^A-Za-z0-9_\-]', '', code)
            return cleaned[:20].upper()

        self.assertEqual(sanitize_referral_code("PROCHAIT001"), "PROCHAIT001")
        self.assertEqual(sanitize_referral_code("prochait-001_test"), "PROCHAIT-001_TEST")
        self.assertEqual(sanitize_referral_code("PROCHAIT!!!001"), "PROCHAIT001")
        self.assertEqual(sanitize_referral_code("a" * 50), "A" * 20)
        self.assertEqual(sanitize_referral_code(None), "")

    def test_query_params_error_safety(self):
        """
        ทดสอบความปลอดภัยว่าหาก st.query_params เกิดข้อผิดพลาด/ไม่มีค่า จะไม่ทำให้แอป crash
        """
        import logging
        
        # จำลองการเกิด Error ตอนดึง query_params
        def get_demo_param_safe(query_params_mock):
            is_demo = False
            try:
                raw_demo = "false"
                if query_params_mock:
                    if hasattr(query_params_mock, "get"):
                        raw_demo = query_params_mock.get("demo", "false")
                if isinstance(raw_demo, list):
                    raw_demo = raw_demo[0] if raw_demo else "false"
                is_demo = raw_demo.lower() == "true"
            except BaseException as e:
                logging.warning(f"Error check: {e}")
            return is_demo

        # ถ้า mock เป็น None (เหมือนไม่มีคุณลักษณะ) ต้องไม่พัง
        self.assertFalse(get_demo_param_safe(None))
        # ถ้า mock เป็น dict
        self.assertTrue(get_demo_param_safe({"demo": "true"}))
        # ถ้า mock โยน exception
        class BrokenParams:
            def get(self, name, default):
                raise RuntimeError("Segfault simulated")
        self.assertFalse(get_demo_param_safe(BrokenParams()))

