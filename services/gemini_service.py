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
        tone: str = ""
    ) -> SEOContent:
        """
        เรียกใช้งานโมเดล Gemini เพื่อเขียนบทความและแพ็คโซเชียลคอนเทนต์ คืนผลลัพธ์เป็นวัตถุ SEOContent
        """
        prompt = get_blogger_seo_prompt(
            topic=topic,
            keyword=keyword,
            target_audience=target_audience,
            business_type=business_type,
            content_goal=content_goal,
            tone=tone
        )
        logging.info(f"กำลังส่งสัญญานเรียกเขียนบทความไปยัง Gemini Model: '{self.model_name}'...")
        
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
