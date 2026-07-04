import logging
from google import genai
from google.genai import types

from config.settings import Settings
from models.content_models import SEOContent
from prompts.blogger_seo_prompt import get_blogger_seo_prompt
from utils.retry import retry

class GeminiService:
    """
    เซอร์วิสการจัดการเชื่อมต่อและทำงานร่วมกับ Gemini API
    """
    def __init__(self):
        self.api_key = Settings.GEMINI_API_KEY
        self.model_name = Settings.GEMINI_MODEL
        if not self.api_key:
            raise ValueError("กรุณาระบุ GEMINI_API_KEY ในไฟล์ .env")
        self.client = genai.Client(api_key=self.api_key)

    @retry(max_retries=3, delays=[2, 5, 10])
    def generate_blogger_article(
        self, 
        topic: str, 
        keyword: str,
        target_audience: str = "",
        business_type: str = "",
        content_goal: str = "",
        tone: str = "",
        content_type: str = "business",
        blueprint_inputs: dict = None
    ) -> SEOContent:
        """
        เรียกใช้งานโมเดล Gemini เพื่อเขียนบทความและแพ็คโซเชียลคอนเทนต์ คืนผลลัพธ์เป็นวัตถุ SEOContent
        """
        from services.blueprint_service import BlueprintService
        
        # ค้นหาค่า Blueprint ปัจจุบัน
        blueprint = BlueprintService.get_blueprint(content_type)
        
        # ควบรวมและเคลียร์ค่าอินพุตเพื่อประกอบส่งต่อเป็นบริบท
        inputs = {}
        if blueprint_inputs:
            inputs.update(blueprint_inputs)
            
        # การเติมค่ามาตรฐานจากฟังก์ชันเดิมเพื่อรักษาระบบทำงานร่วมกัน
        if topic:
            inputs["topic"] = topic
        if keyword:
            inputs["keyword"] = keyword
        if target_audience and "target_audience" not in inputs:
            inputs["target_audience"] = target_audience
        if business_type and "business_type" not in inputs:
            inputs["business_type"] = business_type
        if content_goal and "content_goal" not in inputs:
            inputs["content_goal"] = content_goal
        if tone and "tone" not in inputs:
            inputs["tone"] = tone
            
        blueprint_context = BlueprintService.build_blueprint_context(content_type, inputs)
        prompt_strategy = blueprint.get("prompt_strategy", {})
        output_labels_str = BlueprintService.get_output_requirements_description(content_type)
        
        # สร้าง Prompt แบบไดนามิกตามยุทธศาสตร์เฉพาะของ Blueprint นั้นๆ
        prompt = get_blogger_seo_prompt(
            content_type=content_type,
            blueprint_label=blueprint.get("label", "ธุรกิจ / สินค้า"),
            blueprint_context=blueprint_context,
            prompt_strategy=prompt_strategy,
            output_labels_str=output_labels_str
        )
        
        logging.info(f"กำลังส่งสัญญาณเรียกเขียนบทความไปยัง Gemini Model: '{self.model_name}' (ประเภทบลูปริ้นต์: {content_type})...")
        
        try:
            # ยิงเรียก Gemini API พร้อมบีบบังคับโครงสร้างการตอบกลับผ่าน Pydantic Model (SEOContent)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SEOContent,
                ),
            )
            
            result_json = response.text
            logging.info("Gemini API เขียนบทความประมวลผลเสร็จสิ้นและส่งข้อมูลกลับมา")
            
            # ถอดรหัสโครงสร้าง
            seo_content = SEOContent.model_validate_json(result_json)
            
            # ล้างแท็ก HTML ที่ต้นทางสำหรับข้อมูลข้อความทั้งหมด
            from utils.sanitize import strip_html_tags
            
            seo_content.seo_title = strip_html_tags(seo_content.seo_title)
            seo_content.meta_description = strip_html_tags(seo_content.meta_description)
            seo_content.slug_suggestion = strip_html_tags(seo_content.slug_suggestion)
            seo_content.focus_keyword = strip_html_tags(seo_content.focus_keyword)
            seo_content.content_summary = strip_html_tags(seo_content.content_summary)
            
            if seo_content.related_keywords:
                seo_content.related_keywords = [strip_html_tags(kw) for kw in seo_content.related_keywords]
                
            if seo_content.social_pack:
                sp = seo_content.social_pack
                sp.facebook_post = strip_html_tags(sp.facebook_post)
                sp.tiktok_hook = strip_html_tags(sp.tiktok_hook)
                sp.tiktok_script = strip_html_tags(sp.tiktok_script)
                sp.youtube_shorts_script = strip_html_tags(sp.youtube_shorts_script)
                sp.youtube_title = strip_html_tags(sp.youtube_title)
                sp.youtube_description = strip_html_tags(sp.youtube_description)
                
                # ทำความสะอาดและตรวจเช็คแฮชแท็กทีละตัว
                raw_hashtags = [strip_html_tags(ht) for ht in sp.facebook_hashtags] if sp.facebook_hashtags else []
                cleaned_hashtags = []
                for ht in raw_hashtags:
                    ht_clean = ht.strip().replace(" ", "").replace("#", "")
                    if ht_clean:
                        cleaned_hashtags.append(f"#{ht_clean}")
                
                # หากมีชื่อหน่วยงานในข้อมูลนำเข้า ให้สร้างและแทรกแฮชแท็กนำหน้า
                agency_name = inputs.get("agency_name", inputs.get("organization_name", inputs.get("institution_name", "")))
                if agency_name:
                    agency_clean = agency_name.strip().replace(" ", "").replace("#", "")
                    if agency_clean:
                        agency_tag = f"#{agency_clean}"
                        if agency_tag not in cleaned_hashtags:
                            cleaned_hashtags.insert(0, agency_tag)
                
                # ห้ามมีคำเชิงขายสำหรับหมวดราชการ/CSR/การศึกษา
                if content_type in ["government", "csr", "education"]:
                    forbidden = ["#โปรเด็ด", "#ซื้อเลย", "#ลดราคา"]
                    cleaned_hashtags = [ht for ht in cleaned_hashtags if ht not in forbidden]

                # จำกัดแฮชแท็กสูงสุด 8 รายการ
                cleaned_hashtags = cleaned_hashtags[:8]
                
                # หากมีไม่ครบ 5 ตัว ให้เติมคีย์เวิร์ดสำรองตามประเภทบลูปริ้นต์ (ไม่มีการขายของใน Gov/CSR/Edu)
                if len(cleaned_hashtags) < 5:
                    default_tags = {
                        "government": ["#ข่าวประชาสัมพันธ์", "#ประโยชน์เพื่อประชาชน", "#บริการประชาชน", "#พัฒนาชุมชน", "#ข่าวสารรัฐบาล"],
                        "csr": ["#โครงการเพื่อสังคม", "#รณรงค์รักษ์โลก", "#จิตสาธารณะ", "#สร้างแรงบันดาลใจ", "#ปันความรัก"],
                        "education": ["#สาระความรู้", "#คลังความรู้", "#การเรียนรู้", "#ทักษะชีวิต", "#วิชาการ"],
                        "event": ["#สัมมนาดีๆ", "#กิจกรรมพิเศษ", "#ลงทะเบียนฟรี", "#ข่าวสารประชาสัมพันธ์", "#ห้ามพลาด"],
                        "personal_brand": ["#ผู้นำความคิด", "#ถอดบทเรียน", "#แรงบันดาลใจ", "#ความรู้ธุรกิจ", "#พัฒนาตนเอง"],
                        "business": ["#ธุรกิจออนไลน์", "#สินค้าดีมีคุณภาพ", "#โปรโมชั่นเด็ด", "#แชร์เก็บไว้เลย", "#การตลาด"]
                    }
                    fallback_tags = default_tags.get(content_type, default_tags["business"])
                    for tag in fallback_tags:
                        if tag not in cleaned_hashtags:
                            cleaned_hashtags.append(tag)
                            if len(cleaned_hashtags) >= 8:
                                break
                                
                cleaned_hashtags = cleaned_hashtags[:8]
                sp.facebook_hashtags = cleaned_hashtags
                
                # รวมแฮชแท็กและส่งต่อประกบเข้าท้ายเนื้อหา facebook_post สองบรรทัด
                hashtags_line = " ".join(cleaned_hashtags)
                if hashtags_line and hashtags_line not in sp.facebook_post:
                    sp.facebook_post = f"{sp.facebook_post}\n\n{hashtags_line}"
                
            if seo_content.featured_image:
                fi = seo_content.featured_image
                fi.prompt = strip_html_tags(fi.prompt)
                fi.style = strip_html_tags(fi.style)
                fi.concept = strip_html_tags(fi.concept)
                
            return seo_content
            
        except Exception as e:
            logging.error(f"การเรียกเขียนบทความผ่าน Gemini API เกิดข้อผิดพลาด: {e}")
            raise e
