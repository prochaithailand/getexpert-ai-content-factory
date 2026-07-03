import streamlit as st
import time
import os
import logging
import json
import re
from config.settings import Settings
from services.sheets_service import SheetsService
from services.gemini_service import GeminiService
from services.blogger_service import BloggerService
from services.blueprint_service import BlueprintService
from utils.sanitize import strip_html_tags

# กำหนดหน้าจอหลักของ Streamlit
st.set_page_config(
    page_title="GetExpert AI Content Factory Portal",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# สไตล์ CSS เพิ่มเติมเพื่อความพรีเมียม
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .status-badge {
        padding: 5px 12px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
    }
    .status-waiting { background-color: #ffeeba; color: #856404; }
    .status-processing { background-color: #b8daff; color: #004085; }
    .status-drafted { background-color: #c3e6cb; color: #155724; }
    .status-failed { background-color: #f5c6cb; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# (ฟังก์ชัน strip_html_tags ได้รับการอิมพอร์ตมาจาก utils.sanitize เรียบร้อยแล้ว)

# เริ่มต้นเรียกเซอร์วิส Sheets
@st.cache_resource
def get_sheets_service():
    return SheetsService()

try:
    sheets_service = get_sheets_service()
except Exception as e:
    st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets API ได้: {e}")
    st.stop()

# โหลดข้อมูล Blueprint ทั้งหมด
blueprints_data = BlueprintService.get_all_blueprints()

# ตรวจสอบ URL Parameter ว่าเป็น Demo Mode หรือไม่ (?demo=true)
is_demo = st.query_params.get("demo", "false").lower() == "true"

if is_demo:
    # ----------------------------------------------------
    # DEMO MODE (Client Trial - คลีนและรันตอบสนองทันที - UX Sprint 1 / Sprint 5)
    # ----------------------------------------------------
    # แสดงแบนเนอร์ด้านบนของหน้าเว็บ (Sprint 6)
    st.info("🎁 ทดลองใช้ฟรี 3 Content Packs / หลังจากนั้นเริ่มต้นเพียง 99 บาท ได้ 10 Content Credits (1 Credit = สร้างครบชุด 1 ครั้ง)")

    # Hero Section
    st.markdown("""
    <div style='text-align: center; padding: 20px 0 10px 0;'>
        <h1 style='font-size: 2.6em; font-weight: 800; color: #1e293b; margin-bottom: 12px; line-height: 1.25;'>
            🚀 เปลี่ยน 1 หัวข้อ เป็นคอนเทนต์ครบทุกช่องทางด้วย AI
        </h1>
        <p style='font-size: 1.2em; color: #64748b; font-weight: 400; margin-bottom: 25px; max-width: 800px; margin-left: auto; margin-right: auto;'>
            สร้างแผนยุทธศาสตร์เนื้อหา บทความ SEO และโซเชียลสคริปต์ที่ตรงบริบทองค์กรของคุณทันที
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Value Cards
    with st.container(border=True):
        st.markdown("<h4 style='margin-bottom: 15px; color: #1e293b; font-weight: 700;'>🎁 คุณจะได้รับคอนเทนต์ทั้งหมดจากหัวข้อเดียว:</h4>", unsafe_allow_html=True)
        v_col1, v_col2, v_col3, v_col4, v_col5 = st.columns(5)
        v_col1.markdown("📄 **SEO / PR Article**")
        v_col2.markdown("📘 **Social Media Post**")
        v_col3.markdown("🎬 **TikTok Video Script**")
        v_col4.markdown("▶️ **YouTube Shorts / Infographic**")
        v_col5.markdown("🖼️ **AI Image Prompt**")
        st.markdown("<div style='margin-top: 10px; font-size: 0.8em; color: #94a3b8; font-weight: 500; text-align: right;'>ทั้งหมดสร้างด้วยการประมวลผลยุทธศาสตร์ AI Blueprint</div>", unsafe_allow_html=True)

    st.write("") # เว้นบรรทัดสั้นๆ

    # 1. User Identification (Sprint 6)
    with st.container(border=True):
        st.markdown("##### 🔑 ระบุตัวตนก่อนใช้งานเพื่อตรวจสอบสิทธิ์เครดิตของคุณ")
        col_em, col_nm = st.columns(2)
        with col_em:
            user_email = st.text_input("อีเมลของคุณ (Email) *", placeholder="example@mail.com", key="demo_email_input").strip()
        with col_nm:
            user_name = st.text_input("ชื่อของคุณ (Name)", placeholder="สมชาย รักเรียน", key="demo_name_input").strip()
            
    # ตรวจสอบสิทธิ์เครดิต
    is_eligible = False
    credit_type = "blocked"
    credit_balance = 0
    status_msg = ""
    
    if user_email:
        from services.credit_service import CreditService
        credit_service = CreditService(sheets_service)
        # ตรวจสอบหรือสร้างผู้ใช้
        credit_service.get_or_create_user(user_email, user_name)
        is_eligible, credit_type, credit_balance, status_msg = credit_service.check_credit_eligibility(user_email)
        
        # แสดงสถานะเครดิตบนหน้าบ้าน
        if credit_type == "free":
            st.info(f"💡 {status_msg} (คุณใช้สิทธิ์ฟรีไปแล้ว {3 - credit_balance} / 3 Content Packs)")
        elif credit_type == "paid":
            st.success(f"💎 {status_msg} (คุณเหลือเครดิต {credit_balance} Content Packs)")
        elif credit_type == "blocked":
            st.error(f"⚠️ {status_msg}")
    else:
        st.warning("⚠️ กรุณากรอกอีเมลของคุณด้านบนเพื่อตรวจสอบสิทธิ์การใช้งานก่อนเริ่มสร้างคอนเทนต์")
    
    # 2. Content Type Selector
    st.write("##### 📈 เลือกประเภทงานที่ต้องการสร้างคอนเทนต์")
    selected_content_type = st.radio(
        "ประเภทคอนเทนต์ที่เหมาะสมกับเป้าหมายของคุณ:",
        options=list(blueprints_data.keys()),
        format_func=lambda k: f"{blueprints_data[k]['label']} — {blueprints_data[k]['description']}",
        key="demo_content_selector"
    )
    
    st.write("")
    col1, col2 = st.columns([1, 1.2])

    with col1:
        if not user_email:
            st.info("กรุณาระบุอีเมลด้านบนเพื่อเริ่มการกรอกรายละเอียด")
        elif not is_eligible:
            # แสดงหน้าจอ Payment Gate แทนตัวฟอร์ม (Sprint 6)
            with st.container(border=True):
                st.markdown("""
                ### 💳 คุณใช้สิทธิ์ทดลองใช้ฟรีครบ 3 Content Packs แล้ว
                
                หากต้องการสร้างคอนเทนต์ต่อ ซื้อเครดิตเริ่มต้นเพียง **99 บาท** รับ **10 Content Credits**
                
                *(1 Credit = สร้าง Content Pack ครบชุด 1 ครั้ง)*
                
                ---
                
                #### 📌 ช่องทางการชำระเงิน (Manual Payment)
                1. **สแกน QR Code หรือโอนเข้าบัญชี:**
                   - ธนาคารกสิกรไทย: 012-3-45678-9 (บริษัท เก็ทเอ็กซ์เพิร์ท จำกัด)
                2. **ส่งสลิปหลักฐานการชำระเงิน:**
                   - แอด LINE OA: **@GetExpert**
                   - ส่งรูปสลิปให้แอดมินเพื่อเติมเครดิต
                
                *แอดมินจะทำการเติมเครดิตให้คุณทันทีหลังตรวจสอบหลักฐานเรียบร้อยแล้ว*
                """)
        else:
            with st.container(border=True):
                st.subheader("💡 ป้อนรายละเอียดตามบลูปริ้นต์")
                
                with st.form("demo_content_form", clear_on_submit=False):
                    blueprint_inputs = {}
                
                # แสดงฟอร์มตามลักษณะยุทธศาสตร์ประเภทที่เลือก (Dynamic Form)
                if selected_content_type == "business":
                    topic = st.text_input("หัวข้อที่ต้องการสร้างคอนเทนต์ *", placeholder="น้ำมันสนเข็มแดงช่วยบรรเทาอาการปวดเมื่อยได้อย่างไร")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="น้ำมันสนเข็มแดง")
                    st.write("---")
                    st.markdown("**🎯 ข้อมูลแนวทางแบรนด์ (Brand Guidelines)**")
                    blueprint_inputs["business_name"] = st.text_input("ชื่อธุรกิจ / สินค้าของคุณคืออะไร", placeholder="เช่น GetExpert คลินิกสุขภาพ")
                    blueprint_inputs["target_audience"] = st.text_input("ลูกค้ากลุ่มเป้าหมายคือใคร", placeholder="เช่น คนวัยทำงานที่มีอาการปวดเมื่อยคอบ่าไหล่")
                    blueprint_inputs["customer_problem"] = st.text_input("ปัญหาหลักของลูกค้าคืออะไร", placeholder="เช่น ปวดเมื่อยเรื้อรังจากออฟฟิศซินโดรม")
                    blueprint_inputs["unique_value"] = st.text_input("จุดเด่นของสินค้า / บริการ", placeholder="เช่น สกัดจากสมุนไพรธรรมชาติซึมไวไม่เหนียวเหนอะหนะ")
                    blueprint_inputs["marketing_goal"] = st.text_input("เป้าหมายการตลาด", placeholder="เช่น สร้างความเชื่อมั่นและเพิ่มยอดขาย")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น เป็นกันเอง เข้าใจง่าย น่าเชื่อถือ")
                    blueprint_inputs["cta"] = st.text_input("คำเชิญชวนดำเนินการ (CTA)", placeholder="เช่น สั่งซื้อวันนี้รับส่วนลด 20%")
                    
                elif selected_content_type == "government":
                    topic = st.text_input("หัวข้อประชาสัมพันธ์ *", placeholder="โครงการจัดการขยะอิเล็กทรอนิกส์ในชุมชน")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="ขยะอิเล็กทรอนิกส์, จัดการขยะ")
                    st.write("---")
                    st.markdown("**🏛 ข้อมูลประชาสัมพันธ์ภาครัฐ (Government Context)**")
                    blueprint_inputs["agency_name"] = st.text_input("ชื่อหน่วยงานราชการของคุณ", placeholder="เช่น เทศบาลตำบลแสนสุข")
                    blueprint_inputs["public_target"] = st.text_input("ประชาชนกลุ่มเป้าหมาย", placeholder="เช่น ผู้อยู่อาศัยในเขตเทศบาลแสนสุข")
                    blueprint_inputs["project_objective"] = st.text_input("วัตถุประสงค์ของโครงการ", placeholder="เช่น รณรงค์แยกทิ้งขยะอันตรายอย่างถูกวิธี")
                    blueprint_inputs["public_benefit"] = st.text_input("ประโยชน์ที่ประชาชนจะได้รับ", placeholder="เช่น ชุมชนสะอาด ปลอดภัยจากสารพิษตกค้าง")
                    blueprint_inputs["key_information"] = st.text_input("ข้อมูลสำคัญที่ต้องการแจ้ง", placeholder="เช่น จุดบริการรับทิ้งขยะทุกวันเสาร์ที่ลานหน้าอำเภอ")
                    blueprint_inputs["contact_channel"] = st.text_input("ช่องทางติดต่อ / เข้าร่วม", placeholder="เช่น โทรสายด่วนเทศบาล 1133 หรือเพจเทศบาล")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น สุภาพ เป็นทางการ น่าเชื่อถือ เข้าใจง่าย")
                    
                elif selected_content_type == "csr":
                    topic = st.text_input("ชื่อโครงการ / แคมเปญ *", placeholder="แคมเปญบริจาคหนังสือเก่าเพื่อน้องในชนบท")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="บริจาคหนังสือ, ปันความรู้")
                    st.write("---")
                    st.markdown("**❤️ ข้อมูลโครงการเพื่อสังคม (CSR Impact Context)**")
                    blueprint_inputs["campaign_name"] = st.text_input("ชื่อแคมเปญเพื่อสังคม", placeholder="เช่น โครงการห้องสมุดปันฝัน")
                    blueprint_inputs["social_problem"] = st.text_input("ปัญหาสังคมที่ต้องการแก้", placeholder="เช่น โรงเรียนชายขอบขาดแคลนหนังสือเสริมทักษะ")
                    blueprint_inputs["affected_group"] = st.text_input("กลุ่มเป้าหมายที่ได้รับผลกระทบ", placeholder="เช่น นักเรียนโรงเรียนบ้านดอยสามสิบ")
                    blueprint_inputs["campaign_goal"] = st.text_input("เป้าหมายของโครงการ", placeholder="เช่น รวบรวมหนังสืออ่านนอกเวลาจำนวน 500 เล่ม")
                    blueprint_inputs["expected_impact"] = st.text_input("ผลลัพธ์ที่คาดหวัง", placeholder="เช่น ช่วยพัฒนาทักษะการอ่านและส่งเสริมโอกาสเด็กไทย")
                    blueprint_inputs["participation_invite"] = st.text_input("สิ่งที่อยากเชิญชวนให้คนมีส่วนร่วม", placeholder="เช่น เชิญชวนบริจาคหนังสือสภาพดีที่จุดรับบริจาค")
                    blueprint_inputs["organization_name"] = st.text_input("หน่วยงาน / องค์กรเจ้าของโครงการ", placeholder="เช่น บริษัท กรีนคอร์ป ร่วมกับ มูลนิธิปัญญา")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น สร้างแรงบันดาลใจ อบอุ่น มีความหวัง เชิญชวน")
                    
                elif selected_content_type == "education":
                    topic = st.text_input("หัวข้อบทเรียน / กิจกรรม *", placeholder="พื้นฐานการประหยัดพลังงานไฟฟ้าง่ายๆ ในชีวิตประจำวัน")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="ประหยัดไฟฟ้า, พลังงานในบ้าน")
                    st.write("---")
                    st.markdown("**🎓 ข้อมูลด้านการศึกษา (Educational Context)**")
                    blueprint_inputs["institution_name"] = st.text_input("ชื่อสถาบันการศึกษา / มหาวิทยาลัย", placeholder="เช่น โรงเรียนวิทยารักษ์ หรือคอร์สออนไลน์ GetAcademy")
                    blueprint_inputs["learner_group"] = st.text_input("ระดับชั้น / กลุ่มผู้เรียน", placeholder="เช่น นักเรียนมัธยมศึกษาตอนต้น หรือผู้เรียนทั่วไป")
                    blueprint_inputs["learning_objective"] = st.text_input("วัตถุประสงค์การเรียนรู้", placeholder="เช่น เพื่อเข้าใจการเลือกใช้เครื่องใช้ไฟฟ้าอย่างประหยัดและถูกวิธี")
                    blueprint_inputs["core_knowledge"] = st.text_input("สาระสำคัญที่ต้องการสื่อ", placeholder="เช่น การปิดไฟดวงที่ไม่ใช้, เลือกใช้แอร์เบอร์ 5, คำนวณค่าไฟคร่าวๆ")
                    blueprint_inputs["expected_outcome"] = st.text_input("ผลลัพธ์ที่คาดหวังจากผู้เรียน", placeholder="เช่น ปรับเปลี่ยนพฤติกรรมเพื่อช่วยลดรายจ่ายในครอบครัว")
                    blueprint_inputs["content_format"] = st.text_input("รูปแบบเนื้อหาที่ต้องการ", placeholder="เช่น บทเรียนสรุปสั้น 3 ประเด็นสำคัญพร้อมข้อดี")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น เข้าใจง่าย มีเหตุผลเชิงวิทยาศาสตร์ สนุกสนานและสร้างสรรค์")
                    
                elif selected_content_type == "event":
                    topic = st.text_input("ชื่องาน / กิจกรรม *", placeholder="งานสัมมนาติดอาวุธการเขียนบทความยอดขายล้านวิว")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="สัมมนาการเขียน, Content Marketing")
                    st.write("---")
                    st.markdown("**🎉 ข้อมูลการประชาสัมพันธ์กิจกรรม (Event Context)**")
                    blueprint_inputs["event_name"] = st.text_input("ชื่อกิจกรรมประชาสัมพันธ์", placeholder="เช่น สัมมนา Write to Millionaire")
                    blueprint_inputs["organizer_name"] = st.text_input("หน่วยงานหรือผู้จัด", placeholder="เช่น GetExpert AI Content Platform")
                    blueprint_inputs["event_objective"] = st.text_input("วัตถุประสงค์ของงาน", placeholder="เช่น เพื่อเผยแพร่เทคนิคการทำ Content Marketing ยอดคนดูเยอะ")
                    blueprint_inputs["date_time_location"] = st.text_input("วัน เวลา สถานที่จัดงาน", placeholder="เช่น วันที่ 25 กรกฎาคม 2570 เวลา 13:00 - 17:00 น. ณ ฮอลล์ 5 ไบเทคบางนา")
                    blueprint_inputs["event_highlights"] = st.text_input("จุดเด่นของงาน", placeholder="เช่น แขกรับเชิญพิเศษจากครีเอเตอร์ชื่อดัง และแจกคอร์สสรุปฟรี")
                    blueprint_inputs["attendee_benefits"] = st.text_input("สิ่งที่ผู้เข้าร่วมจะได้รับ", placeholder="เช่น ไฟล์เทมเพลตโพสต์เขียน 10 แบบฟรี และเครือข่ายผู้เข้าร่วมงาน")
                    blueprint_inputs["registration_channel"] = st.text_input("ช่องทางลงทะเบียน / ติดต่อ", placeholder="เช่น แอดไลน์ @getexpert หรือจองตั๋วผ่าน getexpert.co/tickets")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น กระตุ้นความสนใจ น่าตื่นเต้น เชื้อเชิญ กระชับชัดเจน")
                    
                elif selected_content_type == "personal_brand":
                    topic = st.text_input("หัวข้อที่ต้องการสื่อสาร *", placeholder="บทเรียนที่สำคัญที่สุดที่ผมเรียนรู้หลังจากเจ๊งธุรกิจรอบแรก")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="บทเรียนการทำธุรกิจ, ถอดบทเรียนความล้มเหลว")
                    st.write("---")
                    st.markdown("**👤 ข้อมูลแบรนด์บุคคล (Personal Branding)**")
                    blueprint_inputs["expert_niche"] = st.text_input("ความเชี่ยวชาญ / กลุ่มวิชาชีพของคุณ", placeholder="เช่น ที่ปรึกษาผู้บริหารและนักวางกลยุทธ์ธุรกิจ")
                    blueprint_inputs["target_followers"] = st.text_input("ผู้ติดตามหรือกลุ่มเป้าหมายคือใคร", placeholder="เช่น เจ้าของธุรกิจรุ่นใหม่และพนักงานฝันอยากมีธุรกิจ")
                    blueprint_inputs["experience_story"] = st.text_input("ประสบการณ์หรือมุมมองสำคัญที่เล่า", placeholder="เช่น ประสบการณ์จัดงบการเงินพังจนต้องปิดร้านกาแฟร้านแรกในชีวิต")
                    blueprint_inputs["core_identity"] = st.text_input("ภาพลักษณ์ที่ต้องการสร้าง", placeholder="เช่น ผู้เชี่ยวชาญตัวจริง ตรงไปตรงมา มีความจริงใจพร้อมแบ่งปัน")
                    blueprint_inputs["key_takeaway"] = st.text_input("ข้อความหลักที่อยากให้คนจดจำ", placeholder="เช่น กระแสเงินสดสำคัญกว่ากำไรทางบัญชีเสมอ")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น เล่าเรื่องแบบภาพยนตร์ จริงใจ เป็นธรรมชาติ ถ่อมตัวแต่มีความรู้")
                    blueprint_inputs["cta"] = st.text_input("คำเชิญชวนดำเนินการ (CTA)", placeholder="เช่น กดแชร์แบ่งปันบทเรียนนี้ หรือลงทะเบียนรับข่าวสารรายสัปดาห์")

                submitted = st.form_submit_button("✨ สร้าง Content Pack", disabled=st.session_state.get('is_processing', False))
                
                if submitted:
                    if not topic or not keyword:
                        st.error("กรุณากรอกทั้งหัวข้อและคีย์เวิร์ด (ช่องที่มีเครื่องหมาย *)")
                    elif st.session_state.get('is_processing', False):
                        st.warning("ระบบกำลังประมวลผลงานชิ้นก่อนหน้า กรุณารอสักครู่...")
                    elif not user_email:
                        st.error("กรุณากรอกอีเมลของคุณก่อนเริ่มสร้างคอนเทนต์")
                    elif not is_eligible:
                        st.error("โควตาเครดิตไม่เพียงพอ กรุณาติดต่อชำระเงินซื้อเครดิต")
                    else:
                        # ล็อกกันกดซ้ำ
                        st.session_state['is_processing'] = True
                        
                        try:
                            # รันประมวลผลแบบ Synchronous พร้อม st.status ลิสต์ทีละขั้นตอน
                            with st.status("🧠 วิเคราะห์ยุทธศาสตร์และหัวข้อ...", expanded=True) as status_box:
                                
                                # 1. เตรียมข้อมูล Blueprint สำหรับ Google Sheets
                                status_box.update(label="📚 บันทึกแผนงานและวิเคราะห์คีย์เวิร์ด...")
                                blueprint_label = blueprints_data[selected_content_type]["label"]
                                blueprint_inputs_json = json.dumps(blueprint_inputs, ensure_ascii=False)
                                output_types_list = ", ".join(blueprints_data[selected_content_type]["outputs"].keys())
                                
                                # แมปข้อมูลสำหรับคอลัมน์ U:X เดิมเพื่อความเข้ากันได้ย้อนหลัง
                                target_audience = blueprint_inputs.get("target_audience", blueprint_inputs.get("public_target", blueprint_inputs.get("target_followers", "")))
                                business_type = blueprint_inputs.get("business_name", blueprint_inputs.get("agency_name", blueprint_inputs.get("organization_name", blueprint_inputs.get("institution_name", ""))))
                                content_goal = blueprint_inputs.get("marketing_goal", blueprint_inputs.get("project_objective", blueprint_inputs.get("campaign_goal", blueprint_inputs.get("learning_objective", ""))))
                                tone = blueprint_inputs.get("tone", "")
                                
                                row_idx = sheets_service.add_new_row(
                                    topic=topic,
                                    keyword=keyword,
                                    target_audience=target_audience,
                                    business_type=business_type,
                                    content_goal=content_goal,
                                    tone=tone,
                                    content_type=selected_content_type,
                                    blueprint_label=blueprint_label,
                                    blueprint_inputs_json=blueprint_inputs_json,
                                    output_types_list=output_types_list,
                                    user_email=user_email
                                )
                                sheets_service.update_row_status(row_idx, "Processing")
                                
                                # 2. เรียกใช้งาน Gemini API
                                status_box.update(label="✍️ สร้างบทความคุณภาพสูง...")
                                gemini_service = GeminiService()
                                seo_content = gemini_service.generate_blogger_article(
                                    topic=topic,
                                    keyword=keyword,
                                    target_audience=target_audience,
                                    business_type=business_type,
                                    content_goal=content_goal,
                                    tone=tone,
                                    content_type=selected_content_type,
                                    blueprint_inputs=blueprint_inputs
                                )
                                
                                # 3. อัปโหลดขึ้น Blogger Draft
                                status_box.update(label="📘 จัดเตรียมโซเชียลมีเดียสลับเนื้อหา...")
                                
                                status_box.update(label="🔗 อัปโหลดแบบร่างหลังบ้าน...")
                                blogger_service = BloggerService()
                                
                                faq_html = ""
                                if seo_content.faq:
                                    faq_html = "<h2>คำถามที่พบบ่อย (FAQ)</h2><ul>"
                                    for item in seo_content.faq:
                                        faq_html += f"<li><strong>{item.question}</strong><br/>{item.answer}</li>"
                                    faq_html += "</ul>"
                                
                                cta_html = ""
                                if seo_content.call_to_action:
                                    cta_html = f"<div class='cta-section' style='margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-left: 5px solid #007bff;'><p>{seo_content.call_to_action}</p></div>"
                                
                                full_html = seo_content.article_html + faq_html + cta_html
                                post_result = blogger_service.create_draft_post(seo_content.title, full_html)
                                
                                # 4. อัปเดตชีตสำเร็จ
                                sheets_service.update_row_success(
                                    row_idx=row_idx,
                                    seo_content=seo_content,
                                    post_id=post_result.post_id,
                                    url=post_result.url,
                                    retry_count=0
                                )
                                
                                # 5. หักแต้มเครดิตผู้ใช้อัตโนมัติ (Sprint 6)
                                from services.credit_service import CreditService
                                credit_service = CreditService(sheets_service)
                                credit_service.consume_credit(
                                    email=user_email,
                                    credit_type=credit_type,
                                    topic=topic,
                                    content_type=selected_content_type,
                                    blueprint_label=blueprint_label
                                )
                                
                                status_box.update(label="✅ Content Pack พร้อมใช้งาน", state="complete", expanded=False)
                            
                            # บันทึกข้อมูลลง Session State
                            facebook_hashtags_str = ", ".join(seo_content.social_pack.facebook_hashtags)
                            related_kws_str = ", ".join(seo_content.related_keywords)
                            
                            st.session_state['demo_result'] = {
                                "blogger_url": post_result.url,
                                "seo_title": seo_content.seo_title,
                                "meta_description": seo_content.meta_description,
                                "slug_suggestion": seo_content.slug_suggestion,
                                "focus_keyword": seo_content.focus_keyword,
                                "related_keywords": related_kws_str,
                                "content_summary": seo_content.content_summary,
                                "facebook_post": seo_content.social_pack.facebook_post,
                                "facebook_hashtags": facebook_hashtags_str,
                                "tiktok_hook": seo_content.social_pack.tiktok_hook,
                                "tiktok_script": seo_content.social_pack.tiktok_script,
                                "youtube_title": seo_content.social_pack.youtube_title,
                                "youtube_description": seo_content.social_pack.youtube_description,
                                "youtube_shorts_script": seo_content.social_pack.youtube_shorts_script,
                                "featured_image_prompt": seo_content.featured_image.prompt,
                                "image_style": seo_content.featured_image.style,
                                "image_concept": seo_content.featured_image.concept,
                                "article_html": full_html,
                                # ข้อมูล Sprint 5
                                "content_type": selected_content_type,
                                "blueprint_label": blueprint_label,
                                "outputs_map": blueprints_data[selected_content_type]["outputs"]
                            }
                            st.session_state['is_processing'] = False
                            st.rerun()
                            
                        except Exception as err:
                            st.session_state['is_processing'] = False
                            st.error(f"เกิดข้อผิดพลาดในการประมวลผลสัญญาน: {err}")
                            # บันทึกประวัติความล้มเหลวลงในชีต Usage Logs โดยไม่หักแต้มเครดิต
                            try:
                                from services.credit_service import CreditService
                                credit_service = CreditService(sheets_service)
                                credit_service.log_failed_generation(
                                    email=user_email,
                                    credit_type=credit_type,
                                    topic=topic,
                                    content_type=selected_content_type,
                                    blueprint_label=blueprint_label,
                                    error_msg=str(err)
                                )
                            except Exception as log_err:
                                logging.error(f"ไม่สามารถบันทึก Usage Log ล้มเหลวได้: {log_err}")

    with col2:
        with st.container(border=True):
            if 'demo_result' in st.session_state:
                res = st.session_state['demo_result']
                
                # Success Banner
                st.success("🎉 Content Pack พร้อมใช้งานแล้ว")
                st.info(f"📋 ประเภทคอนเทนต์: **{res.get('blueprint_label', 'ธุรกิจ')}**")
                
                # ดึงโครงสร้าง Tab Labels ไดนามิกเฉพาะของแต่ละ Blueprint
                outputs_map = res.get("outputs_map", {})
                tab_labels = [
                    outputs_map.get("seo_article", "📰 Blogger & SEO"),
                    outputs_map.get("facebook_post", "📘 Facebook Post"),
                    outputs_map.get("tiktok_script", "🎵 TikTok Script"),
                    outputs_map.get("youtube_script", "🔴 YouTube Shorts"),
                    outputs_map.get("image_prompt", "🎨 Image Prompts")
                ]
                
                tab_blogger, tab_facebook, tab_tiktok, tab_youtube, tab_image = st.tabs(tab_labels)
                
                with tab_blogger:
                    st.info("📋 คัดลอกเพื่อนำไปใช้งานได้ทันที (คลิกปุ่ม Copy มุมขวาบนของกล่องข้อความดิบ หรือก๊อปปี้ HTML ด้านล่างสุด)")
                    st.markdown(f"##### 📋 คัดลอก{outputs_map.get('seo_article', 'บทความทั้งหมด')} (ข้อความธรรมดา)")
                    clean_text = strip_html_tags(res['article_html'])
                    full_copyable_text = f"หัวข้อ (Title): {strip_html_tags(res['seo_title'])}\nคำโปรย (Meta Description): {strip_html_tags(res['meta_description'])}\n\n{clean_text}"
                    st.code(full_copyable_text, language=None)
                    
                    st.write("---")
                    st.write(f"**SEO Title:** {strip_html_tags(res['seo_title'])}")
                    st.write(f"**Meta Description:** {strip_html_tags(res['meta_description'])}")
                    st.write(f"**Slug (URL แนะนำ):** `{strip_html_tags(res['slug_suggestion'])}`")
                    st.write(f"**Focus Keyword:** {strip_html_tags(res['focus_keyword'])}")
                    st.write(f"**Summary:** {strip_html_tags(res['content_summary'])}")
                    
                    st.write("---")
                    st.markdown("##### 👀 ตัวอย่างหน้าตาบทความ (Formatted Preview)")
                    st.markdown(res['article_html'], unsafe_allow_html=True)
                    
                    st.write("---")
                    st.markdown("##### 📋 คัดลอก HTML Source")
                    st.code(res['article_html'], language="html")
                    
                with tab_facebook:
                    st.info("📋 คัดลอกเพื่อนำไปใช้งานได้ทันที (คลิกปุ่ม Copy ที่มุมขวาบนของกล่องรหัส)")
                    st.markdown(f"**ข้อความโพสต์ประชาสัมพันธ์ ({outputs_map.get('facebook_post', 'Social Post')}):**")
                    st.code(strip_html_tags(res['facebook_post']), language=None)
                    st.write(f"**แฮชแท็กแนะนำ:** {strip_html_tags(res['facebook_hashtags'])}")
                    
                with tab_tiktok:
                    st.info("📋 คัดลอกเพื่อนำไปใช้งานได้ทันที (คลิกปุ่ม Copy ที่มุมขวาบนของกล่องรหัสเพื่อคัดลอกสคริปต์)")
                    st.markdown(f"🔥 **TikTok Hook ดึงดูดสายตา:** *\"{strip_html_tags(res['tiktok_hook'])}\"*")
                    st.markdown(f"**{outputs_map.get('tiktok_script', 'สคริปต์สั้นบทพูดและแนวภาพ TikTok')}:**")
                    st.code(strip_html_tags(res['tiktok_script']), language=None)
                    
                with tab_youtube:
                    st.info("📋 คัดลอกเพื่อนำไปใช้งานได้ทันที (คลิกปุ่ม Copy ที่มุมขวาบนเพื่อคัดลอกสคริปต์)")
                    st.write(f"🎥 **{outputs_map.get('youtube_script', 'YouTube Shorts Title')}:** {strip_html_tags(res['youtube_title'])}")
                    st.write(f"**คำอธิบายและสรุป:** {strip_html_tags(res['youtube_description'])}")
                    st.markdown(f"**{outputs_map.get('youtube_script', 'สคริปต์สำหรับวิดีโอ YouTube Shorts')}:**")
                    st.code(strip_html_tags(res['youtube_shorts_script']), language=None)
                    
                with tab_image:
                    st.info("📋 คัดลอกเพื่อนำไปใช้งานได้ทันที (คลิกปุ่ม Copy มุมขวาเพื่อนำคำสั่งไปส่ง AI วาดภาพ)")
                    st.markdown(f"**{outputs_map.get('image_prompt', 'Featured Image Prompt')}:**")
                    st.code(strip_html_tags(res['featured_image_prompt']), language=None)
                    st.write(f"**Image Style:** {strip_html_tags(res['image_style'])}")
                    st.write(f"**Concept:** {strip_html_tags(res['image_concept'])}")
            else:
                # Empty State (ก่อนลูกค้ากดเจนเนื้อหา)
                st.markdown("""
                <div style='text-align: center; padding: 40px 20px;'>
                    <div style='font-size: 55px; margin-bottom: 20px;'>📦</div>
                    <h3 style='margin-bottom: 15px; color: #1e293b; font-weight: 700; font-size: 1.3em;'>Content Pack ของคุณจะประกอบด้วย</h3>
                    <div style='text-align: left; max-width: 280px; margin: 0 auto 25px auto; color: #475569; font-size: 0.95em; line-height: 1.8; font-weight: 500;'>
                        • 📄 บทความคุณภาพสูง หรือข่าวประชาสัมพันธ์<br/>
                        • 📘 โพสต์สื่อโซเชียลมีเดียหลักสไตล์แบรนด์<br/>
                        • 🎬 สคริปต์สั้นสำหรับวิดีโอ TikTok<br/>
                        • ▶️ รายละเอียดคำบรรยาย / สคริปต์วิดีโอสั้น YouTube<br/>
                        • 🖼️ Prompt วาดรูปภาพประกอบประชาสัมพันธ์
                    </div>
                    <p style='font-weight: 700; color: #007bff; font-size: 1em; margin-top: 15px;'>เมื่อพร้อมแล้ว กรอกข้อมูลด้านซ้ายแล้วกดปุ่ม "✨ สร้าง Content Pack"</p>
                </div>
                """, unsafe_allow_html=True)

else:
    # ----------------------------------------------------
    # STANDARD MODE (Admin Portal - เมนูจัดการหลังบ้านเดิม)
    # ----------------------------------------------------
    # แสดงแบนเนอร์ด้านบนของหน้าเว็บ (Sprint 6)
    st.info("🎁 ทดลองใช้ฟรี 3 Content Packs / หลังจากนั้นเริ่มต้นเพียง 99 บาท ได้ 10 Content Credits (1 Credit = สร้างครบชุด 1 ครั้ง)")

    st.title("🚀 GetExpert AI Content Factory Portal")
    st.markdown("ระบบผลิตชุดโซเชียลคอนเทนต์ครบวงจร (Sprint 5: Client Delivery & AI Content Blueprint Strategy)")

    # 1. User Identification (Sprint 6)
    with st.container(border=True):
        st.markdown("##### 🔑 ระบุตัวตนก่อนใช้งานเพื่อตรวจสอบสิทธิ์เครดิตของคุณ")
        col_em, col_nm = st.columns(2)
        with col_em:
            user_email = st.text_input("อีเมลของคุณ (Email) *", placeholder="example@mail.com", key="std_email_input").strip()
        with col_nm:
            user_name = st.text_input("ชื่อของคุณ (Name)", placeholder="สมชาย รักเรียน", key="std_name_input").strip()

    # ตรวจสอบสิทธิ์เครดิต
    is_eligible = False
    credit_type = "blocked"
    credit_balance = 0
    status_msg = ""

    if user_email:
        from services.credit_service import CreditService
        credit_service = CreditService(sheets_service)
        # ตรวจสอบหรือสร้างผู้ใช้
        credit_service.get_or_create_user(user_email, user_name)
        is_eligible, credit_type, credit_balance, status_msg = credit_service.check_credit_eligibility(user_email)

        # แสดงสถานะเครดิตบนหน้าบ้าน
        if credit_type == "free":
            st.info(f"💡 {status_msg} (คุณใช้สิทธิ์ฟรีไปแล้ว {3 - credit_balance} / 3 Content Packs)")
        elif credit_type == "paid":
            st.success(f"💎 {status_msg} (คุณเหลือเครดิต {credit_balance} Content Packs)")
        elif credit_type == "blocked":
            st.error(f"⚠️ {status_msg}")
    else:
        st.warning("⚠️ กรุณากรอกอีเมลของคุณด้านบนเพื่อตรวจสอบสิทธิ์การใช้งานก่อนเริ่มสร้างคอนเทนต์")

    # 2. Content Type Selector
    st.write("##### 📈 เลือกประเภทงานที่ต้องการสร้างคอนเทนต์")
    selected_content_type = st.radio(
        "ประเภทคอนเทนต์ที่เหมาะสมกับเป้าหมายของคุณ:",
        options=list(blueprints_data.keys()),
        format_func=lambda k: f"{blueprints_data[k]['label']} — {blueprints_data[k]['description']}",
        key="std_content_selector"
    )

    col1, col2 = st.columns([1, 1.2])

    with col1:
        if not user_email:
            st.info("กรุณาระบุอีเมลด้านบนเพื่อเริ่มการกรอกรายละเอียด")
        elif not is_eligible:
            # แสดงหน้าจอ Payment Gate แทนตัวฟอร์ม (Sprint 6)
            with st.container(border=True):
                st.markdown("""
                ### 💳 คุณใช้สิทธิ์ทดลองใช้ฟรีครบ 3 Content Packs แล้ว
                
                หากต้องการสร้างคอนเทนต์ต่อ ซื้อเครดิตเริ่มต้นเพียง **99 บาท** รับ **10 Content Credits**
                
                *(1 Credit = สร้าง Content Pack ครบชุด 1 ครั้ง)*
                
                ---
                
                #### 📌 ช่องทางการชำระเงิน (Manual Payment)
                1. **สแกน QR Code หรือโอนเข้าบัญชี:**
                   - ธนาคารกสิกรไทย: 012-3-45678-9 (บริษัท เก็ทเอ็กซ์เพิร์ท จำกัด)
                2. **ส่งสลิปหลักฐานการชำระเงิน:**
                   - แอด LINE OA: **@GetExpert**
                   - ส่งรูปสลิปให้แอดมินเพื่อเติมเครดิต
                
                *แอดมินจะทำการเติมเครดิตให้คุณทันทีหลังตรวจสอบหลักฐานเรียบร้อยแล้ว*
                """)
        else:
            with st.container(border=True):
                st.subheader("📝 ป้อนรายละเอียดตามบลูปริ้นต์")
            
            with st.form("content_form", clear_on_submit=True):
                blueprint_inputs = {}
                
                # แสดงฟอร์มตามลักษณะยุทธศาสตร์ประเภทที่เลือก (Dynamic Form)
                if selected_content_type == "business":
                    topic = st.text_input("หัวข้อที่ต้องการสร้างคอนเทนต์ *", placeholder="วิธีประหยัดค่าไฟช่วงหน้าร้อน")
                    keyword = st.text_input("คำสำคัญหลัก (Focus Keyword) *", placeholder="ประหยัดค่าไฟ, แอร์บ้าน")
                    st.write("---")
                    st.markdown("**🎯 ข้อมูลแนวทางแบรนด์ (Brand Guidelines)**")
                    blueprint_inputs["business_name"] = st.text_input("ชื่อธุรกิจ / สินค้าของคุณคืออะไร", placeholder="เช่น ร้านจำหน่ายเครื่องปรับอากาศ")
                    blueprint_inputs["target_audience"] = st.text_input("ลูกค้ากลุ่มเป้าหมายคือใคร", placeholder="เช่น เจ้าของบ้านทั่วไป, แม่บ้านพ่อบ้าน")
                    blueprint_inputs["customer_problem"] = st.text_input("ปัญหาหลักของลูกค้าคืออะไร", placeholder="เช่น ค่าไฟฟ้าพุ่งสูงช่วงฤดูร้อน")
                    blueprint_inputs["unique_value"] = st.text_input("จุดเด่นของสินค้า / บริการ", placeholder="เช่น บริการล้างแอร์แถมแผงกันความร้อนฟรี")
                    blueprint_inputs["marketing_goal"] = st.text_input("เป้าหมายการตลาด", placeholder="เช่น เพิ่มยอดจองคิวบริการล้างแอร์ช่วงนี้")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น สุภาพเป็นทางการ, สนุกสนานเป็นกันเอง")
                    blueprint_inputs["cta"] = st.text_input("คำเชิญชวนดำเนินการ (CTA)", placeholder="เช่น จองคิวล้างแอร์ด่วนวันนี้ลดทันที 15%")
                    
                elif selected_content_type == "government":
                    topic = st.text_input("หัวข้อประชาสัมพันธ์ *", placeholder="โครงการตรวจสุขภาพฟรีกองทุนสุขภาพประจำปี")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="ตรวจสุขภาพฟรี, กองทุนสุขภาพ")
                    st.write("---")
                    st.markdown("**🏛 ข้อมูลประชาสัมพันธ์ภาครัฐ (Government Context)**")
                    blueprint_inputs["agency_name"] = st.text_input("ชื่อหน่วยงานราชการของคุณ", placeholder="เช่น อบต. บางรัก")
                    blueprint_inputs["public_target"] = st.text_input("ประชาชนกลุ่มเป้าหมาย", placeholder="เช่น ประชาชนสิทธิหลักประกันสุขภาพในเขต อบต.")
                    blueprint_inputs["project_objective"] = st.text_input("วัตถุประสงค์ของโครงการ", placeholder="เช่น เพื่อการป้องกันโรคและส่งเสริมสุขภาพล่วงหน้า")
                    blueprint_inputs["public_benefit"] = st.text_input("ประโยชน์ที่ประชาชนจะได้รับ", placeholder="เช่น ตรวจสุขภาพเบื้องต้น 10 รายการ ฟรีไม่เสียค่าใช้จ่าย")
                    blueprint_inputs["key_information"] = st.text_input("ข้อมูลสำคัญที่ต้องการแจ้ง", placeholder="เช่น ติดต่อรับบัตรคิวได้ที่ รพ.สต. ใกล้บ้าน หรือ ณ หอประชุมอำเภอ")
                    blueprint_inputs["contact_channel"] = st.text_input("ช่องทางติดต่อ / เข้าร่วม", placeholder="เช่น โทร 02-123-4567 ต่อกองการสาธารณสุข")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น สุภาพ เรียบร้อย น่าเชื่อถือ เข้าใจง่าย")
                    
                elif selected_content_type == "csr":
                    topic = st.text_input("ชื่อโครงการ / แคมเปญ *", placeholder="โครงการปลูกป่าชายเลนคืนความอุดมสมบูรณ์")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="ปลูกป่าชายเลน, รักษ์โลก")
                    st.write("---")
                    st.markdown("**❤️ ข้อมูลโครงการเพื่อสังคม (CSR Impact Context)**")
                    blueprint_inputs["campaign_name"] = st.text_input("ชื่อแคมเปญเพื่อสังคม", placeholder="เช่น โครงการป่าเลนฟื้นใจ")
                    blueprint_inputs["social_problem"] = st.text_input("ปัญหาสังคมที่ต้องการแก้", placeholder="เช่น แนวชายฝั่งถูกกัดเซาะและแหล่งพันธุ์สัตว์น้ำลดลง")
                    blueprint_inputs["affected_group"] = st.text_input("กลุ่มเป้าหมายที่ได้รับผลกระทบ", placeholder="เช่น ชุมชนชาวประมงพื้นบ้านบริเวณชายฝั่ง")
                    blueprint_inputs["campaign_goal"] = st.text_input("เป้าหมายของโครงการ", placeholder="เช่น ปลูกกล้าโกงกางจำนวน 2,000 ต้น")
                    blueprint_inputs["expected_impact"] = st.text_input("ผลลัพธ์ที่คาดหวัง", placeholder="เช่น ชุมชนมีแนวป้องกันภัยธรรมชาติและสัตว์น้ำกลับมาสมบูรณ์")
                    blueprint_inputs["participation_invite"] = st.text_input("สิ่งที่อยากเชิญชวนให้คนมีส่วนร่วม", placeholder="เช่น เชิญชวนอาสาสมัครร่วมลงพื้นที่ปลูกป่าวันเสาร์")
                    blueprint_inputs["organization_name"] = st.text_input("หน่วยงาน / องค์กรเจ้าของโครงการ", placeholder="เช่น บริษัท พลังงานสะอาด จำกัด มหาชน")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น สื่อสารเห็นอกเห็นใจ ชักชวนร่วมมือ มุ่งมั่นพัฒนาสังคม")
                    
                elif selected_content_type == "education":
                    topic = st.text_input("หัวข้อบทเรียน / กิจกรรม *", placeholder="วิธีการทำงานและประโยชน์เบื้องต้นของ AI ในชีวิตการทำงาน")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="เรียนรู้ AI, ประโยชน์ของปัญญาประดิษฐ์")
                    st.write("---")
                    st.markdown("**🎓 ข้อมูลด้านการศึกษา (Educational Context)**")
                    blueprint_inputs["institution_name"] = st.text_input("ชื่อสถาบันการศึกษา / มหาวิทยาลัย", placeholder="เช่น มหาวิทยาลัยเทคโนโลยีการเขียน")
                    blueprint_inputs["learner_group"] = st.text_input("ระดับชั้น / กลุ่มผู้เรียน", placeholder="เช่น ผู้เริ่มต้นสนใจด้านเทคโนโลยี และวัยทำงาน")
                    blueprint_inputs["learning_objective"] = st.text_input("วัตถุประสงค์การเรียนรู้", placeholder="เช่น เพื่อเข้าใจการใช้ Prompt ทุ่นแรงงานประจำวัน")
                    blueprint_inputs["core_knowledge"] = st.text_input("สาระสำคัญที่ต้องการสื่อ", placeholder="เช่น นิยาม AI, การเขียนคำสั่งเบื้องต้น, ตัวอย่างเคสล้างตาราง")
                    blueprint_inputs["expected_outcome"] = st.text_input("ผลลัพธ์ที่คาดหวังจากผู้เรียน", placeholder="เช่น ผู้เรียนสามารถเอาเครื่องมือ AI ไปประยุกต์ใช้ลดเวลาทำงาน")
                    blueprint_inputs["content_format"] = st.text_input("รูปแบบเนื้อหาที่ต้องการ", placeholder="เช่น สรุปเนื้อหาบทความแบ่งเป็น 3 หมวดการเรียนรู้")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น เข้าใจง่าย มีเหตุและผลวิชาการ ปรับใช้อบรมได้จริง")
                    
                elif selected_content_type == "event":
                    topic = st.text_input("ชื่องาน / กิจกรรม *", placeholder="งานมหกรรมรวมพลังครีเอเตอร์และอินฟลูเอนเซอร์แห่งปี")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="มหกรรมครีเอเตอร์, Creator Expo")
                    st.write("---")
                    st.markdown("**🎉 ข้อมูลการประชาสัมพันธ์กิจกรรม (Event Context)**")
                    blueprint_inputs["event_name"] = st.text_input("ชื่อกิจกรรมประชาสัมพันธ์", placeholder="เช่น งาน Creator Festival 2027")
                    blueprint_inputs["organizer_name"] = st.text_input("หน่วยงานหรือผู้จัด", placeholder="เช่น ชมรมมีเดียสร้างสรรค์")
                    blueprint_inputs["event_objective"] = st.text_input("วัตถุประสงค์ของงาน", placeholder="เช่น เพื่อรวมตัวครีเอเตอร์มาแบ่งปันแนวทางและพบปะแฟนคลับ")
                    blueprint_inputs["date_time_location"] = st.text_input("วัน เวลา สถานที่จัดงาน", placeholder="เช่น วันที่ 18-19 กันยายน 2570 ณ รอยัลพารากอนฮอลล์ ชั้น 5")
                    blueprint_inputs["event_highlights"] = st.text_input("จุดเด่นของงาน", placeholder="เช่น เวทีพูดคุยแลกเปลี่ยนประสบการณ์ และลานเปิดตัวช่องดัง")
                    blueprint_inputs["attendee_benefits"] = st.text_input("สิ่งที่ผู้เข้าร่วมจะได้รับ", placeholder="เช่น การแลกเปลี่ยนคำแนะนำกับคีย์แบรนด์ สิทธิ์เข้าลุ้นรางวัล")
                    blueprint_inputs["registration_channel"] = st.text_input("ช่องทางลงทะเบียน / ติดต่อ", placeholder="เช่น ลงทะเบียนผ่านแอป EventPop หรือเว็บไซต์งาน")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น มีความกระตือรือร้น ทันสมัย สุภาพและตื่นตาตื่นใจ")
                    
                elif selected_content_type == "personal_brand":
                    topic = st.text_input("หัวข้อที่ต้องการสื่อสาร *", placeholder="เทคนิคการจัดการเวลาแบบ 80/20 ที่ผมใช้ทำงานแค่ 4 ชั่วโมงต่อวัน")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="เทคนิคจัดเวลา, กฎ 80/20")
                    st.write("---")
                    st.markdown("**👤 ข้อมูลแบรนด์บุคคล (Personal Branding)**")
                    blueprint_inputs["expert_niche"] = st.text_input("ความเชี่ยวชาญ / กลุ่มวิชาชีพของคุณ", placeholder="เช่น โค้ชพัฒนาทักษะและความก้าวหน้าในอาชีพ")
                    blueprint_inputs["target_followers"] = st.text_input("ผู้ติดตามหรือกลุ่มเป้าหมายคือใคร", placeholder="เช่น ฟรีแลนซ์และพนักงานออฟฟิศที่เผชิญภาวะงานทับตัว")
                    blueprint_inputs["experience_story"] = st.text_input("ประสบการณ์หรือมุมมองสำคัญที่เล่า", placeholder="เช่น เคยล้มป่วยจากสัญญานทำงานหามรุ่งหามค่ำจนเปลี่ยนชีวิต")
                    blueprint_inputs["core_identity"] = st.text_input("ภาพลักษณ์ที่ต้องการสร้าง", placeholder="เช่น ผู้ให้คำปรึกษาที่ให้ผลลัพธ์ที่เป็นความจริง สไตล์จริงใจตรงไปตรงมา")
                    blueprint_inputs["key_takeaway"] = st.text_input("ข้อความหลักที่อยากให้คนจดจำ", placeholder="เช่น การปัดปฏิเสธงานไม่สำคัญคือทักษะการเพิ่มผลิตภาพที่แท้จริง")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น เล่าเรื่องผ่านตัวคุณ เป็นกันเองจริงใจ มีความสุภาพแต่น่าฟัง")
                    blueprint_inputs["cta"] = st.text_input("คำเชิญชวนดำเนินการ (CTA)", placeholder="เช่น กดแชร์หากคุณคิดเหมือนกัน หรือทักเรามาใต้คอมเมนต์เพื่อแลกไอเดีย")
                submitted = st.form_submit_button("ส่งคำขอเขียนและแพ็คคอนเทนต์ (Add to Queue)", disabled=st.session_state.get('is_processing', False))
                
                if submitted:
                    if not topic or not keyword:
                        st.error("กรุณากรอกหัวข้อและคำสำคัญคีย์หลัก (มีเครื่องหมาย *)")
                    elif st.session_state.get('is_processing', False):
                        st.warning("ระบบกำลังประมวลผลงานชิ้นก่อนหน้า กรุณารอสักครู่...")
                    elif not user_email:
                        st.error("กรุณากรอกอีเมลของคุณก่อนเริ่มสร้างคอนเทนต์")
                    elif not is_eligible:
                        st.error("โควตาเครดิตไม่เพียงพอ กรุณาติดต่อชำระเงินซื้อเครดิต")
                    else:
                        st.session_state['is_processing'] = True
                        try:
                            # บันทึกข้อมูลแผนงานบลูปริ้นต์ลงชีตในระบบคิวงานรอรันรายวัน
                            blueprint_label = blueprints_data[selected_content_type]["label"]
                            blueprint_inputs_json = json.dumps(blueprint_inputs, ensure_ascii=False)
                            output_types_list = ", ".join(blueprints_data[selected_content_type]["outputs"].keys())
                            
                            target_audience = blueprint_inputs.get("target_audience", blueprint_inputs.get("public_target", blueprint_inputs.get("target_followers", "")))
                            business_type = blueprint_inputs.get("business_name", blueprint_inputs.get("agency_name", blueprint_inputs.get("organization_name", blueprint_inputs.get("institution_name", ""))))
                            content_goal = blueprint_inputs.get("marketing_goal", blueprint_inputs.get("project_objective", blueprint_inputs.get("campaign_goal", blueprint_inputs.get("learning_objective", ""))))
                            tone = blueprint_inputs.get("tone", "")
                            
                            row_idx = sheets_service.add_new_row(
                                topic=topic,
                                keyword=keyword,
                                target_audience=target_audience,
                                business_type=business_type,
                                content_goal=content_goal,
                                tone=tone,
                                content_type=selected_content_type,
                                blueprint_label=blueprint_label,
                                blueprint_inputs_json=blueprint_inputs_json,
                                output_types_list=output_types_list,
                                user_email=user_email
                            )
                            st.session_state['last_row_idx'] = row_idx
                            st.success(f"ส่งคำขอเข้าสู่คิวงานเรียบร้อยแล้ว! (พิกัดแถวที่ {row_idx})")
                            st.session_state['is_processing'] = False
                            st.rerun()
                        except Exception as error:
                            st.session_state['is_processing'] = False
                            st.error(f"เกิดปัญหาในการบันทึกลงชีต: {error}")

    with col2:
        with st.container(border=True):
            st.subheader("🔍 ตรวจเช็คสถานะและรายละเอียด Content Pack")
            
            if 'last_row_idx' in st.session_state:
                row_idx = st.session_state['last_row_idx']
                
                try:
                    row_data = sheets_service.get_row_by_index(row_idx)
                    
                    st.info(f"รายการล่าสุด: **{row_data.topic}** (คีย์เวิร์ด: {row_data.keyword})")
                    
                    # การเลือกสไตล์ Badge ตามสถานะ
                    status_lower = row_data.status.strip().lower()
                    badge_class = "status-waiting"
                    if status_lower == "processing":
                        badge_class = "status-processing"
                    elif status_lower == "drafted":
                        badge_class = "status-drafted"
                    elif status_lower == "failed":
                        badge_class = "status-failed"
                        
                    st.markdown(
                        f"สถานะปัจจุบัน: <span class='status-badge {badge_class}'>{row_data.status}</span>", 
                        unsafe_allow_html=True
                    )
                    
                    if status_lower == "drafted":
                        st.success("🎉 ระบบผลิตชุด Content Pack สำเร็จเสร็จสมบูรณ์เรียบร้อยแล้ว!")
                        
                        # ค้นหาค่า Blueprint จาก row_data.content_type เพื่อคำนวณป้ายชื่อ Tab แบบไดนามิก
                        row_content_type = getattr(row_data, 'content_type', 'business')
                        row_blueprint = BlueprintService.get_blueprint(row_content_type)
                        row_outputs = row_blueprint.get("outputs", {})
                        
                        st.info(f"📂 AI Content Blueprint ที่ใช้: **{row_blueprint.get('label', 'ธุรกิจ')}**\n\nบทบาท: *{row_blueprint.get('prompt_strategy', {}).get('role', '')}*")
                        
                        tab_labels = [
                            row_outputs.get("seo_article", "📰 Blogger & SEO"),
                            row_outputs.get("facebook_post", "📘 Facebook Post"),
                            row_outputs.get("tiktok_script", "🎵 TikTok Script"),
                            row_outputs.get("youtube_script", "🔴 YouTube Shorts"),
                            row_outputs.get("image_prompt", "🎨 Image Prompts")
                        ]
                        
                        tab_blogger, tab_facebook, tab_tiktok, tab_youtube, tab_image = st.tabs(tab_labels)
                        
                        with tab_blogger:
                            st.markdown(f"🔗 **Blogger Draft URL:** [คลิกเปิดร่างบทความใน Blogger]({row_data.blogger_url})")
                            st.write(f"**Blogger Post ID:** `{row_data.blogger_post_id}`")
                            st.write(f"**SEO Title:** {strip_html_tags(row_data.seo_title)}")
                            st.write(f"**Meta Description:** {strip_html_tags(row_data.meta_description)}")
                            st.write(f"**Slug Recommendation:** `{strip_html_tags(row_data.slug_suggestion)}`")
                            st.write(f"**Focus Keyword:** {strip_html_tags(row_data.focus_keyword)}")
                            st.write(f"**Related Keywords:** {strip_html_tags(row_data.related_keywords)}")
                            st.write(f"**Content Summary:** {strip_html_tags(row_data.content_summary)}")
                            
                        with tab_facebook:
                            st.markdown(f"**โพสต์แนะนำประชาสัมพันธ์ ({row_outputs.get('facebook_post', 'Social Post')}):**")
                            st.code(strip_html_tags(row_data.facebook_post), language=None)
                            st.write(f"**แนะนำแฮชแท็ก:** {strip_html_tags(row_data.facebook_hashtags)}")
                            
                        with tab_tiktok:
                            st.markdown(f"🔥 **TikTok Hook (3 วินาทีแรก):** *\"{strip_html_tags(row_data.tiktok_hook)}\"*")
                            st.markdown(f"**{row_outputs.get('tiktok_script', 'สคริปต์สั้นบทพูดและแนวภาพ TikTok')}:**")
                            st.code(strip_html_tags(row_data.tiktok_script), language=None)
                            
                        with tab_youtube:
                            st.write(f"🎥 **{row_outputs.get('youtube_script', 'YouTube Shorts Title')}:** {strip_html_tags(row_data.youtube_title)}")
                            st.write(f"**คำอธิบายสรุปข่าว:** {strip_html_tags(row_data.youtube_description)}")
                            st.markdown(f"**{row_outputs.get('youtube_script', 'สคริปต์วิดีโอ YouTube Shorts')}:**")
                            st.code(strip_html_tags(row_data.youtube_shorts_script), language=None)
                            
                        with tab_image:
                            st.markdown(f"**{row_outputs.get('image_prompt', 'Featured Image Prompt')}:**")
                            st.code(strip_html_tags(row_data.featured_image_prompt), language=None)
                            st.write(f"**Image Style:** {strip_html_tags(row_data.image_style)}")
                            st.write(f"**Image Concept:** {strip_html_tags(row_data.image_concept)}")
                            
                    elif status_lower == "failed":
                        st.error(f"❌ การทำงานขัดข้องหลังพยายาม Retry ครบกำหนด: {row_data.last_error}")
                    else:
                        st.warning("⏳ รอประมวลผล (กรุณากรอกและสั่งรัน Engine main.py หลังบ้านเพื่อรับบทความ)")
                        
                    if st.button("🔄 โหลดรีเฟรชสถานะแถวล่าสุด"):
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"ไม่สามารถดึงข้อมูลสำหรับแถวที่ {row_idx} ได้: {e}")
            else:
                st.write("ยังไม่มีการส่งหัวข้อคำขอใหม่ในเซสชั่นนี้")

    st.markdown("---")

    # แดชบอร์ดสรุปตารางคิวงานทั้งหมด
    st.subheader("📋 ตารางประมวลผลคิวงานผลิต Content Pack ทั้งหมด")

    if st.button("🔄 โหลดรีเฟรชตารางข้อมูล"):
        st.rerun()

    try:
        all_rows = sheets_service.read_all_rows()
        if all_rows:
            # แปลงข้อมูลวัตถุ Pydantic เข้าสู่รูปแบบตารางเพื่อแสดงผลใน Streamlit
            table_data = []
            for row in reversed(all_rows): # กลับลำดับเพื่อให้แถวใหม่สุดอยู่บนสุด
                # ค้นหาป้ายประเภทบลูปริ้นต์
                row_type = getattr(row, 'content_type', 'business')
                bp_info = blueprints_data.get(row_type, blueprints_data["business"])
                
                table_data.append({
                    "ID": row.id,
                    "ประเภทคอนเทนต์": bp_info["label"],
                    "Topic": row.topic,
                    "Keyword": row.keyword,
                    "Status": row.status,
                    "SEO Title": row.seo_title,
                    "Blogger URL": row.blogger_url,
                    "Retry Count": row.retry_count,
                    "Last Error": row.last_error,
                    "Updated At": row.updated_at
                })
            st.dataframe(
                table_data,
                column_config={
                    "Blogger URL": st.column_config.LinkColumn("Blogger URL Link"),
                },
                use_container_width=True
            )
        else:
            st.info("ไม่มีรายการข้อมูลประวัติการทำงานในแผ่นชีต")
    except Exception as e:
        st.error(f"ไม่สามารถโหลดสรุปข้อมูลตารางคิวงานได้: {e}")
