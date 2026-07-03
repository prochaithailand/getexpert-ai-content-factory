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
