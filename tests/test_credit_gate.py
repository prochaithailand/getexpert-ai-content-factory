# tests/test_credit_gate.py

import unittest
from unittest.mock import MagicMock
from models.credit_models import UserCredit, UsageLog
from services.credit_service import CreditService

class TestCreditGate(unittest.TestCase):
    def test_new_user_eligibility(self):
        """
        ผู้ใช้ใหม่ต้องได้สิทธิ์ Free Trial จำนวน 3 ครั้ง
        """
        sheets_mock = MagicMock()
        sheets_mock.get_user_by_email.return_value = None  # ไม่เจอผู้ใช้ในชีต

        credit_service = CreditService(sheets_service=sheets_mock)
        is_eligible, credit_type, balance, msg = credit_service.check_credit_eligibility("new_user@example.com")
        
        self.assertTrue(is_eligible)
        self.assertEqual(credit_type, "free")
        self.assertEqual(balance, 3)
        self.assertIn("ทดลองใช้ฟรี", msg)

    def test_existing_user_partial_free(self):
        """
        ผู้ใช้ที่เคยสร้างฟรีไปบ้างแต่ยังไม่ครบ 3 ครั้ง
        """
        sheets_mock = MagicMock()
        existing_user = UserCredit(
            user_email="partial@example.com",
            user_name="Test User",
            created_at="2026-07-03 00:00:00",
            free_credits_used=1,  # ใช้ไป 1 เหลือ 2
            paid_credits_balance=0,
            total_generated=1,
            payment_status="Free Trial",
            last_generated_at="2026-07-03 00:00:00",
            updated_at="2026-07-03 00:00:00"
        )
        sheets_mock.get_user_by_email.return_value = (existing_user, 2)

        credit_service = CreditService(sheets_service=sheets_mock)
        is_eligible, credit_type, balance, msg = credit_service.check_credit_eligibility("partial@example.com")
        
        self.assertTrue(is_eligible)
        self.assertEqual(credit_type, "free")
        self.assertEqual(balance, 2)  # 3 - 1 = 2
        self.assertIn("คุณใช้สิทธิ์ฟรีไปแล้ว 1 / 3", msg)

    def test_user_credits_depleted(self):
        """
        ผู้ใช้ใช้สิทธิ์ฟรีครบ 3 และไม่มีเครดิตเติมเงินเหลือ
        """
        sheets_mock = MagicMock()
        depleted_user = UserCredit(
            user_email="depleted@example.com",
            user_name="Test User",
            created_at="2026-07-03 00:00:00",
            free_credits_used=3,
            paid_credits_balance=0,
            total_generated=3,
            payment_status="Credit Depleted",
            last_generated_at="2026-07-03 00:00:00",
            updated_at="2026-07-03 00:00:00"
        )
        sheets_mock.get_user_by_email.return_value = (depleted_user, 3)

        credit_service = CreditService(sheets_service=sheets_mock)
        is_eligible, credit_type, balance, msg = credit_service.check_credit_eligibility("depleted@example.com")
        
        self.assertFalse(is_eligible)
        self.assertEqual(credit_type, "blocked")
        self.assertEqual(balance, 0)
        self.assertIn("สิทธิ์ทดลองใช้ฟรีครบแล้ว", msg)

    def test_user_paid_credits(self):
        """
        ผู้ใช้ใช้ฟรีครบ 3 แล้ว แต่มีเครดิตเติมเงินคงเหลือ
        """
        sheets_mock = MagicMock()
        paid_user = UserCredit(
            user_email="buyer@example.com",
            user_name="Test User",
            created_at="2026-07-03 00:00:00",
            free_credits_used=3,
            paid_credits_balance=5,  # เหลือเครดิตเติมเงิน 5 ครั้ง
            total_generated=3,
            payment_status="Active Customer",
            last_generated_at="2026-07-03 00:00:00",
            updated_at="2026-07-03 00:00:00"
        )
        sheets_mock.get_user_by_email.return_value = (paid_user, 4)

        credit_service = CreditService(sheets_service=sheets_mock)
        is_eligible, credit_type, balance, msg = credit_service.check_credit_eligibility("buyer@example.com")
        
        self.assertTrue(is_eligible)
        self.assertEqual(credit_type, "paid")
        self.assertEqual(balance, 5)
        self.assertIn("เหลือเครดิต 5", msg)

    def test_consume_free_credit(self):
        """
        ทดสอบการหักสิทธิ์ใช้งานแบบฟรี
        """
        sheets_mock = MagicMock()
        user = UserCredit(
            user_email="consume_free@example.com",
            user_name="Test User",
            created_at="2026-07-03 00:00:00",
            free_credits_used=0,
            paid_credits_balance=0,
            total_generated=0,
            payment_status="Free Trial",
            last_generated_at="",
            updated_at=""
        )
        sheets_mock.get_user_by_email.return_value = (user, 2)

        credit_service = CreditService(sheets_service=sheets_mock)
        success, msg = credit_service.consume_credit(
            email="consume_free@example.com",
            credit_type="free",
            topic="หัวข้อทดสอบ",
            content_type="business",
            blueprint_label="ธุรกิจ"
        )
        
        self.assertTrue(success)
        self.assertEqual(user.free_credits_used, 1)
        self.assertEqual(user.total_generated, 1)
        sheets_mock.save_user_credit.assert_called_once()
        sheets_mock.add_usage_log.assert_called_once()
        
        log_arg = sheets_mock.add_usage_log.call_args[0][0]
        self.assertIsInstance(log_arg, UsageLog)
        self.assertEqual(log_arg.user_email, "consume_free@example.com")
        self.assertEqual(log_arg.credit_type_used, "free")
        self.assertEqual(log_arg.credits_before, 3)
        self.assertEqual(log_arg.credits_after, 2)
        self.assertEqual(log_arg.status, "Success")

    def test_consume_paid_credit(self):
        """
        ทดสอบการหักสิทธิ์ใช้งานแบบจ่ายเงิน
        """
        sheets_mock = MagicMock()
        user = UserCredit(
            user_email="consume_paid@example.com",
            user_name="Test User",
            created_at="2026-07-03 00:00:00",
            free_credits_used=3,
            paid_credits_balance=10,
            total_generated=3,
            payment_status="Active Customer",
            last_generated_at="",
            updated_at=""
        )
        sheets_mock.get_user_by_email.return_value = (user, 5)

        credit_service = CreditService(sheets_service=sheets_mock)
        success, msg = credit_service.consume_credit(
            email="consume_paid@example.com",
            credit_type="paid",
            topic="หัวข้อทดสอบ",
            content_type="business",
            blueprint_label="ธุรกิจ"
        )
        
        self.assertTrue(success)
        self.assertEqual(user.paid_credits_balance, 9)
        self.assertEqual(user.total_generated, 4)
        sheets_mock.save_user_credit.assert_called_once()
        sheets_mock.add_usage_log.assert_called_once()
        
        log_arg = sheets_mock.add_usage_log.call_args[0][0]
        self.assertEqual(log_arg.credit_type_used, "paid")
        self.assertEqual(log_arg.credits_before, 10)
        self.assertEqual(log_arg.credits_after, 9)
        self.assertEqual(log_arg.status, "Success")

    def test_log_failed_generation(self):
        """
        กรณีประมวลผลการทำงานล้มเหลว ต้องมีล็อกสเตตัส Failed และไม่หักคะแนนเครดิตใดๆ
        """
        sheets_mock = MagicMock()
        user = UserCredit(
            user_email="fail_user@example.com",
            user_name="Test User",
            created_at="2026-07-03 00:00:00",
            free_credits_used=0,
            paid_credits_balance=0,
            total_generated=0,
            payment_status="Free Trial",
            last_generated_at="",
            updated_at=""
        )
        sheets_mock.get_user_by_email.return_value = (user, 2)

        credit_service = CreditService(sheets_service=sheets_mock)
        credit_service.log_failed_generation(
            email="fail_user@example.com",
            credit_type="free",
            topic="หัวข้อที่พัง",
            content_type="business",
            blueprint_label="ธุรกิจ",
            error_msg="Gemini rate limit error"
        )
        
        # ห้ามเรียก save_user_credit (ห้ามแก้คะแนน)
        sheets_mock.save_user_credit.assert_not_called()
        self.assertEqual(user.free_credits_used, 0)
        self.assertEqual(user.total_generated, 0)
        
        # ต้องเขียน log status Failed
        sheets_mock.add_usage_log.assert_called_once()
        log_arg = sheets_mock.add_usage_log.call_args[0][0]
        self.assertEqual(log_arg.user_email, "fail_user@example.com")
        self.assertEqual(log_arg.credits_before, 3)
        self.assertEqual(log_arg.credits_after, 3)
        self.assertIn("Failed:", log_arg.status)
        self.assertIn("Gemini rate limit error", log_arg.status)

if __name__ == "__main__":
    unittest.main()
