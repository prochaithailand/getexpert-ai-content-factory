import os
import os.path
import logging
from datetime import datetime
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config.settings import Settings
from models.content_models import SheetRow, SEOContent
from utils.retry import retry

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/blogger'
]

def get_google_credentials():
    """
    ฟังก์ชันทำ OAuth เพื่อขอรับสิทธิ์เข้าถึงของ Google
    """
    creds = None
    creds_file = Settings.GOOGLE_CREDENTIALS_FILE
    token_file = Settings.GOOGLE_TOKEN_FILE
    
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            logging.warning(f"ไม่สามารถโหลดไฟล์ Token {token_file} ได้: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logging.info("กำลังรีเฟรช OAuth Token...")
                creds.refresh(Request())
            except Exception as e:
                logging.warning(f"รีเฟรช OAuth Token ล้มเหลว: {e} จะเริ่มล็อกอินใหม่")
                creds = None
                
        if not creds:
            if not os.path.exists(creds_file):
                logging.error(f"ไม่พบไฟล์ Credentials {creds_file}")
                raise FileNotFoundError(
                    f"ไม่พบไฟล์ {creds_file} กรุณาดาวน์โหลดและติดตั้งไฟล์คีย์จาก Google Cloud"
                )
            logging.info("กำลังขออนุญาตเข้าใช้สิทธิ์บัญชี Google ผ่านเว็บบราวเซอร์...")
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            logging.info(f"บันทึกรหัสสิทธิ์เรียบร้อยลงใน {token_file}")
            
    return creds

class SheetsService:
    """
    บริการจัดการ Google Sheets สำหรับการดึงแถวรอโพสต์ และอัปเดตผลลัพธ์ SEO/Blogger
    """
    def __init__(self):
        self.creds = get_google_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.spreadsheet_id = Settings.GOOGLE_SHEET_ID
        self.sheet_name = Settings.GOOGLE_SHEET_NAME

    @retry(max_retries=3, delays=[2, 5, 10])
    def read_waiting_rows(self) -> List[SheetRow]:
        """
        ดึงค่าแถวข้อมูลทั้งหมดในช่วงคอลัมน์ A:T (20 คอลัมน์) และคัดกรองเฉพาะ Status = 'Waiting'
        """
        range_name = f"{self.sheet_name}!A:T"
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        except Exception as e:
            logging.error(f"การดึงข้อมูลชีตล้มเหลว: {e}")
            raise e

        values = result.get('values', [])
        if not values or len(values) <= 1:
            return []

        waiting_rows = []
        for idx, row in enumerate(values[1:], start=2):
            # เติมแถวให้ครบ 20 คอลัมน์เพื่อความปลอดภัยจากการดึง Index
            padded = row + [''] * (20 - len(row))
            status = padded[3].strip() if padded[3] else ""
            
            if status.lower() == 'waiting':
                sheet_row = SheetRow(
                    row_idx=idx,
                    id=padded[0],
                    topic=padded[1],
                    keyword=padded[2],
                    status=padded[3],
                    seo_title=padded[4],
                    meta_description=padded[5],
                    blogger_post_id=padded[6],
                    blogger_url=padded[7],
                    slug_suggestion=padded[8],
                    focus_keyword=padded[9],
                    related_keywords=padded[10],
                    content_summary=padded[11],
                    featured_image_prompt=padded[12],
                    image_style=padded[13],
                    image_concept=padded[14],
                    retry_count=padded[15],
                    last_error=padded[16],
                    processed_at=padded[17],
                    created_at=padded[18],
                    updated_at=padded[19]
                )
                waiting_rows.append(sheet_row)
        
        logging.info(f"ค้นพบข้อมูลบทความรอคิวเขียนใหม่ (Status = Waiting) จำนวน: {len(waiting_rows)} รายการ")
        return waiting_rows

    @retry(max_retries=3, delays=[2, 5, 10])
    def update_row_status(self, row_idx: int, status: str):
        """
        อัปเดตสถานะของแถวข้อมูล (Status ช่อง D และ Updated At ช่อง T)
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!D{row_idx}",
                valueInputOption="RAW",
                body={"values": [[status]]}
            ).execute()
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!T{row_idx}",
                valueInputOption="RAW",
                body={"values": [[now_str]]}
            ).execute()
            
        except Exception as e:
            logging.error(f"ไม่สามารถอัปเดตสถานะของแถวที่ {row_idx} เป็น {status} ได้: {e}")
            raise e

    @retry(max_retries=3, delays=[2, 5, 10])
    def update_row_success(self, row_idx: int, seo_content: SEOContent, post_id: str, url: str, retry_count: int):
        """
        อัปเดตข้อมูลบทความที่อัปโหลดสำเร็จลงใน Google Sheet
        เขียนคลุมคอลัมน์ D ถึง R (15 คอลัมน์) เพื่อความต่อเนื่องของข้อมูลและรักษาสิทธิ์ของคอลัมน์คีย์อื่นๆ
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        related_kws = ", ".join(seo_content.related_keywords)
        
        values = [[
            "Drafted",                           # D: Status
            seo_content.seo_title,               # E: SEO Title
            seo_content.meta_description,        # F: Meta Description
            post_id,                             # G: Blogger Post ID
            url,                                 # H: Blogger URL
            seo_content.slug_suggestion,         # I: Slug Suggestion
            seo_content.focus_keyword,           # J: Focus Keyword
            related_kws,                         # K: Related Keywords
            seo_content.content_summary,         # L: Content Summary
            seo_content.featured_image.prompt,   # M: Featured Image Prompt
            seo_content.featured_image.style,    # N: Image Style
            seo_content.featured_image.concept,  # O: Image Concept
            str(retry_count),                    # P: Retry Count
            "",                                  # Q: Last Error (เคลียร์ข้อผิดพลาดเดิม)
            now_str                              # R: Processed At
        ]]
        
        try:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!D{row_idx}:R{row_idx}",
                valueInputOption="RAW",
                body={"values": values}
            ).execute()
            
            # อัปเดต Updated At ช่อง T
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!T{row_idx}",
                valueInputOption="RAW",
                body={"values": [[now_str]]}
            ).execute()
            
            logging.info(f"บันทึกประมวลผลข้อมูลบทความ SEO ลงแผ่นชีตแถวที่ {row_idx} สำเร็จ")
        except Exception as e:
            logging.error(f"การบันทึกบทความสำเร็จลงแผ่นชีตแถวที่ {row_idx} ล้มเหลว: {e}")
            raise e

    @retry(max_retries=3, delays=[2, 5, 10])
    def update_row_failed(self, row_idx: int, error_msg: str, retry_count: int):
        """
        อัปเดตข้อมูลกรณีประมวลผลล้มเหลว (Status = Failed, บันทึก Retry Count และ Last Error)
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # D: Status = Failed
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!D{row_idx}",
                valueInputOption="RAW",
                body={"values": [["Failed"]]}
            ).execute()
            
            # P: Retry Count และ Q: Last Error
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!P{row_idx}:Q{row_idx}",
                valueInputOption="RAW",
                body={"values": [[str(retry_count), error_msg]]}
            ).execute()
            
            # T: Updated At
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!T{row_idx}",
                valueInputOption="RAW",
                body={"values": [[now_str]]}
            ).execute()
            
            logging.info(f"อัปเดตสถานะความล้มเหลวของแถวที่ {row_idx} ลงชีตสำเร็จ")
        except Exception as e:
            logging.error(f"ไม่สามารถเขียนสถานะความล้มเหลวของแถวที่ {row_idx} ลงชีตได้: {e}")
            raise e
