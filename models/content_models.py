from typing import List, Optional
from pydantic import BaseModel, Field

class ContentRequest(BaseModel):
    """
    คลาสข้อมูลตัวแทนคำขอสร้างบทความ (รวมฟิลด์ไดนามิกและยุทธศาสตร์ของ Sprint 5)
    """
    topic: str
    keyword: str
    target_audience: Optional[str] = ""
    business_type: Optional[str] = ""
    content_goal: Optional[str] = ""
    tone: Optional[str] = ""
    
    # ฟิลด์เพิ่มเติมของ Sprint 5
    content_type: Optional[str] = "business"
    blueprint_inputs: Optional[dict] = Field(default_factory=dict)
    output_types: Optional[List[str]] = Field(default_factory=list)

class FAQItem(BaseModel):
    """
    คลาสรายการคำถามที่พบบ่อย (FAQ)
    """
    question: str = Field(description="คำถามยอดนิยมที่เกี่ยวกับหัวข้อบทความ")
    answer: str = Field(description="คำตอบที่กระชับ ชัดเจน และเป็นประโยชน์แก่ผู้อ่าน")

class FeaturedImagePrompt(BaseModel):
    """
    คลาสเก็บข้อแนะนำและ Prompt สำหรับภาพหน้าปกบทความ
    """
    prompt: str = Field(description="Prompt สำหรับเจนรูปภาพด้วย AI เช่น Midjourney/DALL-E เป็นภาษาอังกฤษอย่างละเอียด")
    style: str = Field(description="สไตล์รูปภาพที่ต้องการ เช่น Minimalist vector illustration, 3D render, Clean modern tech graphic")
    concept: str = Field(description="แนวคิดเบื้องหลังการออกแบบภาพประกอบปกบทความ")

class SocialContentPack(BaseModel):
    """
    คลาสรวมผลลัพธ์ของโซเชียลคอนเทนต์แพ็คสำหรับช่องทางต่างๆ (จะสลับข้อความผลลัพธ์ตามกลยุทธ์ Blueprint)
    """
    facebook_post: str = Field(description="เนื้อหาโพสต์ลง Facebook หรือ LinkedIn ตามจรรยาบรรณของ Blueprint มีอิโมจิประดับย่อหน้าสวยงาม")
    facebook_hashtags: List[str] = Field(description="รายการแฮชแท็กที่เกี่ยวข้องจำนวน 5-10 ตัว")
    tiktok_hook: str = Field(description="ประโยคเด็ดเปิดตัวดึงความสนใจ 3 วินาทีแรก (Hook) สำหรับวีดีโอสั้นหรือคลิปประชาสัมพันธ์")
    tiktok_script: str = Field(description="สคริปต์สั้นบทพูดและแนวภาพสำหรับวิดีโอสั้น ความยาว 30-60 วินาที")
    youtube_shorts_script: str = Field(description="สคริปต์พูดหรือรายละเอียดเนื้อความภาพประกอบ (Infographic text/Shorts) สำหรับวิดีโอสั้น")
    youtube_title: str = Field(description="ชื่อหัวข้อแนะนำที่ดึงดูดสายตา")
    youtube_description: str = Field(description="รายละเอียดข้อความสรุปพร้อมคีย์เวิร์ดแฮชแท็กแนะนำ")

class SEOContent(BaseModel):
    """
    คลาสผลลัพธ์การเขียนบทความ SEO และ Social Content Pack (Structured JSON Schema)
    """
    title: str = Field(description="ชื่อหัวข้อบทความ/ข่าวประชาสัมพันธ์หลัก สำหรับแสดงผลใน Blogger")
    seo_title: str = Field(description="ชื่อหัวข้อสำหรับแสดงผลใน Search Engine (SEO Title ความยาวไม่เกิน 60 ตัวอักษร)")
    meta_description: str = Field(description="สรุปเนื้อหาสั้นสำหรับแสดงใน Google Search (ความยาว 120-150 ตัวอักษร)")
    slug_suggestion: str = Field(description="ข้อเสนอแนะเกี่ยวกับส่วนท้ายของ URL หรือ Slug (ภาษาอังกฤษคั่นด้วยขีดกลาง เช่น clean-energy-project-for-public)")
    focus_keyword: str = Field(description="คีย์เวิร์ดหลักของบทความ")
    related_keywords: List[str] = Field(description="รายการคีย์เวิร์ดรองที่เกี่ยวข้องกับการทำ SEO (3-5 คำ)")
    content_summary: str = Field(description="สรุปเนื้อหาบทความแบบสั้น (Content Summary)")
    article_html: str = Field(description="เนื้อหาทั้งหมดในรูปแบบ HTML (ใช้เฉพาะแท็กมาตรฐาน เช่น <p>, <h2>, <h3>, <ul>, <li>, <strong>, <em>, <a> โดยห้ามใส่ <html>, <head>, <body> หรือสไตล์ CSS)")
    faq: List[FAQItem] = Field(description="รายการคำถามที่พบบ่อยพร้อมคำตอบ (FAQ) อย่างน้อย 3 ข้อ")
    call_to_action: str = Field(description="คำเชิญชวนหรือแนวทางการส่งต่อความต้องการ (CTA) ปิดท้ายบทความ (เช่น ชวนร่วมโครงการ/รับบริการ GetExpert)")
    internal_link_suggestion: str = Field(description="คำแนะนำประเภทหัวข้อหรือประเภทบทความเดิมที่เกี่ยวข้องเพื่อใช้เป็นคีย์เชื่อมโยงลิงก์ภายใน")
    featured_image: FeaturedImagePrompt = Field(description="ข้อแนะนำและ Prompt สำหรับสร้างภาพประกอบหน้าปก")
    suggested_visual_elements: str = Field(description="คำแนะนำองค์ประกอบภาพ แผนภูมิ หรืออินโฟกราฟิกที่ควรแทรกเพิ่มในบทความเพื่อเพิ่มคุณภาพ")
    social_pack: SocialContentPack = Field(description="ชุดข้อมูลคอนเทนต์สำหรับโพสต์บนสื่อโซเชียลมีเดียหลายช่องทาง")

class BloggerPostResult(BaseModel):
    """
    คลาสผลลัพธ์การอัปโหลดบทความเข้าสู่ Blogger API
    """
    post_id: str
    url: str

class ProcessingResult(BaseModel):
    """
    คลาสสรุปผลการรันทำงานแต่ละแถว
    """
    row_idx: int
    status: str
    post_id: Optional[str] = None
    url: Optional[str] = None
    retry_count: int = 0
    error_message: Optional[str] = None

class SheetRow(BaseModel):
    """
    คลาสโมเดลข้อมูลแถวใน Google Sheets สำหรับ Sprint 5 (รองรับคอลัมน์ A ถึง AI รวม 35 คอลัมน์)
    """
    row_idx: int
    id: str                                  # A
    topic: str                               # B
    keyword: str                             # C
    status: str                              # D
    seo_title: Optional[str] = ""            # E
    meta_description: Optional[str] = ""     # F
    blogger_post_id: Optional[str] = ""      # G
    blogger_url: Optional[str] = ""          # H
    slug_suggestion: Optional[str] = ""      # I
    focus_keyword: Optional[str] = ""        # J
    related_keywords: Optional[str] = ""     # K
    content_summary: Optional[str] = ""      # L
    featured_image_prompt: Optional[str] = ""# M
    image_style: Optional[str] = ""          # N
    image_concept: Optional[str] = ""        # O
    retry_count: Optional[str] = ""          # P
    last_error: Optional[str] = ""           # Q
    processed_at: Optional[str] = ""         # R
    created_at: Optional[str] = ""           # S
    updated_at: Optional[str] = ""           # T
    target_audience: Optional[str] = ""      # U
    business_type: Optional[str] = ""        # V
    content_goal: Optional[str] = ""         # W
    tone: Optional[str] = ""                 # X
    facebook_post: Optional[str] = ""        # Y
    facebook_hashtags: Optional[str] = ""    # Z
    tiktok_hook: Optional[str] = ""          # AA
    tiktok_script: Optional[str] = ""        # AB
    youtube_shorts_script: Optional[str] = ""# AC
    youtube_title: Optional[str] = ""        # AD
    youtube_description: Optional[str] = ""  # AE
    
    # ฟิลด์ใหม่ของ Sprint 5 (คอลัมน์ AF ถึง AI)
    content_type: Optional[str] = "business"       # AF
    blueprint_label: Optional[str] = ""            # AG
    blueprint_inputs_json: Optional[str] = "{}"    # AH
    output_types_list: Optional[str] = ""          # AI
