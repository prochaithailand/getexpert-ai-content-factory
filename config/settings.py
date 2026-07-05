import os
from dotenv import load_dotenv

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

def get_secret_or_env(key: str, default: str = None) -> str:
    """
    ดึงค่าความปลอดภัยจาก Streamlit Secrets ก่อน หากไม่พบให้ดึงจากตัวแปรสภาพแวดล้อม (.env / System ENV)
    """
    try:
        import streamlit as st
        # ในสภาพแวดล้อม Streamlit, st.secrets จะทำงานเป็นลักษณะคล้าย Dict
        if st.secrets and key in st.secrets:
            return st.secrets[key]
    except Exception:
        # หากรันคำสั่งอื่น เช่น python main.py นอกระบบ Streamlit จะลื่นไหลไปทำงานตัวถัดไป
        pass
    return os.getenv(key, default)

class Settings:
    # Gemini Configuration
    GEMINI_API_KEY = get_secret_or_env("GEMINI_API_KEY")
    GEMINI_MODEL = get_secret_or_env("GEMINI_MODEL", "gemini-2.5-flash")

    # Google Sheets Configuration
    GOOGLE_SHEET_ID = get_secret_or_env("GOOGLE_SHEET_ID")
    GOOGLE_SHEET_NAME = get_secret_or_env("GOOGLE_SHEET_NAME", "Sheet1")

    # Blogger Configuration
    BLOGGER_BLOG_ID = get_secret_or_env("BLOGGER_BLOG_ID")

    # Google OAuth File Paths
    GOOGLE_CREDENTIALS_FILE = get_secret_or_env("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_TOKEN_FILE = get_secret_or_env("GOOGLE_TOKEN_FILE", "token.json")

    # Google OAuth Raw JSON Contents (สำหรับการรันผ่านระบบ Streamlit Secrets บน Cloud)
    GOOGLE_CREDENTIALS_JSON = get_secret_or_env("GOOGLE_CREDENTIALS_JSON")
    GOOGLE_TOKEN_JSON = get_secret_or_env("GOOGLE_TOKEN_JSON")

    # Logging Configuration
    LOG_LEVEL = get_secret_or_env("LOG_LEVEL", "INFO")

    # LINE Messaging API Configuration
    LINE_CHANNEL_ACCESS_TOKEN = get_secret_or_env("LINE_CHANNEL_ACCESS_TOKEN")
    LINE_USER_ID = get_secret_or_env("LINE_USER_ID")

    @classmethod
    def validate(cls):
        """
        ตรวจสอบตัวแปรที่สำคัญว่าถูกกรอกครบถ้วนแล้วหรือยัง
        """
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.GOOGLE_SHEET_ID:
            missing.append("GOOGLE_SHEET_ID")
        if not cls.BLOGGER_BLOG_ID:
            missing.append("BLOGGER_BLOG_ID")

        if missing:
            raise ValueError(f"กรุณากรอกข้อมูลตัวแปรความปลอดภัยให้ครบถ้วน: {', '.join(missing)}")
