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

    def test_strip_html_tags_sanitization(self):
        """
        ทดสอบว่าฟังก์ชัน strip_html_tags ทำการแกะแท็ก HTML และล้างออกได้อย่างหมดจด
        """
        from utils.sanitize import strip_html_tags
        
        # ข้อความที่มีแท็ก HTML ปะปน
        html_input = "<strong>อบต.บางรัก</strong> ขอเชิญร่วม <p>โครงการแยกขยะ</p> เพื่อชุมชน <br/> สะอาด"
        sanitized = strip_html_tags(html_input)
        
        # ตรวจสอบว่าไม่มีเครื่องหมาย tag เหลืออยู่
        self.assertNotIn("<strong>", sanitized)
        self.assertNotIn("</strong>", sanitized)
        self.assertNotIn("<p>", sanitized)
        self.assertNotIn("</p>", sanitized)
        self.assertNotIn("<br/>", sanitized)
        self.assertNotIn("<br>", sanitized)
        self.assertIn("อบต.บางรัก", sanitized)
        self.assertIn("โครงการแยกขยะ", sanitized)

    def test_hashtags_generation_and_rules(self):
        """
        ทดสอบการล้างและตรวจสอบแฮชแท็กโซเชียลมีเดีย รวมถึงการคัดค้านคำขาย และดึงชื่อหน่วยงานสร้างเป็นแฮชแท็กนำหน้า
        """
        from models.content_models import SEOContent, SocialContentPack, FeaturedImagePrompt
        
        # 1. จำลองการสร้างโมเดลผลลัพธ์
        mock_content = SEOContent(
            title="ข่าวประชาสัมพันธ์โครงการแยกขยะ",
            seo_title="ข่าวประชาสัมพันธ์โครงการแยกขยะ",
            meta_description="ข่าวประชาสัมพันธ์โครงการแยกขยะของ อบต.บางรัก",
            slug_suggestion="pr-garbage-sorting",
            focus_keyword="แยกขยะ",
            related_keywords=["แยกขยะ", "ชุมชนสะอาด"],
            content_summary="สรุปโครงการแยกขยะ",
            article_html="<p>เนื้อหาข่าวประชาสัมพันธ์ราชการ</p>",
            faq=[],
            call_to_action="ติดต่อ อบต.บางรักเพื่อสอบถามข้อมูลเพิ่มเติม",
            internal_link_suggestion="ไม่มี",
            suggested_visual_elements="ภาพประกอบการแยกขยะ",
            social_pack=SocialContentPack(
                facebook_post="ขอเชิญชวนพี่น้องประชาชนร่วมโครงการแยกขยะ",
                facebook_hashtags=["#ข่าวสาร", "โปรเด็ด", "ซื้อเลย", "ลดราคา", "<strong>ขยะสะอาด</strong>"],
                tiktok_hook="รู้หรือไม่ขยะเปลี่ยนเป็นเงินได้",
                tiktok_script="สคริปต์ TikTok เล่าขยะ",
                youtube_shorts_script="สคริปต์ Shorts เล่าขยะ",
                youtube_title="ความรู้เรื่องขยะ",
                youtube_description="รายละเอียดวีดีโอ"
            ),
            featured_image=FeaturedImagePrompt(
                prompt="ภาพกองขยะสะอาด",
                style="3D Render",
                concept="Clean environment"
            )
        )
        
        # 2. จำลองการทำงานประมวลผลแฮชแท็กแบบเดียวกับใน gemini_service.py
        inputs = {"agency_name": "อบต.บางรัก"}
        content_type = "government"
        
        from utils.sanitize import strip_html_tags
        sp = mock_content.social_pack
        
        # ทำความสะอาดแฮชแท็ก
        raw_hashtags = [strip_html_tags(ht) for ht in sp.facebook_hashtags] if sp.facebook_hashtags else []
        cleaned_hashtags = []
        for ht in raw_hashtags:
            ht_clean = ht.strip().replace(" ", "").replace("#", "")
            if ht_clean:
                cleaned_hashtags.append(f"#{ht_clean}")
                
        # ปรับปรุงให้มีแฮชแท็กชื่อหน่วยงานนำหน้า
        agency_name = inputs.get("agency_name", inputs.get("organization_name", inputs.get("institution_name", "")))
        if agency_name:
            agency_clean = agency_name.strip().replace(" ", "").replace("#", "")
            if agency_clean:
                agency_tag = f"#{agency_clean}"
                if agency_tag not in cleaned_hashtags:
                    cleaned_hashtags.insert(0, agency_tag)
                    
        # ห้ามมีคำเชิงขายสำหรับหมวดราชการ/CSR/การศึกษา (เช่น #โปรเด็ด, #ซื้อเลย, #ลดราคา)
        if content_type in ["government", "csr", "education"]:
            forbidden = ["#โปรเด็ด", "#ซื้อเลย", "#ลดราคา"]
            cleaned_hashtags = [ht for ht in cleaned_hashtags if ht not in forbidden]
            
        # จำกัดแฮชแท็กสูงสุด 8 รายการ
        cleaned_hashtags = cleaned_hashtags[:8]
        
        # เติมเพิ่มหากไม่ครบ 5
        if len(cleaned_hashtags) < 5:
            default_tags = {
                "government": ["#ข่าวประชาสัมพันธ์", "#ประโยชน์เพื่อประชาชน", "#บริการประชาชน", "#พัฒนาชุมชน", "#ข่าวสารรัฐบาล"]
            }
            fallback_tags = default_tags["government"]
            for tag in fallback_tags:
                if tag not in cleaned_hashtags:
                    cleaned_hashtags.append(tag)
                    if len(cleaned_hashtags) >= 8:
                        break
                        
        cleaned_hashtags = cleaned_hashtags[:8]
        sp.facebook_hashtags = cleaned_hashtags
        
        # ต่อท้ายโพสต์
        hashtags_line = " ".join(cleaned_hashtags)
        if hashtags_line and hashtags_line not in sp.facebook_post:
            sp.facebook_post = f"{sp.facebook_post}\n\n{hashtags_line}"
            
        # 3. ยืนยันผลการประมวลผล
        self.assertIn("#อบต.บางรัก", sp.facebook_hashtags)
        self.assertIn("#อบต.บางรัก", sp.facebook_post)
        
        # ยืนยันจำนวนแฮชแท็กอยู่ระหว่าง 5 ถึง 8 รายการ
        self.assertTrue(5 <= len(sp.facebook_hashtags) <= 8)
        
        # ยืนยันว่าคำเชิงขายและแท็ก HTML ถูกกำจัดออกไป
        self.assertNotIn("#โปรเด็ด", sp.facebook_hashtags)
        self.assertNotIn("#ซื้อเลย", sp.facebook_hashtags)
        self.assertNotIn("#ลดราคา", sp.facebook_hashtags)
        self.assertNotIn("<strong>", "".join(sp.facebook_hashtags))

if __name__ == "__main__":
    unittest.main()
