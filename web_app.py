import streamlit as st
import time
import os
import logging
from config.settings import Settings
from services.sheets_service import SheetsService
from services.gemini_service import GeminiService
from services.blogger_service import BloggerService

# กำหนดหน้าจอหลักของ Streamlit
st.set_page_config(
    page_title="GetExpert AI Content Factory Portal",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# สไตล์ CSS เพิ่มเติมเพื่อความพรีเมียม (ไม่มีส่วนห่อหุ้ม card html ที่แยกส่วนตัวเปิด/ปิดอีกต่อไป)
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

# เริ่มต้นเรียกเซอร์วิส Sheets
@st.cache_resource
def get_sheets_service():
    return SheetsService()

try:
    sheets_service = get_sheets_service()
except Exception as e:
    st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets API ได้: {e}")
    st.stop()

# ตรวจสอบ URL Parameter ว่าเป็น Demo Mode หรือไม่ (?demo=true)
is_demo = st.query_params.get("demo", "false").lower() == "true"

if is_demo:
    # ----------------------------------------------------
    # DEMO MODE (Client Trial - คลีนและรันตอบสนองทันที - UX Sprint 1)
    # ----------------------------------------------------
    # Hero Section
    st.markdown("""
    <div style='text-align: center; padding: 20px 0 10px 0;'>
        <h1 style='font-size: 2.6em; font-weight: 800; color: #1e293b; margin-bottom: 12px; line-height: 1.25;'>
            🚀 เปลี่ยน 1 หัวข้อ เป็นคอนเทนต์ครบทุกช่องทางด้วย AI
        </h1>
        <p style='font-size: 1.2em; color: #64748b; font-weight: 400; margin-bottom: 25px; max-width: 800px; margin-left: auto; margin-right: auto;'>
            สร้างบทความ SEO, Facebook, TikTok, YouTube และ AI Image Prompt พร้อมใช้งานภายในไม่กี่นาที
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Value Cards (ใช้ตู้คอนเทนเนอร์แบบ Native)
    with st.container(border=True):
        st.markdown("<h4 style='margin-bottom: 15px; color: #1e293b; font-weight: 700;'>🎁 คุณจะได้รับคอนเทนต์ทั้งหมดจากหัวข้อเดียว:</h4>", unsafe_allow_html=True)
        v_col1, v_col2, v_col3, v_col4, v_col5 = st.columns(5)
        v_col1.markdown("📄 **SEO Article**")
        v_col2.markdown("📘 **Facebook Post**")
        v_col3.markdown("🎬 **TikTok Script**")
        v_col4.markdown("▶️ **YouTube Shorts**")
        v_col5.markdown("🖼️ **AI Image Prompt**")
        st.markdown("<div style='margin-top: 10px; font-size: 0.8em; color: #94a3b8; font-weight: 500; text-align: right;'>ทั้งหมดสร้างจากหัวข้อเดียว</div>", unsafe_allow_html=True)

    st.write("") # เว้นบรรทัดสั้นๆ
    col1, col2 = st.columns([1, 1.2])

    with col1:
        # ฟอร์มรับข้อมูลห่อหุ้มใน Container(border=True)
        with st.container(border=True):
            st.subheader("💡 บอก AI เกี่ยวกับธุรกิจของคุณ")
            
            with st.form("demo_content_form", clear_on_submit=False):
                topic = st.text_input(
                    "หัวข้อที่ต้องการสร้างคอนเทนต์ *", 
                    placeholder="น้ำมันสนเข็มแดงช่วยบรรเทาอาการปวดเมื่อยได้อย่างไร"
                )
                keyword = st.text_input(
                    "คำค้นหาหลัก *", 
                    placeholder="น้ำมันสนเข็มแดง"
                )
                
                st.write("---")
                st.markdown("**🎯 ข้อมูลแนวทางแบรนด์ (Brand Guidelines)**")
                target_audience = st.text_input(
                    "ลูกค้าของคุณคือใคร", 
                    placeholder="คนวัยทำงานที่มีอาการปวดคอ บ่า ไหล่"
                )
                business_type = st.text_input(
                    "ธุรกิจของคุณ", 
                    placeholder="ธุรกิจผลิตภัณฑ์สุขภาพ"
                )
                content_goal = st.text_input(
                    "คุณต้องการให้คอนเทนต์ช่วยอะไร", 
                    placeholder="สร้างความน่าเชื่อถือและเพิ่มยอดขาย"
                )
                tone = st.text_input(
                    "สไตล์การเขียน", 
                    placeholder="เป็นกันเอง เข้าใจง่าย น่าเชื่อถือ"
                )
                
                submitted = st.form_submit_button("✨ สร้าง Content Pack")
                
                if submitted:
                    if not topic or not keyword:
                        st.error("กรุณากรอกทั้งหัวข้อและคีย์เวิร์ด (ช่องที่มีเครื่องหมาย *)")
                    else:
                        try:
                            # รันประมวลผลแบบ Synchronous พร้อม st.status ลิสต์ทีละขั้นตอน (Loading Experience)
                            with st.status("🧠 วิเคราะห์หัวข้อ...", expanded=True) as status_box:
                                
                                # 1. เขียนจองคิวลงชีต
                                status_box.update(label="📚 วิเคราะห์คีย์เวิร์ด...")
                                row_idx = sheets_service.add_new_row(
                                    topic=topic,
                                    keyword=keyword,
                                    target_audience=target_audience,
                                    business_type=business_type,
                                    content_goal=content_goal,
                                    tone=tone
                                )
                                sheets_service.update_row_status(row_idx, "Processing")
                                
                                # 2. เรียกใช้งาน Gemini API
                                status_box.update(label="✍️ สร้างบทความ SEO...")
                                gemini_service = GeminiService()
                                seo_content = gemini_service.generate_blogger_article(
                                    topic=topic,
                                    keyword=keyword,
                                    target_audience=target_audience,
                                    business_type=business_type,
                                    content_goal=content_goal,
                                    tone=tone
                                )
                                
                                # 3. อัปโหลดขึ้น Blogger Draft
                                status_box.update(label="📘 สร้าง Facebook...")
                                # (ประมวลผลเสร็จแล้วในออบเจ็กต์โครงสร้าง JSON)
                                
                                status_box.update(label="🎬 สร้าง TikTok...")
                                # (สคริปต์บรรจุเรียบร้อย)
                                
                                status_box.update(label="▶️ สร้าง YouTube Shorts...")
                                # (สคริปต์ Shorts บรรจุเรียบร้อย)
                                
                                status_box.update(label="🖼️ สร้าง AI Image Prompt...")
                                # (คำแนะแนววาดภาพบรรจุเรียบร้อย)
                                
                                status_box.update(label="🔗 อัปโหลดแบบร่าง Blogger...")
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
                                "article_html": full_html
                            }
                        except Exception as err:
                            st.error(f"เกิดข้อผิดพลาดในการประมวลผลสัญญาน: {err}")

    with col2:
        # ส่วนแสดงผลลัพธ์ห่อหุ้มใน Container(border=True)
        with st.container(border=True):
            if 'demo_result' in st.session_state:
                res = st.session_state['demo_result']
                
                # Success Banner
                st.success("🎉 Content Pack พร้อมใช้งานแล้ว")
                
                tab_blogger, tab_facebook, tab_tiktok, tab_youtube, tab_image = st.tabs([
                    "📰 Blogger & SEO", 
                    "📘 Facebook Post", 
                    "🎵 TikTok Script", 
                    "🔴 YouTube Shorts",
                    "🎨 Image Prompts"
                ])
                
                with tab_blogger:
                    st.info("📋 คัดลอกเพื่อนำไปใช้งานได้ทันที (คัดลอกซอร์สโค้ด HTML ด้านล่างสุด หรือเปิดร่างใน Blogger)")
                    st.markdown(f"🔗 **Blogger Link:** [คลิกเปิดอ่านร่างบทความบนเว็บ Blogger]({res['blogger_url']})")
                    st.write(f"**SEO Title:** {res['seo_title']}")
                    st.write(f"**Meta Description:** {res['meta_description']}")
                    st.write(f"**Slug (URL แนะนำ):** `{res['slug_suggestion']}`")
                    st.write(f"**Focus Keyword:** {res['focus_keyword']}")
                    st.write(f"**Summary:** {res['content_summary']}")
                    st.write("---")
                    st.write("**ตัวอย่างหน้าตาบทความ (Formatted Preview):**")
                    st.markdown(res['article_html'], unsafe_allow_html=True)
                    st.write("---")
                    st.write("**ซอร์สโค้ด HTML (สำหรับก๊อปปี้ไปวางหลังบ้านเว็บอื่นๆ):**")
                    st.code(res['article_html'], language="html")
                    
                with tab_facebook:
                    st.info("📋 คัดลอกเพื่อนำไปใช้งานได้ทันที (คลิกปุ่ม Copy ที่มุมขวาบนของกล่องรหัส)")
                    st.markdown("**ข้อความโพสต์แนะนำสำหรับ Facebook:**")
                    st.code(res['facebook_post'], language=None)
                    st.write(f"**แฮชแท็กแนะนำ:** {res['facebook_hashtags']}")
                    
                with tab_tiktok:
                    st.info("📋 คัดลอกเพื่อนำไปใช้งานได้ทันที (คลิกปุ่ม Copy ที่มุมขวาบนของกล่องรหัสเพื่อคัดลอกสคริปต์)")
                    st.markdown(f"🔥 **TikTok Hook ดึงดูดสายตา:** *\"{res['tiktok_hook']}\"*")
                    st.markdown("**สคริปต์สั้นบทพูดและแนวภาพ TikTok:**")
                    st.code(res['tiktok_script'], language=None)
                    
                with tab_youtube:
                    st.info("📋 คัดลอกเพื่อนำไปใช้งานได้ทันที (คลิกปุ่ม Copy ที่มุมขวาบนเพื่อคัดลอกสคริปต์ Shorts)")
                    st.write(f"🎥 **YouTube Shorts Title:** {res['youtube_title']}")
                    st.write(f"**YouTube Description:** {res['youtube_description']}")
                    st.markdown("**สคริปต์สำหรับวิดีโอ YouTube Shorts:**")
                    st.code(res['youtube_shorts_script'], language=None)
                    
                with tab_image:
                    st.info("📋 คัดลอกเพื่อนำไปใช้งานได้ทันที (คลิกปุ่ม Copy มุมขวาเพื่อนำคำสั่งไปส่ง AI วาดภาพ)")
                    st.markdown("**Featured Image Prompt:**")
                    st.code(res['featured_image_prompt'], language=None)
                    st.write(f"**Image Style:** {res['image_style']}")
                    st.write(f"**Concept:** {res['image_concept']}")
            else:
                # Empty State (ก่อนลูกค้ากดเจนเนื้อหา - ใช้กล่องข้อความ HTML ปิดสมบูรณ์ในตัวเดียว)
                st.markdown("""
                <div style='text-align: center; padding: 40px 20px;'>
                    <div style='font-size: 55px; margin-bottom: 20px;'>📦</div>
                    <h3 style='margin-bottom: 15px; color: #1e293b; font-weight: 700; font-size: 1.3em;'>Content Pack ของคุณจะประกอบด้วย</h3>
                    <div style='text-align: left; max-width: 280px; margin: 0 auto 25px auto; color: #475569; font-size: 0.95em; line-height: 1.8; font-weight: 500;'>
                        • 📄 บทความ SEO พร้อมใช้งาน<br/>
                        • 📘 โพสต์ Facebook ดึงดูดความสนใจ<br/>
                        • 🎬 สคริปต์วิดีโอสั้นลง TikTok<br/>
                        • ▶️ สคริปต์วิดีโอ YouTube Shorts<br/>
                        • 🖼️ Prompt วาดรูปภาพปกด้วย AI
                    </div>
                    <p style='font-weight: 700; color: #007bff; font-size: 1em; margin-top: 15px;'>เมื่อพร้อมแล้ว กรอกข้อมูลด้านซ้ายแล้วกดปุ่ม "✨ สร้าง Content Pack"</p>
                </div>
                """, unsafe_allow_html=True)

else:
    # ----------------------------------------------------
    # STANDARD MODE (Admin Portal - เมนูจัดการหลังบ้านเดิม)
    # ----------------------------------------------------
    st.title("🚀 GetExpert AI Content Factory Portal")
    st.markdown("ระบบผลิตชุดโซเชียลคอนเทนต์ครบวงจร (Sprint 4: Client Delivery & Content Pack MVP)")

    col1, col2 = st.columns([1, 1.2])

    with col1:
        with st.container(border=True):
            st.subheader("📝 ป้อนคำขอเขียนบทความและระบุแนวทางแบรนด์")
            
            with st.form("content_form", clear_on_submit=True):
                topic = st.text_input("หัวข้อบทความ (Topic) *", placeholder="เช่น วิธีประหยัดค่าไฟช่วงหน้าร้อน")
                keyword = st.text_input("คำสำคัญหลัก (Focus Keyword) *", placeholder="เช่น ประหยัดค่าไฟ, แอร์บ้าน")
                
                st.write("---")
                st.markdown("**🎯 ข้อมูลบริบทแบรนด์ (Brand Contexts)**")
                target_audience = st.text_input("กลุ่มเป้าหมาย (Target Audience)", placeholder="เช่น เจ้าของธุรกิจขนาดเล็ก, พนักงานบริษัท")
                business_type = st.text_input("ประเภทธุรกิจ (Business Type)", placeholder="เช่น ร้านอาหาร, คลินิกความงาม")
                content_goal = st.text_input("เป้าหมายเนื้อหา (Content Goal)", placeholder="เช่น ดึงผู้ซื้อรายใหม่, เพิ่มยอดแอดไลน์")
                tone = st.text_input("โทนน้ำเสียงที่ต้องการ (Tone)", placeholder="เช่น สุภาพเป็นทางการ, สนุกสนานเป็นกันเอง")
                
                submitted = st.form_submit_button("ส่งคำขอเขียนและแพ็คคอนเทนต์ (Add to Queue)")
                
                if submitted:
                    if not topic or not keyword:
                        st.error("กรุณากรอกหัวข้อและคำสำคัญคีย์หลัก (มีเครื่องหมาย *)")
                    else:
                        try:
                            # แทรกข้อมูลแถวใหม่พร้อมรายละเอียดบริบทลงชีต
                            row_idx = sheets_service.add_new_row(
                                topic=topic,
                                keyword=keyword,
                                target_audience=target_audience,
                                business_type=business_type,
                                content_goal=content_goal,
                                tone=tone
                            )
                            st.session_state['last_row_idx'] = row_idx
                            st.success(f"ส่งคำขอเข้าสู่คิวงานเรียบร้อยแล้ว! (พิกัดแถวที่ {row_idx})")
                        except Exception as error:
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
                        
                        # แบ่งหมวดหมู่งานคัดลอกด้วย Tabs
                        tab_blogger, tab_facebook, tab_tiktok, tab_youtube, tab_image = st.tabs([
                            "📰 Blogger & SEO", 
                            "📘 Facebook Post", 
                            "🎵 TikTok Script", 
                            "🔴 YouTube Shorts",
                            "🎨 Image Prompts"
                        ])
                        
                        with tab_blogger:
                            st.markdown(f"🔗 **Blogger Draft URL:** [คลิกเปิดร่างบทความใน Blogger]({row_data.blogger_url})")
                            st.write(f"**Blogger Post ID:** `{row_data.blogger_post_id}`")
                            st.write(f"**SEO Title:** {row_data.seo_title}")
                            st.write(f"**Meta Description:** {row_data.meta_description}")
                            st.write(f"**Slug Recommendation:** `{row_data.slug_suggestion}`")
                            st.write(f"**Focus Keyword:** {row_data.focus_keyword}")
                            st.write(f"**Related Keywords:** {row_data.related_keywords}")
                            st.write(f"**Content Summary:** {row_data.content_summary}")
                            
                        with tab_facebook:
                            st.markdown("**โพสต์แนะนำสำหรับ Facebook (สามารถคลิกมุมขวาบนเพื่อคัดลอกได้ทันที):**")
                            st.code(row_data.facebook_post, language=None)
                            st.write(f"**แนะนำแฮชแท็ก:** {row_data.facebook_hashtags}")
                            
                        with tab_tiktok:
                            st.markdown(f"🔥 **TikTok Hook (3 วินาทีแรก):** *\"{row_data.tiktok_hook}\"*")
                            st.markdown("**สคริปต์สั้นบทพูดและแนวภาพ TikTok (Copy ไปใช้งานอัดคลิป):**")
                            st.code(row_data.tiktok_script, language=None)
                            
                        with tab_youtube:
                            st.write(f"🎥 **YouTube Shorts Title:** {row_data.youtube_title}")
                            st.write(f"**YouTube Description:** {row_data.youtube_description}")
                            st.markdown("**สคริปต์วิดีโอ YouTube Shorts:**")
                            st.code(row_data.youtube_shorts_script, language=None)
                            
                        with tab_image:
                            st.markdown("**Featured Image Prompt (Midjourney / DALL-E):**")
                            st.code(row_data.featured_image_prompt, language=None)
                            st.write(f"**Image Style:** {row_data.image_style}")
                            st.write(f"**Image Concept:** {row_data.image_concept}")
                            
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
                table_data.append({
                    "ID": row.id,
                    "Topic": row.topic,
                    "Keyword": row.keyword,
                    "Status": row.status,
                    "SEO Title": row.seo_title,
                    "Blogger URL": row.blogger_url,
                    "Audience": row.target_audience,
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
