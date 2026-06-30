import os
from dotenv import load_dotenv

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

class Settings:
    # Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Google Sheets Configuration
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Sheet1")

    # Blogger Configuration
    BLOGGER_BLOG_ID = os.getenv("BLOGGER_BLOG_ID")

    # Google OAuth File Paths
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        """
        ตรวจสอบตัวแปรที่สำคัญใน .env ว่ากรอกครบแล้วหรือยัง
        """
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.GOOGLE_SHEET_ID:
            missing.append("GOOGLE_SHEET_ID")
        if not cls.BLOGGER_BLOG_ID:
            missing.append("BLOGGER_BLOG_ID")

        if missing:
            raise ValueError(f"กรุณากรอกข้อมูลตัวแปรสภาพแวดล้อมในไฟล์ .env ให้ครบถ้วน: {', '.join(missing)}")
