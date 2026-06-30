import logging
from googleapiclient.discovery import build
from config.settings import Settings
from services.sheets_service import get_google_credentials
from models.content_models import BloggerPostResult
from utils.retry import retry

class BloggerService:
    """
    เซอร์วิสการจัดการเชื่อมต่อและทำงานร่วมกับ Blogger API v3
    """
    def __init__(self):
        self.creds = get_google_credentials()
        self.service = build('blogger', 'v3', credentials=self.creds)
        self.blog_id = Settings.BLOGGER_BLOG_ID
        if not self.blog_id:
            raise ValueError("กรุณาระบุ BLOGGER_BLOG_ID ในไฟล์ .env")

    @retry(max_retries=3, delays=[2, 5, 10])
    def create_draft_post(self, title: str, html_content: str) -> BloggerPostResult:
        """
        สร้างโพสต์บทความใหม่บน Blogger ในรูปแบบแบบร่าง (Draft)
        """
        body = {
            'kind': 'blogger#post',
            'blog': {'id': self.blog_id},
            'title': title,
            'content': html_content
        }
        
        logging.info(f"กำลังเชื่อมต่อสร้างบล็อกแบบร่าง (Draft) บน Blog ID: {self.blog_id}...")
        
        try:
            # เรียก REST API ของ Blogger สั่งเพิ่มโพสต์โดยใส่ option parameter isDraft=True
            request = self.service.posts().insert(
                blogId=self.blog_id,
                body=body,
                isDraft=True
            )
            response = request.execute()
            
            post_id = response.get('id')
            post_url = response.get('url')
            
            logging.info(f"บันทึกโพสต์แบบร่างสำเร็จ ได้รับ Post ID: {post_id}")
            return BloggerPostResult(post_id=post_id, url=post_url)
            
        except Exception as e:
            logging.error(f"การอัปโหลดโพสต์แบบร่างเข้า Blogger ล้มเหลว: {e}")
            raise e
