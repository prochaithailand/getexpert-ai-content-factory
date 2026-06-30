import logging
from google import genai
from google.genai import types

from config.settings import Settings
from models.content_models import GeneratedContent
from prompts.blogger_seo_prompt import get_blogger_seo_prompt

class GeminiService:
    """
    เซอร์วิสการจัดการเชื่อมต่อและทำงานร่วมกับ Gemini API
    """
    def __init__(self):
        self.api_key = Settings.GEMINI_API_KEY
        self.model_name = Settings.GEMINI_MODEL
        if not self.api_key:
            raise ValueError("กรุณาระบุ GEMINI_API_KEY ในไฟล์ .env")
        # เริ่มต้นโมดูล GenAI Client
        self.client = genai.Client(api_key=self.api_key)

    def generate_blogger_article(self, topic: str, keyword: str) -> GeneratedContent:
        """
        เรียกใช้งานโมเดล Gemini เพื่อเขียนบทความตามคำสั่งระบุโครงสร้าง JSON
        """
        prompt = get_blogger_seo_prompt(topic, keyword)
        logging.info(f"กำลังส่งสัญญานเรียกเขียนบทความไปยัง Gemini Model: '{self.model_name}'...")
        
        try:
            # ยิงเรียก Gemini API พร้อมบีบบังคับโครงสร้างการตอบกลับผ่าน Pydantic Model (GeneratedContent)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GeneratedContent,
                ),
            )
            
            result_json = response.text
            logging.info("Gemini API เขียนบทความประมวลผลเสร็จสิ้นและส่งข้อมูลกลับมา")
            
            # ถอดรหัสโครงสร้างและส่งกลับเป็น Pydantic Model วัตถุประมวลผล
            return GeneratedContent.model_validate_json(result_json)
            
        except Exception as e:
            logging.error(f"การเรียกเขียนบทความผ่าน Gemini API เกิดข้อผิดพลาด: {e}")
            raise e
