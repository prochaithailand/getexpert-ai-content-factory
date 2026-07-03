# models/credit_models.py

from typing import Optional
from pydantic import BaseModel, Field

class UserCredit(BaseModel):
    """
    โมเดลข้อมูลระดับผู้ใช้สำหรับตรวจสอบเครดิตและการชำระเงิน
    """
    user_email: str = Field(description="อีเมลของผู้ใช้สำหรับจัดแยกโควตา")
    user_name: str = Field(description="ชื่อจริง / ชื่อในการแสดงผลของผู้ใช้")
    created_at: str = Field(description="วันที่ผู้ใช้นี้เข้าลงทะเบียนเริ่มระบบครั้งแรก")
    free_credits_used: int = Field(default=0, description="จำนวนครั้งสร้างคอนเทนต์ฟรีที่ใช้ไปแล้ว (ลิมิตสูงสุด 3)")
    paid_credits_balance: int = Field(default=0, description="ยอดคงเหลือของเครดิตจ่ายเงินคงเหลือ")
    total_generated: int = Field(default=0, description="ยอดประมวลผลสะสมทั้งหมดที่สำเร็จ")
    payment_status: str = Field(default="Free Trial", description="สถานะโหมดชำระเงินของผู้ใช้ (เช่น Free Trial, Active Customer)")
    last_generated_at: str = Field(default="", description="เวลาประมวลผลงานชิ้นล่าสุด")
    updated_at: str = Field(description="เวลาปรับปรุงสถานะผู้ใช้งานล่าสุด")
    # Sprint 7 Referral Fields
    is_referral_partner: bool = Field(default=False, description="ผู้ใช้เป็น Referral Partner หรือไม่")
    referral_code: str = Field(default="", description="รหัส Referral (เช่น KALAYA001)")
    referral_link: str = Field(default="", description="ลิงก์ Referral แนะนำผู้ใช้อื่น")
    referral_started_at: str = Field(default="", description="วันที่เริ่มเป็นพาร์ทเนอร์แนะนำ")
    referral_package_paid: float = Field(default=0.0, description="จำนวนเงินที่จ่ายค่าแพ็กแนะนำ (เช่น 149)")
    referral_status: str = Field(default="", description="สถานะการแนะนำ (Active / Inactive)")
    referred_by: str = Field(default="", description="รหัสแนะนำที่เป็นผู้ส่งผู้ใช้นี้มา (Referrer Code)")

class UsageLog(BaseModel):
    """
    ประวัติบันทึกการนำเครดิตไปใช้ประมวลผลในระบบ
    """
    timestamp: str = Field(description="เวลาทำรายการ")
    user_email: str = Field(description="อีเมลผู้ทำรายการ")
    content_type: str = Field(description="ประเภทผลลัพธ์ยุทธศาสตร์บลูปริ้นต์")
    blueprint_label: str = Field(description="ชื่อแสดงประเภทบลูปริ้นต์")
    topic: str = Field(description="หัวข้อบทความที่สร้าง")
    credit_type_used: str = Field(description="ประเภทเครดิตที่ใช้หัก (free หรือ paid)")
    credits_before: int = Field(description="จำนวนเครดิตคงเหลือก่อนหัก")
    credits_after: int = Field(description="จำนวนเครดิตคงเหลือหลังหัก")
    status: str = Field(description="สถานะการทำงาน (Success หรือ Failed)")

class PaymentRecord(BaseModel):
    """
    ข้อมูลการรับชำระเงินและแจ้งเติมเครดิตด้วยมือของแอดมิน
    """
    payment_date: str = Field(description="เวลาที่โอนเงิน")
    user_email: str = Field(description="อีเมลผู้ชำระเงิน")
    package_name: str = Field(description="ชื่อชุดแพ็กเกจที่เลือกซื้อ")
    amount: float = Field(description="ยอดจำนวนเงินที่ชำระ (เช่น 99.00)")
    credits_added: int = Field(description="เครดิตเติมเพิ่ม (เช่น 10)")
    payment_method: str = Field(description="ช่องทางโอนเงิน (เช่น QR Code, Bank Transfer)")
    slip_status: str = Field(default="Pending", description="สถานะตรวจเช็คสลิป (Pending, Approved, Rejected)")
    approved_by: str = Field(default="", description="ชื่อผู้ตรวจสอบอนุมัติเครดิต")
    approved_at: str = Field(default="", description="เวลาอนุมัติสลิปโอนเงิน")
    note: str = Field(default="", description="บันทึกเพิ่มเติม")
