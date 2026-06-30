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
from models.content_models import SheetRow

# กำหนด OAuth scopes สำหรับอ่านเขียนชีตและอัปโหลด Blogger
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/blogger'
]

def get_google_credentials():
    """
    ฟังก์ชันกลางในการทำ OAuth authentication คืนค่า Credentials และเก็บข้อมูลล็อกอินลงไฟล์ token.json
    """
    creds = None
    creds_file = Settings.GOOGLE_CREDENTIALS_FILE
    token_file = Settings.GOOGLE_TOKEN_FILE
    
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            logging.warning(f"ไม่สามารถโหลด OAuth token จากไฟล์ {token_file} ได้: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logging.info("กำลังรีเฟรช OAuth Token...")
                creds.refresh(Request())
            except Exception as e:
                logging.warning(f"การรีเฟรช OAuth Token ล้มเหลว: {e} จะทำการยืนยันตัวตนใหม่")
                creds = None
                
        if not creds:
            if not os.path.exists(creds_file):
                logging.error(f"ไม่พบไฟล์ OAuth Credentials ที่ {creds_file}")
                raise FileNotFoundError(
                    f"ไม่พบไฟล์ {creds_file} กรุณาดาวน์โหลดใบรับรองสิทธิ์ (OAuth client ID) จาก Google Cloud และวางไว้ในโฟลเดอร์โครงการ"
                )
            logging.info("กำลังเปิดเว็บบราวเซอร์เพื่อขอยินยอมการเข้าถึงบัญชี Google...")
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            logging.info(f"บันทึก OAuth Token ล็อกอินแล้วลงในไฟล์ {token_file}")
            
    return creds

class SheetsService:
    """
    เซอร์วิสการจัดการเชื่อมต่อและอ่านเขียนข้อมูลแผ่นชีต Google Sheets
    """
    def __init__(self):
        self.creds = get_google_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.spreadsheet_id = Settings.GOOGLE_SHEET_ID
        self.sheet_name = Settings.GOOGLE_SHEET_NAME

    def read_waiting_rows(self) -> List[SheetRow]:
        """
        ดึงข้อมูลทั้งหมดจากตารางและกรองส่งคืนเฉพาะแถวที่มี Status = 'Waiting'
        """
        range_name = f"{self.sheet_name}!A:K"
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        except Exception as e:
            logging.error(f"ไม่สามารถดึงค่าข้อมูลจาก Google Sheets ID: {self.spreadsheet_id} ได้: {e}")
            raise e

        values = result.get('values', [])
        if not values or len(values) <= 1:
            logging.info("ไม่พบรายการข้อมูลหรือมีเพียงแถวหัวตาราง")
            return []

        waiting_rows = []
        # แถวที่ 1 เป็น Header เริ่มวนลูปที่แถวที่ 2 (index 1)
        for idx, row in enumerate(values[1:], start=2):
            padded = row + [''] * (11 - len(row))
            status = padded[3].strip() if padded[3] else ""
            
            if status.lower() == 'waiting':
                sheet_row = SheetRow(
                    row_idx=idx,
                    id=padded[0],
                    topic=padded[1],
                    keyword=padded[2],
                    status=padded[3],
                    generated_title=padded[4],
                    meta_description=padded[5],
                    blogger_post_id=padded[6],
                    blogger_url=padded[7],
                    error_message=padded[8],
                    created_at=padded[9],
                    updated_at=padded[10]
                )
                waiting_rows.append(sheet_row)
        
        logging.info(f"ดึงข้อมูลสำเร็จ ตรวจพบหัวข้อรอการเขียน (Status = Waiting) จำนวน: {len(waiting_rows)} รายการ")
        return waiting_rows

    def update_row_status(self, row_idx: int, status: str):
        """
        อัปเดตสถานะในช่อง Status และอัปเดตเวลาในช่อง Updated At
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # อัปเดตคอลัมน์ Status (D) คือช่องที่ 4
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!D{row_idx}",
                valueInputOption="RAW",
                body={"values": [[status]]}
            ).execute()
            
            # อัปเดตคอลัมน์ Updated At (K) คือช่องที่ 11
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!K{row_idx}",
                valueInputOption="RAW",
                body={"values": [[now_str]]}
            ).execute()
            
            logging.info(f"อัปเดตสถานะของแถวที่ {row_idx} เป็น '{status}' สำเร็จ")
        except Exception as e:
            logging.error(f"การอัปเดตสถานะของแถวที่ {row_idx} ล้มเหลว: {e}")
            raise e

    def update_row_success(self, row_idx: int, title: str, meta: str, post_id: str, url: str):
        """
        เมื่อประมวลผลเสร็จสมบูรณ์ ให้อัปเดตสถานะเป็น Drafted และใส่รายละเอียดผลลัพธ์บทความทั้งหมดลงชีต
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # ข้อมูลอัปเดตแบบรวดเร็วทีเดียวตั้งแต่คอลัมน์ D ถึง I
            # D: Status = Drafted
            # E: Generated Title
            # F: Meta Description
            # G: Blogger Post ID
            # H: Blogger URL
            # I: Error Message (ล้างข้อมูลเก่า)
            values = [[
                "Drafted",
                title,
                meta,
                post_id,
                url,
                ""
            ]]
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!D{row_idx}:I{row_idx}",
                valueInputOption="RAW",
                body={"values": values}
            ).execute()
            
            # อัปเดตคอลัมน์ Updated At (K)
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!K{row_idx}",
                valueInputOption="RAW",
                body={"values": [[now_str]]}
            ).execute()
            
            logging.info(f"บันทึกผลงานสำเร็จลงบนแถวที่ {row_idx} ของแผ่นชีตเรียบร้อย")
        except Exception as e:
            logging.error(f"ไม่สามารถเขียนข้อมูลผลลัพธ์ความสำเร็จลงบนแถวที่ {row_idx} ได้: {e}")
            raise e

    def update_row_error(self, row_idx: int, error_msg: str):
        """
        กรณีเกิดข้อผิดพลาดในการประมวลผล ให้อัปเดตสถานะแถวเป็น Error และเขียนสาเหตุในช่อง Error Message
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # D: Status = Error
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!D{row_idx}",
                valueInputOption="RAW",
                body={"values": [["Error"]]}
            ).execute()
            
            # I: Error Message
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!I{row_idx}",
                valueInputOption="RAW",
                body={"values": [[error_msg]]}
            ).execute()
            
            # K: Updated At
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!K{row_idx}",
                valueInputOption="RAW",
                body={"values": [[now_str]]}
            ).execute()
            
            logging.info(f"บันทึกสาเหตุข้อผิดพลาดลงชีตสำหรับแถวที่ {row_idx} สำเร็จ")
        except Exception as e:
            logging.error(f"ไม่สามารถอัปเดตข้อมูลสาเหตุข้อผิดพลาดบนแถวที่ {row_idx} ได้: {e}")
            raise e
