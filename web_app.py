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
    /* Optimize touch scrolling for Streamlit tabs on mobile */
    div[data-testid="stTabBar"] {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    div[data-testid="stHorizontalBlock"] {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
</style>
""", unsafe_allow_html=True)

# (ฟังก์ชัน strip_html_tags ได้รับการอิมพอร์ตมาจาก utils.sanitize เรียบร้อยแล้ว)

# เริ่มต้นเรียกเซอร์วิส Sheets
@st.cache_resource
def get_sheets_service():
    return SheetsService()

sheets_service = None
try:
    sheets_service = get_sheets_service()
except Exception as e:
    logging.error(f"ไม่สามารถเชื่อมต่อ Google Sheets API ได้: {e}")

@st.cache_resource
def get_credit_service():
    from services.credit_service import CreditService
    return CreditService(sheets_service)

def show_payment_gate():
    """
    แสดงหน้าจอ Payment Gate เมื่อผู้ใช้งานใช้สิทธิ์เครดิตหมด (Sprint 6)
    """
    st.markdown("""
    ### 💳 คุณใช้สิทธิ์ทดลองใช้ฟรีครบ 3 Content Packs แล้ว
    
    หากต้องการสร้างคอนเทนต์ต่อ
    ซื้อเครดิตเริ่มต้นเพียง **99 บาท**
    รับ **10 Content Credits**
    
    *(1 Credit = สร้าง Content Pack ครบชุด 1 ครั้ง)*
    
    ---
    
    #### 📦 แพ็กเกจที่ให้บริการ:
    - **แพ็กเริ่มต้น 99 บาท** = รับ 10 Content Credits
    """)
    
    from pathlib import Path
    qr_path = Path("assets/payment_qr.png")
    if qr_path.exists():
        st.image(str(qr_path), caption="สแกนเพื่อชำระเงิน 99 บาท", width=320)
    else:
        st.warning("⚠️ กรุณาเพิ่มไฟล์ QR Code ที่ assets/payment_qr.png")
        
    st.markdown("""
    #### 📌 วิธีชำระเงิน:
    1. สแกน QR Code ด้านบนเพื่อชำระเงิน
    2. หลังโอนเงินแล้ว กรุณาส่งสลิปมาที่ LINE OA: **@774dfect** (หรือกดลิงก์ [https://lin.ee/TZgX4CD](https://lin.ee/TZgX4CD))
    3. แจ้ง Email ที่ใช้ในระบบ
    4. Admin จะตรวจสอบและเติมเครดิตให้ในระบบ
    """)

    line_oa_url = "https://lin.ee/TZgX4CD"
    
    st.markdown(
        f"""
        <a href="{line_oa_url}" target="_self" style="
            display:block;
            text-align:center;
            background:#06C755;
            color:white;
            padding:14px 18px;
            border-radius:10px;
            font-size:18px;
            font-weight:700;
            text-decoration:none;
            margin:12px 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        ">
            💬 เปิด LINE OA เพื่อส่งสลิป
        </a>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"[เปิด LINE OA สำรอง]({line_oa_url})")

    st.markdown(f"""
    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-top: 10px; margin-bottom: 10px;">
        <span style="font-size: 13px; color: #475569;">
            💡 <b>คำแนะนำเพิ่มเติม:</b> หากแตะปุ่มด้านบนแล้วแอป LINE ไม่เปิดทำงานอัตโนมัติ ให้คัดลอกลิงก์นี้ไปวางในเบราว์เซอร์เพื่อแชทได้ทันที:
            <br>
            <code style="background-color: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 14px;">{line_oa_url}</code>
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ---

    📢 **หลังชำระเงิน กรุณาส่งสลิปพร้อมแจ้ง Email ที่ใช้ในระบบ ทาง LINE OA เพื่อให้ Admin เติมเครดิตให้ถูกบัญชี**

    *ช่องทางติดต่อ:*
    - LINE OA: **@774dfect**
    - ลิงก์ติดต่อ: [https://lin.ee/TZgX4CD](https://lin.ee/TZgX4CD)
    """)

def show_history_row_details(row_data, key_prefix=""):
    """
    แสดงรายละเอียดผลลัพธ์ของ SheetRow ย้อนหลัง (ใช้ใน Card UI ของ My Content History - Sprint 6.1)
    """
    status_lower = row_data.status.strip().lower()
    
    if status_lower == "drafted":
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
        
        tab_blogger, tab_facebook, tab_tiktok, tab_youtube, tab_image = st.tabs(tab_labels, key=f"tabs_{key_prefix}")
        
        with tab_blogger:
            st.markdown(f"🔗 **Blogger Draft URL:** [คลิกเปิดร่างบทความใน Blogger]({row_data.blogger_url})")
            st.write(f"**Blogger Post ID:** `{row_data.blogger_post_id}`")
            st.write(f"**SEO Title:** {strip_html_tags(row_data.seo_title)}")
            st.write(f"**Meta Description:** {strip_html_tags(row_data.meta_description)}")
            st.write(f"**Slug Recommendation:** `{strip_html_tags(row_data.slug_suggestion)}`")
            st.write(f"**Focus Keyword:** {strip_html_tags(row_data.focus_keyword)}")
            st.write(f"**Related Keywords:** {strip_html_tags(row_data.related_keywords)}")
            st.markdown("**บทความฉบับเต็ม / ข้อมูลสรุป:**")
            st.code(strip_html_tags(row_data.content_summary), language=None)
            
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

def show_user_history_section(user_email, key_suffix):
    """
    แสดงส่วนประวัติคอนเทนต์ส่วนตัวของผู้ใช้งาน (Sprint 6.1)
    """
    show_history_key = f"show_history_{key_suffix}"
    history_rows_key = f"history_rows_{key_suffix}"
    
    if show_history_key not in st.session_state:
        st.session_state[show_history_key] = False
    if history_rows_key not in st.session_state:
        st.session_state[history_rows_key] = []
        
    st.write("")
    
    col_hist_btn1, col_hist_btn2 = st.columns([1.5, 3])
    with col_hist_btn1:
        if st.button("📚 ดูคอนเทนต์ที่เคยสร้าง", key=f"load_history_btn_{key_suffix}"):
            with st.spinner("กำลังดึงประวัติคอนเทนต์จากฐานข้อมูล..."):
                try:
                    all_rows = sheets_service.read_all_rows()
                    user_rows = [r for r in all_rows if r.user_email.strip().lower() == user_email.strip().lower()]
                    st.session_state[history_rows_key] = user_rows
                    st.session_state[show_history_key] = True
                    st.success("โหลดประวัติเสร็จสิ้น!")
                except Exception as e:
                    st.error(f"ไม่สามารถโหลดประวัติได้ชั่วคราว: {e}")
                    
    with col_hist_btn2:
        if st.session_state[show_history_key]:
            if st.button("❌ ซ่อนประวัติคอนเทนต์", key=f"hide_history_btn_{key_suffix}"):
                st.session_state[show_history_key] = False
                st.rerun()
                
    if st.session_state[show_history_key]:
        user_rows = st.session_state[history_rows_key]
        st.markdown("### 📚 ประวัติคอนเทนต์ที่เคยสร้าง")
        
        if not user_rows:
            st.info("ยังไม่มีคอนเทนต์ที่เคยสร้างด้วย Email นี้")
        else:
            st.info("💡 สามารถกดปุ่มคัดลอก (Copy) ที่มุมบนขวาของกล่องข้อความผลลัพธ์ในรายละเอียดได้ทันที")
            for idx, row in enumerate(reversed(user_rows)):
                with st.container(border=True):
                    st.markdown(f"#### 📝 หัวข้อ: {row.topic}")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.write(f"📅 **วันที่สร้าง:** {row.processed_at if row.processed_at else (row.created_at if row.created_at else 'ไม่ระบุ')}")
                    with c2:
                        st.write(f"📂 **บลูปริ้นต์:** {row.blueprint_label if row.blueprint_label else row.content_type}")
                    with c3:
                        status_lower = row.status.strip().lower()
                        if status_lower == "drafted":
                            st.markdown("สถานะ: <span class='status-badge status-drafted'>สร้างสำเร็จ</span>", unsafe_allow_html=True)
                        elif status_lower == "processing":
                            st.markdown("สถานะ: <span class='status-badge status-processing'>กำลังแต่งเนื้อหา...</span>", unsafe_allow_html=True)
                        elif status_lower == "failed":
                            st.markdown("สถานะ: <span class='status-badge status-failed'>เกิดข้อผิดพลาด</span>", unsafe_allow_html=True)
                        else:
                            st.markdown("สถานะ: <span class='status-badge status-waiting'>รอคิวรัน</span>", unsafe_allow_html=True)
                            
                    # ปุ่มแสดงรายละเอียด
                    with st.expander("🔍 ดูรายละเอียดผลลัพธ์ Content Pack"):
                        show_history_row_details(row, key_prefix=f"{key_suffix}_{row.row_idx}_{idx}")

def show_user_referral_partner_section(user_email, key_suffix):
    """
    แสดงส่วนแดชบอร์ด Referral Partner ของผู้ใช้นั้นๆ หากได้รับอนุมัติสิทธิ์แล้ว (Sprint 7)
    """
    user_obj = st.session_state.get(f"{key_suffix}_user_credit_obj")
    if user_obj and user_obj.is_referral_partner:
        st.write("")
        with st.container(border=True):
            st.markdown("### 🤝 แดชบอร์ดผู้แนะนำ (Referral Partner Dashboard)")
            st.success(f"คุณเป็น Referral Partner สถานะ: **{user_obj.referral_status}**")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**รหัสแนะนำของคุณ:** `{user_obj.referral_code}`")
                st.markdown(f"**วันที่เข้าร่วม:** {user_obj.referral_started_at}")
            with c2:
                st.markdown(f"**ลิงก์แนะนำของคุณ:** `{user_obj.referral_link}`")
                st.markdown(f"**ค่าสิทธิ์แนะนำ:** {user_obj.referral_package_paid} บาท")
                
            # แสดงประวัติการแนะนำที่ได้รับคอมมิชชั่น
            if st.button("📊 โหลดข้อมูลคอมมิชชั่นแนะนำของฉัน", key=f"load_partner_comm_btn_{key_suffix}"):
                with st.spinner("กำลังดึงข้อมูลคอมมิชชั่น..."):
                    try:
                        all_logs = sheets_service.service.spreadsheets().values().get(
                            spreadsheetId=sheets_service.spreadsheet_id, range="Referral Logs!A:I").execute().get('values', [])
                        
                        partner_logs = []
                        total_earned = 0.0
                        if all_logs and len(all_logs) > 1:
                            for row in all_logs[1:]:
                                if len(row) > 1 and row[1].strip().upper() == user_obj.referral_code.strip().upper():
                                    padded_row = row + [''] * (9 - len(row))
                                    partner_logs.append(padded_row)
                                    try:
                                        total_earned += float(padded_row[6])
                                    except ValueError:
                                        pass
                                        
                        st.markdown(f"💰 **รายได้สะสมทั้งหมด (คอมมิชชั่นชั้นเดียว):** {total_earned} บาท")
                        if partner_logs:
                            import pandas as pd
                            df = pd.DataFrame(partner_logs, columns=[
                                "วันที่", "รหัสแนะนำ", "อีเมลผู้แนะนำ", "อีเมลผู้ใช้ใหม่", 
                                "แพ็กเกจ", "ยอดเงินชำระ", "ค่าแนะนำที่ได้รับ", "สถานะ", "หมายเหตุ"
                            ])
                            st.dataframe(df)
                        else:
                            st.info("ยังไม่มีข้อมูลค่าคอมมิชชั่นจากผู้ที่สมัครผ่านลิงก์ของคุณ")
                    except Exception as e:
                        st.error(f"ไม่สามารถโหลดข้อมูลคอมมิชชั่นได้: {e}")

def show_admin_referral_manager():
    """
    หน้าจอผู้ดูแลระบบสำหรับเปิดสิทธิ์ Referral Partner และบันทึกยอดเงิน/เครดิต (Sprint 7)
    """
    st.info("💡 ส่วนนี้สำหรับแอดมิน: ใช้สำหรับค้นหาผู้ใช้ เปิดสิทธิ์ Referral Partner และบันทึกยอดเติมเครดิตพร้อมคำนวณค่าคอมมิชชั่น")
    
    admin_search_email = st.text_input("ค้นหาอีเมลผู้ใช้งาน *", placeholder="user@example.com", key="admin_search_email").strip()
    
    if admin_search_email:
        try:
            result = sheets_service.get_user_by_email(admin_search_email)
            if not result:
                st.warning("⚠️ ไม่พบผู้ใช้งานรายนี้ในระบบ")
            else:
                user, row_idx = result
                st.markdown(f"#### 👤 ข้อมูลผู้ใช้: {user.user_name} ({user.user_email})")
                
                # แสดงสถานะเดิม
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"💳 **สิทธิ์ทดลองใช้ฟรีที่ใช้ไป:** {user.free_credits_used} / 3")
                with c2:
                    st.write(f"💎 **เครดิตจ่ายเงินคงเหลือ:** {user.paid_credits_balance}")
                with c3:
                    st.write(f"🤝 **เป็น Referral Partner:** {'เป็นแล้ว ✅' if user.is_referral_partner else 'ยังไม่เป็น ❌'}")
                    
                st.write(f"🔗 **ผู้แนะนำ (Referred By):** `{user.referred_by if user.referred_by else 'ไม่มี'}`")
                
                st.write("---")
                
                # 1. การจัดการ Referral Partner
                st.markdown("##### 🤝 จัดการสิทธิ์ Referral Partner")
                if not user.is_referral_partner:
                    st.write("ผู้ใช้รายนี้ยังไม่ได้เป็นพาร์ทเนอร์แนะนำสินค้า")
                    
                    # ให้กรอก Referral Code เอง หรือระบบสุ่มให้
                    suggested_code = user.user_email.split('@')[0][:8].upper() + "001"
                    ref_code_input = st.text_input("กำหนด Referral Code (ต้องไม่ซ้ำและห้ามใช้ Email ตรงๆ)", value=suggested_code).strip().upper()
                    
                    if st.button("🌟 เปิดสิทธิ์ Referral Partner", key="activate_partner_btn"):
                        if not ref_code_input:
                            st.error("กรุณาระบุ Referral Code")
                        elif ref_code_input == user.user_email.upper():
                            st.error("ห้ามใช้ Email ตรงๆ เป็น Referral Code")
                        else:
                            with st.spinner("กำลังตรวจสอบและเปิดสิทธิ์..."):
                                # ตรวจสอบความซ้ำซ้อนของโค้ด
                                existing_ref = sheets_service.get_user_by_referral_code(ref_code_input)
                                if existing_ref:
                                    st.error(f"⚠️ รหัสแนะนำ '{ref_code_input}' นี้ถูกใช้งานแล้วโดยผู้ใช้อื่น! กรุณาเปลี่ยนใหม่")
                                else:
                                    import datetime as dt
                                    now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    # อัปเดตข้อมูลผู้ใช้
                                    user.is_referral_partner = True
                                    user.referral_code = ref_code_input
                                    # สร้าง Referral Link อ้างอิงตามโดเมน Streamlit Cloud
                                    user.referral_link = f"https://getexpert-ai-content-factory1.streamlit.app/?ref={ref_code_input}"
                                    user.referral_started_at = now_str
                                    user.referral_package_paid = 149.0
                                    user.referral_status = "Active"
                                    user.updated_at = now_str
                                    
                                    sheets_service.save_user_credit(user, row_idx)
                                    st.success(f"🎉 เปิดสิทธิ์ Referral Partner สำเร็จ! รหัสแนะนำ: {ref_code_input}")
                                    st.rerun()
                else:
                    st.success(f"ผู้ใช้รายนี้เป็น Referral Partner แล้ว! รหัส: `{user.referral_code}`")
                    st.write(f"🔗 **Referral Link:** `{user.referral_link}`")
                    st.write(f"💰 **ยอดชำระค่าสิทธิ์:** {user.referral_package_paid} บาท")
                    
                    if st.button("🚫 ยกเลิกสิทธิ์ Referral Partner", key="deactivate_partner_btn"):
                        with st.spinner("กำลังยกเลิกสิทธิ์..."):
                            user.is_referral_partner = False
                            user.referral_status = "Inactive"
                            user.updated_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            sheets_service.save_user_credit(user, row_idx)
                            st.success("ยกเลิกสิทธิ์พาร์ทเนอร์แนะนำสำเร็จ")
                            st.rerun()
                            
                st.write("---")
                
                # 2. การบันทึกรับเงินเติมเครดิตและบันทึกค่าแนะนำ
                st.markdown("##### 💳 บันทึกการเติมเครดิตและคำนวณค่าคอมมิชชั่น")
                package_options = {
                    "แพ็กเริ่มต้น 99 บาท (10 Credits)": {"price": 99.00, "credits": 10},
                    "Referral Starter 149 บาท (10 Credits + สิทธิ์แนะนำ)": {"price": 149.00, "credits": 10}
                }
                selected_pkg_name = st.selectbox("เลือกแพ็กเกจที่เติม", options=list(package_options.keys()))
                
                if st.button("💾 บันทึกการเติมเครดิตและสลิป", key="record_payment_credits_btn"):
                    with st.spinner("กำลังเติมเครดิตและบันทึกประวัติ..."):
                        pkg_info = package_options[selected_pkg_name]
                        price = pkg_info["price"]
                        credits_to_add = pkg_info["credits"]
                        
                        import datetime as dt
                        now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 1. ปรับปรุงเครดิตผู้ใช้งาน
                        user.paid_credits_balance += credits_to_add
                        user.payment_status = "Active Customer"
                        user.updated_at = now_str
                        sheets_service.save_user_credit(user, row_idx)
                        
                        # 2. บันทึกใน Payments Sheet
                        from models.credit_models import PaymentRecord
                        payment = PaymentRecord(
                            payment_date=now_str,
                            user_email=user.user_email,
                            package_name=selected_pkg_name,
                            amount=price,
                            credits_added=credits_to_add,
                            payment_method="QR Code",
                            slip_status="Approved",
                            approved_by="Admin",
                            approved_at=now_str,
                            note="เติมเงินผ่านหน้าแอดมินพาร์ทเนอร์"
                        )
                        sheets_service.add_payment_record(payment)
                        
                        # 3. คำนวณคอมมิชชั่น 20 บาท หากผู้ใช้นี้มีผู้แนะนำ (Referred By)
                        # จ่ายเฉพาะเมื่อลูกค้าชำระเงินแพ็กเกจปกติ (คอมมิชชั่นชั้นเดียว)
                        commission_logged = ""
                        if user.referred_by:
                            referrer_result = sheets_service.get_user_by_referral_code(user.referred_by)
                            if referrer_result:
                                referrer_user, _ = referrer_result
                                if referrer_user.is_referral_partner and referrer_user.referral_status == "Active":
                                    # บันทึก Referral Log
                                    commission_amount = 20.00
                                    sheets_service.add_referral_log([
                                        now_str,
                                        referrer_user.referral_code,
                                        referrer_user.user_email,
                                        user.user_email,
                                        selected_pkg_name,
                                        price,
                                        commission_amount,
                                        "Pending Paid",
                                        "ค่าแนะนำแนะนำเพื่อนสมัครใช้บริการ"
                                    ])
                                    commission_logged = f" พร้อมบันทึกคอมมิชชั่นแนะนำเพื่อน 20 บาท ให้กับรหัสพาร์ทเนอร์ {referrer_user.referral_code} ({referrer_user.user_email}) สำเร็จ!"
                        
                        st.success(f"เติมเครดิตสำเร็จ! เพิ่มยอด {credits_to_add} Credits ให้ผู้ใช้ {user.user_email}{commission_logged}")
                        st.rerun()
                        
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")

# โหลดข้อมูล Blueprint ทั้งหมด
blueprints_data = BlueprintService.get_all_blueprints()

# ----------------------------------------------------
# Safe Query Parameter Capture (Sprint 7.1)
# ----------------------------------------------------
ENABLE_REFERRAL_QUERY_CAPTURE = True

def sanitize_referral_code(code: str) -> str:
    """
    ทำความสะอาดรหัสแนะนำให้รับเฉพาะ A-Z, 0-9, _, - และมีความยาวไม่เกิน 20 ตัวอักษร
    """
    if not code:
        return ""
    import re
    cleaned = re.sub(r'[^A-Za-z0-9_\-]', '', code)
    return cleaned[:20].upper()

is_demo = False
try:
    # ดึงค่า demo mode อย่างปลอดภัย
    query_params_demo = getattr(st, "query_params", {})
    raw_demo = "false"
    if query_params_demo:
        if hasattr(query_params_demo, "get"):
            raw_demo = query_params_demo.get("demo", "false")
        elif isinstance(query_params_demo, dict):
            raw_demo = query_params_demo.get("demo", "false")
            
    if isinstance(raw_demo, list):
        raw_demo = raw_demo[0] if raw_demo else "false"
    elif not isinstance(raw_demo, str):
        raw_demo = str(raw_demo) if raw_demo is not None else "false"
        
    is_demo = raw_demo.lower() == "true"
except BaseException as e:
    import logging
    logging.warning(f"ล้มเหลวในการตรวจสอบโหมดทดสอบ (demo mode query param): {e}")

if ENABLE_REFERRAL_QUERY_CAPTURE:
    try:
        query_params_ref = getattr(st, "query_params", {})
        if query_params_ref:
            raw_ref = ""
            if hasattr(query_params_ref, "get"):
                raw_ref = query_params_ref.get("ref", "")
            elif isinstance(query_params_ref, dict):
                raw_ref = query_params_ref.get("ref", "")
                
            if isinstance(raw_ref, list):
                raw_ref = raw_ref[0] if raw_ref else ""
            elif not isinstance(raw_ref, str):
                raw_ref = str(raw_ref) if raw_ref is not None else ""
                
            referral_code = sanitize_referral_code(raw_ref)
            if referral_code:
                st.session_state["referred_by_code"] = referral_code
    except BaseException as e:
        import logging
        logging.warning(f"Referral query capture disabled due to error: {e}", exc_info=True)

if is_demo:
    # ----------------------------------------------------
    # DEMO MODE (Client Trial - คลีนและรันตอบสนองทันที - UX Sprint 1 / Sprint 5)
    # ----------------------------------------------------
    # แสดงแบนเนอร์ด้านบนของหน้าเว็บ (Sprint 6)
    st.info("🎁 ทดลองใช้ฟรี 3 Content Packs")
    if "referred_by_code" in st.session_state and st.session_state["referred_by_code"]:
        st.caption(f"👋 คุณเข้าใช้งานผ่านลิงก์ผู้แนะนำ: **{st.session_state['referred_by_code']}**")

    # Hero Section
    st.markdown("""
    <div style='text-align: center; padding: 20px 0 10px 0;'>
        <h1 style='font-size: 2.6em; font-weight: 800; color: #1e293b; margin-bottom: 12px; line-height: 1.25;'>
            ✨ เปลี่ยน 1 หัวข้อ เป็นคอนเทนต์ครบทุกช่องทางด้วย AI
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
    if 'demo_credit_checked_email' not in st.session_state:
        st.session_state['demo_credit_checked_email'] = ""
    if 'demo_is_eligible' not in st.session_state:
        st.session_state['demo_is_eligible'] = False
    if 'demo_credit_type' not in st.session_state:
        st.session_state['demo_credit_type'] = "blocked"
    if 'demo_credit_balance' not in st.session_state:
        st.session_state['demo_credit_balance'] = 0
    if 'demo_status_msg' not in st.session_state:
        st.session_state['demo_status_msg'] = "กรุณากดปุ่มเพื่อตรวจสอบสิทธิ์การใช้งาน"

    if user_email != st.session_state['demo_credit_checked_email']:
        st.session_state['demo_is_eligible'] = False
        st.session_state['demo_credit_type'] = "blocked"
        st.session_state['demo_credit_balance'] = 0
        st.session_state['demo_status_msg'] = "กรุณากดปุ่มเพื่อตรวจสอบเครดิตอีกครั้ง"

    if user_email:
        if st.button("🔍 ตรวจสอบเครดิตและสิทธิ์ใช้งาน", key="demo_verify_credit_btn"):
            with st.spinner("กำลังเชื่อมต่อระบบฐานข้อมูลเครดิต..."):
                try:
                    credit_service = get_credit_service()
                    user = credit_service.get_or_create_user(user_email, user_name, referred_by=st.session_state.get("referred_by_code", ""))
                    st.session_state['demo_user_credit_obj'] = user
                    eligible, c_type, c_bal, c_msg = credit_service.check_credit_eligibility(user_email)
                    
                    st.session_state['demo_is_eligible'] = eligible
                    st.session_state['demo_credit_type'] = c_type
                    st.session_state['demo_credit_balance'] = c_bal
                    st.session_state['demo_status_msg'] = c_msg
                    st.session_state['demo_credit_checked_email'] = user_email
                    st.success("ตรวจสอบข้อมูลเครดิตสำเร็จ!")
                except Exception as e:
                    st.error(f"ไม่สามารถเชื่อมต่อฐานข้อมูลเครดิตได้ชั่วคราว: {e}")
                    st.session_state['demo_is_eligible'] = False
                    st.session_state['demo_credit_type'] = "blocked"
                    st.session_state['demo_status_msg'] = "⚠️ เชื่อมต่อระบบเครดิตขัดข้องชั่วคราว"
                    
        is_eligible = st.session_state['demo_is_eligible']
        credit_type = st.session_state['demo_credit_type']
        credit_balance = st.session_state['demo_credit_balance']
        status_msg = st.session_state['demo_status_msg']
        
        if st.session_state['demo_credit_checked_email'] == user_email:
            if credit_type == "free":
                st.info(f"💡 {status_msg} (คุณใช้สิทธิ์ฟรีไปแล้ว {3 - credit_balance} / 3 Content Packs)")
            elif credit_type == "paid":
                st.success(f"💎 {status_msg} (คุณเหลือเครดิต {credit_balance} Content Packs)")
            elif credit_type == "blocked":
                st.error(f"⚠️ {status_msg}")
            
            # แสดงส่วนประวัติการสร้างคอนเทนต์ของฉัน (Sprint 6.1)
            show_user_history_section(user_email, "demo")
            # แสดงส่วนแดชบอร์ด Referral Partner ของฉัน (Sprint 7)
            show_user_referral_partner_section(user_email, "demo")
        else:
            st.warning("⚠️ มีการกรอกอีเมลใหม่ กรุณากดปุ่มเพื่อเริ่มตรวจสอบสิทธิ์")
    else:
        is_eligible = False
        credit_type = "blocked"
        credit_balance = 0
        status_msg = ""
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
                show_payment_gate()
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
                        
                    elif selected_content_type == "instagram_carousel":
                        topic = st.text_input("หัวข้อสไลด์หลัก *", placeholder="3 นิสัยทำลายการเงินของคนรุ่นใหม่")
                        keyword = st.text_input("คำค้นหาหลัก *", placeholder="การเงินส่วนบุคคล, วิธีเก็บเงิน")
                        st.write("---")
                        st.markdown("**📸 ข้อมูลสไลด์ Instagram Carousel (Visual Context)**")
                        blueprint_inputs["target_audience"] = st.text_input("กลุ่มเป้าหมายผู้รับชม", placeholder="เช่น พนักงานจบใหม่และวัยเริ่มต้นทำงานช่วงอายุ 22-26 ปี")
                        blueprint_inputs["core_story"] = st.text_input("แกนเรื่องเล่าที่ใช้โยงประเด็น", placeholder="เช่น จากคนที่เงินเดือนหมดตั้งแต่สัปดาห์ที่สองของเดือนจนต้องเริ่มเปลี่ยนตัวเอง")
                        blueprint_inputs["key_insight"] = st.text_input("ข้อมูลเจาะลึกที่คนทั่วไปมักเข้าใจผิด", placeholder="เช่น เงินออมไม่ได้ขึ้นอยู่กับจำนวนเงินที่หาได้ แต่ขึ้นอยู่กับการควบคุมค่าใช้จ่ายคงที่")
                        blueprint_inputs["tone"] = st.text_input("สไตล์น้ำเสียง", placeholder="เช่น เป็นกันเอง เข้าใจง่าย สดใหม่เหมือนคุยกับรุ่นพี่ที่หวังดี")
                        blueprint_inputs["cta"] = st.text_input("ข้อความปิดท้ายเชิญชวน (CTA)", placeholder="เช่น กดเซฟเก็บไว้ทบทวน หรือแชร์เตือนใจเพื่อนใกล้ตัวคุณ")

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
                                credit_service = get_credit_service()
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
                            st.error(f"เกิดข้อผิดพลาดในการประมวลผลสัญญาณ: {err}")
                            # บันทึกประวัติความล้มเหลวลงในชีต Usage Logs โดยไม่หักแต้มเครดิต
                            try:
                                credit_service = get_credit_service()
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
    st.info("🎁 ทดลองใช้ฟรี 3 Content Packs")
    if "referred_by_code" in st.session_state and st.session_state["referred_by_code"]:
        st.caption(f"👋 คุณเข้าใช้งานผ่านลิงก์ผู้แนะนำ: **{st.session_state['referred_by_code']}**")

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
    if 'std_credit_checked_email' not in st.session_state:
        st.session_state['std_credit_checked_email'] = ""
    if 'std_is_eligible' not in st.session_state:
        st.session_state['std_is_eligible'] = False
    if 'std_credit_type' not in st.session_state:
        st.session_state['std_credit_type'] = "blocked"
    if 'std_credit_balance' not in st.session_state:
        st.session_state['std_credit_balance'] = 0
    if 'std_status_msg' not in st.session_state:
        st.session_state['std_status_msg'] = "กรุณากดปุ่มเพื่อตรวจสอบสิทธิ์การใช้งาน"

    if user_email != st.session_state['std_credit_checked_email']:
        st.session_state['std_is_eligible'] = False
        st.session_state['std_credit_type'] = "blocked"
        st.session_state['std_credit_balance'] = 0
        st.session_state['std_status_msg'] = "กรุณากดปุ่มเพื่อตรวจสอบเครดิตอีกครั้ง"

    if user_email:
        if st.button("🔍 ตรวจสอบเครดิตและสิทธิ์ใช้งาน", key="std_verify_credit_btn"):
            with st.spinner("กำลังเชื่อมต่อระบบฐานข้อมูลเครดิต..."):
                try:
                    credit_service = get_credit_service()
                    user = credit_service.get_or_create_user(user_email, user_name, referred_by=st.session_state.get("referred_by_code", ""))
                    st.session_state['std_user_credit_obj'] = user
                    eligible, c_type, c_bal, c_msg = credit_service.check_credit_eligibility(user_email)
                    
                    st.session_state['std_is_eligible'] = eligible
                    st.session_state['std_credit_type'] = c_type
                    st.session_state['std_credit_balance'] = c_bal
                    st.session_state['std_status_msg'] = c_msg
                    st.session_state['std_credit_checked_email'] = user_email
                    st.success("ตรวจสอบข้อมูลเครดิตสำเร็จ!")
                except Exception as e:
                    st.error(f"ไม่สามารถเชื่อมต่อฐานข้อมูลเครดิตได้ชั่วคราว: {e}")
                    st.session_state['std_is_eligible'] = False
                    st.session_state['std_credit_type'] = "blocked"
                    st.session_state['std_status_msg'] = "⚠️ เชื่อมต่อระบบเครดิตขัดข้องชั่วคราว"
                    
        is_eligible = st.session_state['std_is_eligible']
        credit_type = st.session_state['std_credit_type']
        credit_balance = st.session_state['std_credit_balance']
        status_msg = st.session_state['std_status_msg']
        
        if st.session_state['std_credit_checked_email'] == user_email:
            if credit_type == "free":
                st.info(f"💡 {status_msg} (คุณใช้สิทธิ์ฟรีไปแล้ว {3 - credit_balance} / 3 Content Packs)")
            elif credit_type == "paid":
                st.success(f"💎 {status_msg} (คุณเหลือเครดิต {credit_balance} Content Packs)")
            elif credit_type == "blocked":
                st.error(f"⚠️ {status_msg}")
            
            # แสดงส่วนประวัติการสร้างคอนเทนต์ของฉัน (Sprint 6.1)
            show_user_history_section(user_email, "std")
            # แสดงส่วนแดชบอร์ด Referral Partner ของฉัน (Sprint 7)
            show_user_referral_partner_section(user_email, "std")
        else:
            st.warning("⚠️ มีการกรอกอีเมลใหม่ กรุณากดปุ่มเพื่อเริ่มตรวจสอบสิทธิ์")
    else:
        is_eligible = False
        credit_type = "blocked"
        credit_balance = 0
        status_msg = ""
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
                show_payment_gate()
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
                    blueprint_inputs["experience_story"] = st.text_input("ประสบการณ์หรือมุมมองสำคัญที่เล่า", placeholder="เช่น เคยล้มป่วยจากสัญญาณทำงานหามรุ่งหามค่ำจนเปลี่ยนชีวิต")
                    blueprint_inputs["core_identity"] = st.text_input("ภาพลักษณ์ที่ต้องการสร้าง", placeholder="เช่น ผู้ให้คำปรึกษาที่ให้ผลลัพธ์ที่เป็นความจริง สไตล์จริงใจตรงไปตรงมา")
                    blueprint_inputs["key_takeaway"] = st.text_input("ข้อความหลักที่อยากให้คนจดจำ", placeholder="เช่น การปัดปฏิเสธงานไม่สำคัญคือทักษะการเพิ่มผลิตภาพที่แท้จริง")
                    blueprint_inputs["tone"] = st.text_input("สไตล์การเขียน", placeholder="เช่น เล่าเรื่องผ่านตัวคุณ เป็นกันเองจริงใจ มีความสุภาพแต่น่าฟัง")
                    blueprint_inputs["cta"] = st.text_input("คำเชิญชวนดำเนินการ (CTA)", placeholder="เช่น กดแชร์หากคุณคิดเหมือนกัน หรือทักเรามาใต้คอมเมนต์เพื่อแลกไอเดีย")
                    
                elif selected_content_type == "instagram_carousel":
                    topic = st.text_input("หัวข้อสไลด์หลัก *", placeholder="3 นิสัยทำลายการเงินของคนรุ่นใหม่")
                    keyword = st.text_input("คำค้นหาหลัก *", placeholder="การเงินส่วนบุคคล, วิธีเก็บเงิน")
                    st.write("---")
                    st.markdown("**📸 ข้อมูลสไลด์ Instagram Carousel (Visual Context)**")
                    blueprint_inputs["target_audience"] = st.text_input("กลุ่มเป้าหมายผู้รับชม", placeholder="เช่น พนักงานจบใหม่และวัยเริ่มต้นทำงานช่วงอายุ 22-26 ปี")
                    blueprint_inputs["core_story"] = st.text_input("แกนเรื่องเล่าที่ใช้โยงประเด็น", placeholder="เช่น จากคนที่เงินเดือนหมดตั้งแต่สัปดาห์ที่สองของเดือนจนต้องเริ่มเปลี่ยนตัวเอง")
                    blueprint_inputs["key_insight"] = st.text_input("ข้อมูลเจาะลึกที่คนทั่วไปมักเข้าใจผิด", placeholder="เช่น เงินออมไม่ได้ขึ้นอยู่กับจำนวนเงินที่หาได้ แต่ขึ้นอยู่กับการควบคุมค่าใช้จ่ายคงที่")
                    blueprint_inputs["tone"] = st.text_input("สไตล์น้ำเสียง", placeholder="เช่น เป็นกันเอง เข้าใจง่าย สดใหม่เหมือนคุยกับรุ่นพี่ที่หวังดี")
                    blueprint_inputs["cta"] = st.text_input("ข้อความปิดท้ายเชิญชวน (CTA)", placeholder="เช่น กดเซฟเก็บไว้ทบทวน หรือแชร์เตือนใจเพื่อนใกล้ตัวคุณ")
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
    st.info("💡 สามารถตรวจสอบประวัติคิวงานสะสมได้โดยการกดปุ่มแสดงตารางด้านล่าง")

    if 'show_history_table' not in st.session_state:
        st.session_state['show_history_table'] = False

    col_history_btn1, col_history_btn2 = st.columns([1, 4])
    with col_history_btn1:
        if st.button("📥 โหลดแสดงตารางประวัติงาน"):
            st.session_state['show_history_table'] = True
    with col_history_btn2:
        if st.session_state['show_history_table']:
            if st.button("❌ ซ่อนตารางประวัติ"):
                st.session_state['show_history_table'] = False
                st.rerun()

    if st.session_state['show_history_table']:
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
            st.error(f"ไม่สามารถโหลดสรุปข้อมูลตารางคิวงานได้ชั่วคราว: {e}")

    # ระบบจัดการ Referral Partner สำหรับแอดมิน (Sprint 7)
    st.markdown("---")
    show_admin_referral_manager()
