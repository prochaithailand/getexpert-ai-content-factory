from typing import Optional
from pydantic import BaseModel, Field

class ContentRequest(BaseModel):
    """
    คลาสข้อมูลตัวแทนคำขอสร้างบทความ
    """
    topic: str
    keyword: str

class GeneratedContent(BaseModel):
    """
    คลาสข้อมูลโครงสร้างบทความที่ได้มาจาก Gemini API
    """
    title: str = Field(description="ชื่อหัวข้อบทความที่น่าสนใจ ดึงดูดคนคลิก และรองรับการทำ SEO")
    meta_description: str = Field(description="บทสรุปย่อของบทความสำหรับทำ SEO ความยาวประมาณ 120-150 ตัวอักษร")
    html_content: str = Field(description="เนื้อหาบทความทั้งหมดในรูปแบบ HTML (ใช้เฉพาะแท็กมาตรฐาน เช่น <p>, <h2>, <h3>, <ul>, <li>, <strong>, <em>, <a> โดยห้ามใส่ <html>, <head>, <body> หรือสไตล์ CSS)")

class BloggerPostResult(BaseModel):
    """
    คลาสผลลัพธ์การอัปโหลดบทความเข้าสู่ Blogger API
    """
    post_id: str
    url: str

class SheetRow(BaseModel):
    """
    คลาสโมเดลตัวแทนข้อมูลของแต่ละแถวใน Google Sheets
    """
    row_idx: int  # หมายเลขแถวใน Google Sheets (เช่น แถวที่ 2)
    id: str
    topic: str
    keyword: str
    status: str
    generated_title: Optional[str] = ""
    meta_description: Optional[str] = ""
    blogger_post_id: Optional[str] = ""
    blogger_url: Optional[str] = ""
    error_message: Optional[str] = ""
    created_at: Optional[str] = ""
    updated_at: Optional[str] = ""
