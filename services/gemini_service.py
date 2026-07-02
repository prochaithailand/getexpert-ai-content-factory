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
        
        logging.info(f"กำลังส่งสัญญานเรียกเขียนบทความไปยัง Gemini Model: '{self.model_name}' (ประเภทบลูปริ้นต์: {content_type})...")
        
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
            
            # ถอดรหัสโครงสร้างและส่งกลับเป็น Pydantic Model วัตถุประมวลผล
            return SEOContent.model_validate_json(result_json)
            
        except Exception as e:
            logging.error(f"การเรียกเขียนบทความผ่าน Gemini API เกิดข้อผิดพลาด: {e}")
            raise e
