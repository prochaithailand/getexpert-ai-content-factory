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
    
    # หากพบความลับ Google Credentials JSON ในระบบ ให้เขียนใส่ไฟล์เป้าหมาย
    if Settings.GOOGLE_CREDENTIALS_JSON:
        try:
            with open(creds_file, 'w', encoding='utf-8') as f:
                f.write(Settings.GOOGLE_CREDENTIALS_JSON.strip())
            logging.info(f"ดึงข้อมูลลับ GOOGLE_CREDENTIALS_JSON และเขียนไฟล์ {creds_file} เรียบร้อยแล้ว")
        except Exception as e:
            logging.error(f"ไม่สามารถเขียนไฟล์สิทธิ์ Google Credentials ชั่วคราวได้: {e}")

    # หากพบความลับ Google Token JSON ในระบบ และยังไม่มีไฟล์ Token ให้เขียนใส่ไฟล์
    if Settings.GOOGLE_TOKEN_JSON and not os.path.exists(token_file):
        try:
            with open(token_file, 'w', encoding='utf-8') as f:
                f.write(Settings.GOOGLE_TOKEN_JSON.strip())
            logging.info(f"ดึงข้อมูลลับ GOOGLE_TOKEN_JSON และเขียนไฟล์ {token_file} เรียบร้อยแล้ว")
        except Exception as e:
            logging.error(f"ไม่สามารถเขียนไฟล์ล็อกอิน Google Token ชั่วคราวได้: {e}")
    
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
                err_msg = f"ไม่พบไฟล์คีย์ {creds_file} และไม่พบตัวแปร GOOGLE_CREDENTIALS_JSON ในความลับระบบ (Secrets)"
                logging.error(err_msg)
                raise FileNotFoundError(
                    f"{err_msg} กรุณาดาวน์โหลดไฟล์คีย์หรือป้อนสิทธิ์เข้าถึงลงในระบบคอนฟิกของเซิร์ฟเวอร์"
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
    บริการจัดการ Google Sheets สำหรับการดึงแถวรอโพสต์ และอัปเดตผลลัพธ์ SEO/Blogger/Social
    """
    _checked_sheets = set()

    def __init__(self):
        self.creds = get_google_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.spreadsheet_id = Settings.GOOGLE_SHEET_ID
        self.sheet_name = Settings.GOOGLE_SHEET_NAME

    @retry(max_retries=1, delays=[1])
    def read_waiting_rows(self) -> List[SheetRow]:
        """
        ดึงค่าแถวข้อมูลทั้งหมดในช่วงคอลัมน์ A:AJ (36 คอลัมน์) และคัดกรองเฉพาะ Status = 'Waiting'
        """
        range_name = f"{self.sheet_name}!A:AJ"
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
            # เติมแถวให้ครบ 36 คอลัมน์เพื่อความปลอดภัยย้อนหลังและป้องกัน Index Error
            padded = row + [''] * (36 - len(row))
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
                    updated_at=padded[19],
                    # ฟิลด์ใหม่ของ Sprint 4
                    target_audience=padded[20],
                    business_type=padded[21],
                    content_goal=padded[22],
                    tone=padded[23],
                    facebook_post=padded[24],
                    facebook_hashtags=padded[25],
                    tiktok_hook=padded[26],
                    tiktok_script=padded[27],
                    youtube_shorts_script=padded[28],
                    youtube_title=padded[29],
                    youtube_description=padded[30],
                    # ฟิลด์ใหม่ของ Sprint 5
                    content_type=padded[31] if padded[31] else "business",
                    blueprint_label=padded[32],
                    blueprint_inputs_json=padded[33] if padded[33] else "{}",
                    output_types_list=padded[34],
                    # ฟิลด์ใหม่ของ Sprint 6
                    user_email=padded[35]
                )
                waiting_rows.append(sheet_row)
        
        logging.info(f"ค้นพบข้อมูลบทความรอคิวเขียนใหม่ (Status = Waiting) จำนวน: {len(waiting_rows)} รายการ")
        return waiting_rows

    @retry(max_retries=1, delays=[1])
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

    @retry(max_retries=1, delays=[1])
    def update_row_success(self, row_idx: int, seo_content: SEOContent, post_id: str, url: str, retry_count: int):
        """
        อัปเดตข้อมูลบทความที่อัปโหลดสำเร็จลงใน Google Sheet
        เขียนแยก 2 ส่วนเพื่อความปลอดภัยและไม่เขียนทับคอลัมน์อินพุต (Created At (S) และ Target Audience..Tone (U:X))
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        related_kws = ", ".join(seo_content.related_keywords)
        
        # 1. อัปเดตฝั่ง SEO & Blogger (D:R) รวม 15 คอลัมน์
        values_seo = [[
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
            "",                                  # Q: Last Error
            now_str                              # R: Processed At
        ]]
        
        # 2. อัปเดตฝั่ง Social Content Pack (Y:AE) รวม 7 คอลัมน์
        facebook_hashtags_str = ", ".join(seo_content.social_pack.facebook_hashtags)
        values_social = [[
            seo_content.social_pack.facebook_post,
            facebook_hashtags_str,
            seo_content.social_pack.tiktok_hook,
            seo_content.social_pack.tiktok_script,
            seo_content.social_pack.youtube_shorts_script,
            seo_content.social_pack.youtube_title,
            seo_content.social_pack.youtube_description
        ]]
        
        try:
            # ยิงอัปเดตส่วนแรก (D:R)
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!D{row_idx}:R{row_idx}",
                valueInputOption="RAW",
                body={"values": values_seo}
            ).execute()
            
            # ยิงอัปเดตส่วนที่สอง (Y:AE)
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!Y{row_idx}:AE{row_idx}",
                valueInputOption="RAW",
                body={"values": values_social}
            ).execute()
            
            # อัปเดต Updated At ช่อง T
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!T{row_idx}",
                valueInputOption="RAW",
                body={"values": [[now_str]]}
            ).execute()
            
            logging.info(f"บันทึกประมวลผลข้อมูลบทความ SEO และ Social Pack ลงชีตแถวที่ {row_idx} สำเร็จ")
        except Exception as e:
            logging.error(f"การบันทึกบทความและโซเชียลสำเร็จลงแผ่นชีตแถวที่ {row_idx} ล้มเหลว: {e}")
            raise e

    @retry(max_retries=1, delays=[1])
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

    @retry(max_retries=1, delays=[1])
    def add_new_row(
        self, 
        topic: str, 
        keyword: str,
        target_audience: str = "",
        business_type: str = "",
        content_goal: str = "",
        tone: str = "",
        content_type: str = "business",
        blueprint_label: str = "",
        blueprint_inputs_json: str = "{}",
        output_types_list: str = "",
        user_email: str = ""
    ) -> int:
        """
        เพิ่มหัวข้อบทความและคำสั่งรายละเอียดใหม่ลงใน Google Sheet (รองรับฟิลด์ใหม่ของ Sprint 5 และ 6)
        """
        # อ่านข้อมูลคอลัมน์ A เพื่อคำนวณหา ID ถัดไป
        range_name = f"{self.sheet_name}!A:A"
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        
        new_id = 1
        new_row_idx = 2
        if values and len(values) > 1:
            new_row_idx = len(values) + 1
            try:
                last_id = int(values[-1][0])
                new_id = last_id + 1
            except (ValueError, IndexError):
                new_id = len(values)
                
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # เตรียมชุดข้อมูล 36 คอลัมน์ (A:AJ)
        row_data = [
            str(new_id),         # A: ID
            topic,               # B: Topic
            keyword,             # C: Keyword
            "Waiting",           # D: Status
            # E to R (14 columns empty outputs)
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", 
            now_str,             # S: Created At
            now_str,             # T: Updated At
            # U to X (ฟิลด์ป้อนเข้าของ Sprint 4)
            target_audience,     # U: Target Audience
            business_type,       # V: Business Type
            content_goal,        # W: Content Goal
            tone,                # X: Tone
            # Y to AE (7 columns empty social outputs)
            "", "", "", "", "", "", "",
            # AF to AI (ฟิลด์เพิ่มเติมของ Sprint 5)
            content_type,        # AF: Content Type
            blueprint_label,     # AG: Blueprint Label
            blueprint_inputs_json, # AH: Blueprint Inputs JSON
            output_types_list,   # AI: Output Types List
            user_email           # AJ: User Email (Sprint 6)
        ]
        
        write_range = f"{self.sheet_name}!A{new_row_idx}:AJ{new_row_idx}"
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=write_range,
            valueInputOption="RAW",
            body={"values": [row_data]}
        ).execute()
        
        logging.info(f"เพิ่มหัวข้อใหม่และข้อมูลอินพุตแถวที่ {new_row_idx} (ID: {new_id}) ลงชีตสำเร็จ")
        return new_row_idx

    @retry(max_retries=1, delays=[1])
    def get_row_by_index(self, row_idx: int) -> SheetRow:
        """
        ดึงข้อมูลแถวเฉพาะตามเลขดัชนีแถว (row_idx) รองรับ 36 คอลัมน์
        """
        range_name = f"{self.sheet_name}!A{row_idx}:AJ{row_idx}"
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        
        if not values:
            raise ValueError(f"ไม่พบข้อมูลในแถวที่ {row_idx}")
            
        padded = values[0] + [''] * (36 - len(values[0]))
        return SheetRow(
            row_idx=row_idx,
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
            updated_at=padded[19],
            # ฟิลด์ใหม่ของ Sprint 4
            target_audience=padded[20],
            business_type=padded[21],
            content_goal=padded[22],
            tone=padded[23],
            facebook_post=padded[24],
            facebook_hashtags=padded[25],
            tiktok_hook=padded[26],
            tiktok_script=padded[27],
            youtube_shorts_script=padded[28],
            youtube_title=padded[29],
            youtube_description=padded[30],
            # ฟิลด์ใหม่ของ Sprint 5
            content_type=padded[31] if padded[31] else "business",
            blueprint_label=padded[32],
            blueprint_inputs_json=padded[33] if padded[33] else "{}",
            output_types_list=padded[34],
            # ฟิลด์ใหม่ของ Sprint 6
            user_email=padded[35]
        )

    @retry(max_retries=1, delays=[1])
    def read_all_rows(self) -> List[SheetRow]:
        """
        ดึงข้อมูลทุกแถวคิวประมวลผล (ช่วง A:AJ) เพื่อนำไปจัดแสดงในตารางคิวงานบนหน้า Web App
        """
        range_name = f"{self.sheet_name}!A:AJ"
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        except Exception as e:
            logging.error(f"ดึงข้อมูลคิวงานทั้งหมดไม่สำเร็จ: {e}")
            raise e

        values = result.get('values', [])
        if not values or len(values) <= 1:
            return []

        all_rows = []
        for idx, row in enumerate(values[1:], start=2):
            padded = row + [''] * (36 - len(row))
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
                updated_at=padded[19],
                # ฟิลด์ใหม่ของ Sprint 4
                target_audience=padded[20],
                business_type=padded[21],
                content_goal=padded[22],
                tone=padded[23],
                facebook_post=padded[24],
                facebook_hashtags=padded[25],
                tiktok_hook=padded[26],
                tiktok_script=padded[27],
                youtube_shorts_script=padded[28],
                youtube_title=padded[29],
                youtube_description=padded[30],
                # ฟิลด์ใหม่ของ Sprint 5
                content_type=padded[31] if padded[31] else "business",
                blueprint_label=padded[32],
                blueprint_inputs_json=padded[33] if padded[33] else "{}",
                output_types_list=padded[34],
                # ฟิลด์ใหม่ของ Sprint 6
                user_email=padded[35]
            )
            all_rows.append(sheet_row)
        return all_rows

    @retry(max_retries=1, delays=[1])
    def ensure_worksheet_exists(self, sheet_title: str, expected_headers: List[str]):
        """
        ตรวจสอบและสร้าง Worksheet ใหม่ใน Google Sheets หากยังไม่มีอยู่
        """
        if sheet_title in self._checked_sheets:
            return
            
        try:
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheets = spreadsheet.get('sheets', [])
            sheet_titles = [s['properties']['title'] for s in sheets]
            
            if sheet_title not in sheet_titles:
                logging.info(f"ไม่พบชีตย่อย '{sheet_title}' กำลังดำเนินการจัดสร้างแผ่นใหม่...")
                body = {
                    'requests': [
                        {
                            'addSheet': {
                                'properties': {
                                    'title': sheet_title
                                }
                            }
                        }
                    ]
                }
                self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()
                
                # เขียนหัวตารางทันทีที่สร้าง
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_title}!A1",
                    valueInputOption="RAW",
                    body={"values": [expected_headers]}
                ).execute()
                logging.info(f"จัดสร้างชีตย่อย '{sheet_title}' และป้อนหัวตารางสมบูรณ์")
            
            self._checked_sheets.add(sheet_title)
        except Exception as e:
            logging.error(f"ไม่สามารถตรวจสอบ/สร้างชีตย่อย '{sheet_title}' ได้: {e}")
            raise e

    @retry(max_retries=1, delays=[1])
    def get_user_by_email(self, email: str):
        """
        ค้นหาข้อมูลผู้ใช้งานจากอีเมลในชีต Users คืนค่าเป็นโมเดล UserCredit หรือ None
        """
        self.ensure_worksheet_exists("Users", [
            "User Email", "User Name", "Created At", "Free Credits Used", 
            "Paid Credits Balance", "Total Generated", "Payment Status", 
            "Last Generated At", "Updated At", "Is Referral Partner",
            "Referral Code", "Referral Link", "Referral Started At",
            "Referral Package Paid", "Referral Status", "Referred By"
        ])
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range="Users!A:P").execute()
            values = result.get('values', [])
            
            if not values or len(values) <= 1:
                return None
                
            email_lower = email.strip().lower()
            for idx, row in enumerate(values[1:], start=2):
                if row and row[0].strip().lower() == email_lower:
                    padded = row + [''] * (16 - len(row))
                    from models.credit_models import UserCredit
                    
                    is_ref = padded[9].strip().lower() == "true"
                    ref_pkg_paid = 0.0
                    try:
                        ref_pkg_paid = float(padded[13]) if padded[13] else 0.0
                    except ValueError:
                        pass
                        
                    return UserCredit(
                        user_email=padded[0],
                        user_name=padded[1],
                        created_at=padded[2],
                        free_credits_used=int(padded[3]) if padded[3].isdigit() else 0,
                        paid_credits_balance=int(padded[4]) if padded[4].isdigit() else 0,
                        total_generated=int(padded[5]) if padded[5].isdigit() else 0,
                        payment_status=padded[6] if padded[6] else "Free Trial",
                        last_generated_at=padded[7],
                        updated_at=padded[8],
                        is_referral_partner=is_ref,
                        referral_code=padded[10],
                        referral_link=padded[11],
                        referral_started_at=padded[12],
                        referral_package_paid=ref_pkg_paid,
                        referral_status=padded[14],
                        referred_by=padded[15]
                    ), idx
            return None
        except Exception as e:
            logging.error(f"เกิดข้อผิดพลาดในการค้นหาผู้ใช้ตามอีเมล: {e}")
            raise e

    @retry(max_retries=1, delays=[1])
    def save_user_credit(self, user, row_idx: int = None):
        """
        บันทึกหรืออัปเดตข้อมูลผู้ใช้ลงชีต Users
        """
        headers = [
            "User Email", "User Name", "Created At", "Free Credits Used", 
            "Paid Credits Balance", "Total Generated", "Payment Status", 
            "Last Generated At", "Updated At", "Is Referral Partner",
            "Referral Code", "Referral Link", "Referral Started At",
            "Referral Package Paid", "Referral Status", "Referred By"
        ]
        self.ensure_worksheet_exists("Users", headers)
        
        row_data = [
            user.user_email,
            user.user_name,
            user.created_at,
            str(user.free_credits_used),
            str(user.paid_credits_balance),
            str(user.total_generated),
            user.payment_status,
            user.last_generated_at,
            user.updated_at,
            "TRUE" if user.is_referral_partner else "FALSE",
            user.referral_code,
            user.referral_link,
            user.referral_started_at,
            str(user.referral_package_paid),
            user.referral_status,
            user.referred_by
        ]
        
        try:
            if row_idx:
                # ทำการอัปเดตแถวเดิมที่มีอยู่แล้ว
                write_range = f"Users!A{row_idx}:P{row_idx}"
            else:
                # หาแถวใหม่โดยดูจำนวนแถวปัจจุบัน
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id, range="Users!A:A").execute()
                values = result.get('values', [])
                new_row = len(values) + 1 if values else 2
                write_range = f"Users!A{new_row}:P{new_row}"
                
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=write_range,
                valueInputOption="RAW",
                body={"values": [row_data]}
            ).execute()
            logging.info(f"บันทึกผู้ใช้ {user.user_email} สำเร็จที่พิกัด {write_range}")
        except Exception as e:
            logging.error(f"ไม่สามารถบันทึกข้อมูลผู้ใช้ลงชีตได้: {e}")
            raise e

    @retry(max_retries=1, delays=[1])
    def add_usage_log(self, log):
        """
        บันทึกรายการใช้งานเครดิตลงชีต Usage Logs
        """
        headers = [
            "Timestamp", "User Email", "Content Type", "Blueprint Label", 
            "Topic", "Credit Type Used", "Credits Before", "Credits After", "Status"
        ]
        self.ensure_worksheet_exists("Usage Logs", headers)
        
        row_data = [
            log.timestamp,
            log.user_email,
            log.content_type,
            log.blueprint_label,
            log.topic,
            log.credit_type_used,
            str(log.credits_before),
            str(log.credits_after),
            log.status
        ]
        
        try:
            # เพิ่มต่อท้ายแถวสุดท้าย
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range="Usage Logs!A:A").execute()
            values = result.get('values', [])
            new_row = len(values) + 1 if values else 2
            
            write_range = f"Usage Logs!A{new_row}:I{new_row}"
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=write_range,
                valueInputOption="RAW",
                body={"values": [row_data]}
            ).execute()
            logging.info(f"บันทึก Usage Log สำหรับ {log.user_email} สำเร็จ")
        except Exception as e:
            logging.error(f"ไม่สามารถบันทึก Usage Log ลงชีตได้: {e}")
            raise e

    @retry(max_retries=1, delays=[1])
    def add_payment_record(self, payment):
        """
        บันทึกข้อมูลการชำระเงินโอนซื้อเครดิตลงชีต Payments
        """
        headers = [
            "Payment Date", "User Email", "Package Name", "Amount", 
            "Credits Added", "Payment Method", "Slip Status", "Approved By", 
            "Approved At", "Note"
        ]
        self.ensure_worksheet_exists("Payments", headers)
        
        row_data = [
            payment.payment_date,
            payment.user_email,
            payment.package_name,
            str(payment.amount),
            str(payment.credits_added),
            payment.payment_method,
            payment.slip_status,
            payment.approved_by,
            payment.approved_at,
            payment.note
        ]
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range="Payments!A:A").execute()
            values = result.get('values', [])
            new_row = len(values) + 1 if values else 2
            
            write_range = f"Payments!A{new_row}:J{new_row}"
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=write_range,
                valueInputOption="RAW",
                body={"values": [row_data]}
            ).execute()
            logging.info(f"บันทึกรายการชำระเงินสำหรับ {payment.user_email} สำเร็จ")
        except Exception as e:
            logging.error(f"ไม่สามารถบันทึก Payment Record ลงชีตได้: {e}")
            raise e

    @retry(max_retries=1, delays=[1])
    def get_user_by_referral_code(self, ref_code: str):
        """
        ค้นหาข้อมูลผู้ใช้งานจากรหัสแนะนำ (Referral Code) ในชีต Users คืนค่าเป็นโมเดล UserCredit หรือ None
        """
        self.ensure_worksheet_exists("Users", [
            "User Email", "User Name", "Created At", "Free Credits Used", 
            "Paid Credits Balance", "Total Generated", "Payment Status", 
            "Last Generated At", "Updated At", "Is Referral Partner",
            "Referral Code", "Referral Link", "Referral Started At",
            "Referral Package Paid", "Referral Status", "Referred By"
        ])
        
        try:
            result = self.service.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range="Users!A:P").execute()
            values = result.get('values', [])
            
            if not values or len(values) <= 1:
                return None
                
            code_clean = ref_code.strip().upper()
            for idx, row in enumerate(values[1:], start=2):
                if len(row) > 10 and row[10].strip().upper() == code_clean:
                    padded = row + [''] * (16 - len(row))
                    from models.credit_models import UserCredit
                    
                    is_ref = padded[9].strip().lower() == "true"
                    ref_pkg_paid = 0.0
                    try:
                        ref_pkg_paid = float(padded[13]) if padded[13] else 0.0
                    except ValueError:
                        pass
                        
                    return UserCredit(
                        user_email=padded[0],
                        user_name=padded[1],
                        created_at=padded[2],
                        free_credits_used=int(padded[3]) if padded[3].isdigit() else 0,
                        paid_credits_balance=int(padded[4]) if padded[4].isdigit() else 0,
                        total_generated=int(padded[5]) if padded[5].isdigit() else 0,
                        payment_status=padded[6] if padded[6] else "Free Trial",
                        last_generated_at=padded[7],
                        updated_at=padded[8],
                        is_referral_partner=is_ref,
                        referral_code=padded[10],
                        referral_link=padded[11],
                        referral_started_at=padded[12],
                        referral_package_paid=ref_pkg_paid,
                        referral_status=padded[14],
                        referred_by=padded[15]
                    ), idx
            return None
        except Exception as e:
            logging.error(f"เกิดข้อผิดพลาดในการค้นหาผู้ใช้ตามรหัสแนะนำ: {e}")
            raise e

    @retry(max_retries=1, delays=[1])
    def add_referral_log(self, log_data: list):
        """
        บันทึกรายการคำขอบคุณและคอมมิชชั่นแนะนำลงในชีต Referral Logs
        log_data: [Timestamp, Referrer Code, Referrer Email, Referred User Email, Package Name, Payment Amount, Commission Amount, Status, Note]
        """
        headers = [
            "Timestamp", "Referrer Code", "Referrer Email", "Referred User Email", 
            "Package Name", "Payment Amount", "Commission Amount", "Status", "Note"
        ]
        self.ensure_worksheet_exists("Referral Logs", headers)
        
        try:
            result = self.service.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range="Referral Logs!A:A").execute()
            values = result.get('values', [])
            new_row = len(values) + 1 if values else 2
            
            write_range = f"Referral Logs!A{new_row}:I{new_row}"
            self.service.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=write_range,
                valueInputOption="RAW",
                body={"values": [[str(x) for x in log_data]]}
            ).execute()
            logging.info(f"บันทึก Referral Log สำหรับผู้แนะนำ {log_data[1]} สำเร็จ")
        except Exception as e:
            logging.error(f"ไม่สามารถบันทึก Referral Log ลงชีตได้: {e}")
            raise e
