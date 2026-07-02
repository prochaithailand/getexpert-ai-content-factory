# tests/test_blueprints.py

import unittest
from services.blueprint_service import BlueprintService

class TestAIContentBlueprints(unittest.TestCase):
    """
    ชุดทดสอบสำหรับ AI Content Blueprint (Sprint 5)
    """

    def test_get_valid_blueprints(self):
        """
        ทดสอบว่าดึงคีย์ที่ถูกต้องแล้วคืนค่า Blueprint ที่ถูกต้อง
        """
        bp_business = BlueprintService.get_blueprint("business")
        self.assertEqual(bp_business["label"], "📈 ธุรกิจ / สินค้า")
        self.assertIn("topic", bp_business["form_fields"])
        
        bp_gov = BlueprintService.get_blueprint("government")
        self.assertEqual(bp_gov["label"], "🏛 หน่วยงานราชการ")
        self.assertIn("agency_name", bp_gov["form_fields"])

    def test_fallback_blueprint(self):
        """
        ทดสอบว่ากรณีเรียกด้วยคีย์ที่ไม่ถูกต้องหรือว่างเปล่า จะ Fallback ไปหา Business Blueprint
        """
        bp_fallback = BlueprintService.get_blueprint("non_existent_key")
        self.assertEqual(bp_fallback["label"], "📈 ธุรกิจ / สินค้า")
        
        bp_empty = BlueprintService.get_blueprint("")
        self.assertEqual(bp_empty["label"], "📈 ธุรกิจ / สินค้า")

    def test_required_keys_in_all_blueprints(self):
        """
        ทดสอบว่า Blueprint ทุกชิ้นต้องมีโครงสร้างคีย์ครบถ้วน
        """
        all_bps = BlueprintService.get_all_blueprints()
        required_keys = ["label", "description", "form_fields", "prompt_strategy", "outputs"]
        
        for key, bp in all_bps.items():
            for req in required_keys:
                self.assertIn(req, bp, f"Blueprint '{key}' ไม่มีคีย์ที่จำเป็น: '{req}'")
            
            # ตรวจสอบโครงสร้าง Prompt Strategy
            self.assertIn("role", bp["prompt_strategy"])
            self.assertIn("focus", bp["prompt_strategy"])
            self.assertIn("rules", bp["prompt_strategy"])
            
            # ตรวจสอบการแปลงรายการโซเชียลมีเดีย Y:AE
            outputs = bp["outputs"]
            self.assertIn("seo_article", outputs)
            self.assertIn("facebook_post", outputs)
            self.assertIn("tiktok_script", outputs)
            self.assertIn("youtube_script", outputs)
            self.assertIn("image_prompt", outputs)

    def test_build_blueprint_context(self):
        """
        ทดสอบการผูกประมวลข้อความอินพุต
        """
        inputs = {
            "topic": "การออกกำลังกายลดพุง",
            "keyword": "ลดหน้าท้อง",
            "business_name": "GetExpert Fitness",
            "non_blueprint_field": "ค่าอื่นๆ"
        }
        
        context_str = BlueprintService.build_blueprint_context("business", inputs)
        
        self.assertIn("การออกกำลังกายลดพุง", context_str)
        self.assertIn("GetExpert Fitness", context_str)
        self.assertNotIn("ค่าอื่นๆ", context_str)

if __name__ == "__main__":
    unittest.main()
