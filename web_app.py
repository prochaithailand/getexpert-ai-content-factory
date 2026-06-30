import streamlit as st
import time
import os
import logging
from config.settings import Settings
from services.sheets_service import SheetsService

# กำหนดหน้าจอหลักของ Streamlit
st.set_page_config(
    page_title="GetExpert AI Content Factory Portal",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# สไตล์ CSS เพิ่มเติมเพื่อความพรีเมียม (Glassmorphism & Custom Elements)
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
    
    .card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# เริ่มต้นเรียกเซอร์วิส Sheets
@st.cache_resource
def get_sheets_service():
    return SheetsService()

try:
    sheets_service = get_sheets_service()
except Exception as e:
    st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets API ได้: {e}")
    st.stop()

# หัวข้อหลัก
st.title("🚀 GetExpert AI Content Factory Portal")
st.markdown("ระบบอำนวยความสะดวกในการป้อนหัวข้อบทความเข้าคิวงานประมวลผลหลังบ้าน (Sprint 3: Web Form MVP)")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 ป้อนข้อมูลคำขอเขียนบทความ")
    
    with st.form("content_form", clear_on_submit=True):
        topic = st.text_input("หัวข้อบทความ (Topic)", placeholder="เช่น วิธีประหยัดค่าไฟช่วงหน้าร้อน")
        keyword = st.text_input("คำสำคัญหลัก (Focus Keyword)", placeholder="เช่น ประหยัดค่าไฟ, แอร์บ้าน")
        
        submitted = st.form_submit_button("ส่งคำขอเขียนบทความ (Add to Queue)")
        
        if submitted:
            if not topic or not keyword:
                st.error("กรุณากรอกทั้งหัวข้อและคีย์เวิร์ดคีย์ข้อมูล")
            else:
                try:
                    # แทรกข้อมูลแถวใหม่ลง Google Sheet
                    row_idx = sheets_service.add_new_row(topic, keyword)
                    st.session_state['last_row_idx'] = row_idx
                    st.success(f"ส่งคำขอเข้าสู่คิวงานเรียบร้อยแล้ว! (พิกัดแถวที่ {row_idx})")
                except Exception as error:
                    st.error(f"เกิดปัญหาในการบันทึกลงชีต: {error}")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🔍 ตรวจเช็คสถานะรายการส่งล่าสุด")
    
    if 'last_row_idx' in st.session_state:
        row_idx = st.session_state['last_row_idx']
        
        # ดึงสถานะปัจจุบันของแถวนั้น
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
                st.success("🎉 ระบบประมวลผลและสร้างบล็อกร่างเรียบร้อยแล้ว!")
                st.write(f"**SEO Title:** {row_data.seo_title}")
                st.write(f"**Meta Description:** {row_data.meta_description}")
                st.markdown(f"🔗 [คลิกเปิดอ่านร่างบน Blogger]({row_data.blogger_url})")
            elif status_lower == "failed":
                st.error(f"❌ การทำงานขัดข้องหลังพยายาม Retry ครบกำหนด: {row_data.last_error}")
            else:
                st.warning("⏳ รอการประมวลผล (กรุณากดรัน Engine main.py หรือรอตัวกระตุ้น Scheduler)")
                
            if st.button("🔄 โหลดรีเฟรชสถานะแถวล่าสุด"):
                st.rerun()
                
        except Exception as e:
            st.error(f"ไม่สามารถดึงข้อมูลสำหรับแถวที่ {row_idx} ได้: {e}")
    else:
        st.write("ยังไม่มีการส่งหัวข้อคำขอใหม่ในเซสชั่นนี้")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# แดชบอร์ดสรุปตารางคิวงานทั้งหมด
st.subheader("📋 รายการประมวลผลคอนเทนต์ทั้งหมด (Content Queue Dashboard)")

if st.button("🔄 โหลดรีเฟรชตารางข้อมูล"):
    st.rerun()

try:
    all_rows = sheets_service.read_all_rows()
    if all_rows:
        # แปลงข้อมูลวัตถุ Pydantic เข้าสู่รูปแบบตารางเพื่อแสดงผลใน Streamlit
        table_data = []
        for row in reversed(all_rows): # กลับลำดับเพื่อให้แถวใหม่สุดอยู่บนสุด
            table_data.append({
                "ID": row.id,
                "Topic": row.topic,
                "Keyword": row.keyword,
                "Status": row.status,
                "SEO Title": row.seo_title,
                "Blogger URL": row.blogger_url,
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
