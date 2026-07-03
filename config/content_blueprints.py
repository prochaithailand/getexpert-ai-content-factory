# config/content_blueprints.py

CONTENT_BLUEPRINTS = {
    "business": {
        "label": "📈 ธุรกิจ / สินค้า",
        "description": "เหมาะสำหรับสินค้า บริการ การตลาดออนไลน์ และการสร้างยอดขาย",
        "form_fields": [
            "topic",
            "keyword",
            "business_name",
            "target_audience",
            "customer_problem",
            "unique_value",
            "marketing_goal",
            "tone",
            "cta"
        ],
        "prompt_strategy": {
            "role": "Senior Marketing Content Strategist",
            "focus": ["Marketing", "SEO", "Call-to-Action", "Conversion"],
            "rules": [
                "เขียนด้วยจุดมุ่งหมายทางการตลาดที่ชัดเจน น่าสนใจและกระตุ้นการขายอย่างสมเหตุสมผล",
                "เน้นการบอกเล่าความเจ็บปวด (Pain Point) ของลูกค้าและประโยชน์ที่จะได้รับจากผลิตภัณฑ์",
                "มีคำเชิญชวน (CTA) ที่จูงใจแต่ไม่โอ้อวดเกินจริง",
                "สร้างแฮชแท็กสนับสนุนการตลาดและแบรนด์จำนวน 5-8 รายการ ปลอดภัยจาก HTML tags"
            ]
        },
        "outputs": {
            "seo_article": "📰 SEO Article",
            "facebook_post": "📘 Facebook Post",
            "tiktok_script": "🎵 TikTok Script",
            "youtube_script": "🔴 YouTube Shorts",
            "image_prompt": "🎨 Image Prompt"
        }
    },

    "government": {
        "label": "🏛 หน่วยงานราชการ",
        "description": "เหมาะสำหรับข่าวประชาสัมพันธ์ โครงการรัฐ และการสื่อสารกับประชาชน",
        "form_fields": [
            "topic",
            "keyword",
            "agency_name",
            "public_target",
            "project_objective",
            "public_benefit",
            "key_information",
            "contact_channel",
            "tone"
        ],
        "prompt_strategy": {
            "role": "Public Communication & Government PR Writer",
            "focus": ["Public Information", "Trust", "Clarity", "No Hard Sell"],
            "rules": [
                "ใช้ภาษาสุภาพ เป็นทางการ น่าเชื่อถือ และเข้าใจง่ายสำหรับประชาชนทุกระดับ",
                "ห้ามใช้ภาษาขายของหรือการทำ Hard Sell เชิงพาณิชย์เด็ดขาด",
                "เน้นย้ำสิทธิประโยชน์หรือสิ่งที่ประชาชนจะได้รับจากรัฐอย่างตรงไปตรงมา",
                "มีข้อมูลติดต่อประชาสัมพันธ์และขั้นตอนปฏิบัติการเข้าร่วมที่ชัดเจน",
                "สร้างแฮชแท็กเชิงประชาสัมพันธ์ ชุมชน หน่วยงาน หรือประโยชน์ต่อประชาชนจำนวน 5-8 รายการ หลีกเลี่ยงคำเชิงขายของ เช่น #โปรเด็ด #ซื้อเลย #ลดราคา โดยเด็ดขาด และต้องไม่มี HTML tags"
            ]
        },
        "outputs": {
            "seo_article": "📰 ข่าวประชาสัมพันธ์ (Press Release)",
            "facebook_post": "📘 โพสต์ประกาศราชการ (PR Post)",
            "tiktok_script": "🎵 สคริปต์สั้นแจ้งประชาชน (TikTok)",
            "youtube_script": "🔴 คำอธิบายภาพ Infographic (YouTube)",
            "image_prompt": "🎨 ภาพประกอบประชาสัมพันธ์"
        }
    },

    "csr": {
        "label": "❤️ โครงการเพื่อสังคม / CSR",
        "description": "เหมาะสำหรับแคมเปญเพื่อสังคม การชวนมีส่วนร่วม และการสื่อสาร Impact",
        "form_fields": [
            "topic",
            "keyword",
            "campaign_name",
            "social_problem",
            "affected_group",
            "campaign_goal",
            "expected_impact",
            "participation_invite",
            "organization_name",
            "tone"
        ],
        "prompt_strategy": {
            "role": "Social Impact Storyteller & CSR Director",
            "focus": ["Social Impact", "Inspiration", "Community Engagement", "Empathy"],
            "rules": [
                "เน้นการสร้างความตระหนักรู้ แรงบันดาลใจ และการมีความรู้สึกร่วม (Empathy)",
                "ชูประเด็นปัญหาสังคมและแสดงผลลัพธ์ที่เป็นรูปธรรมต่อชุมชน (Social Impact)",
                "ชักชวนเชิญชวนผู้อ่านให้เข้ามามีส่วนร่วมช่วยเหลือกัน ไม่ใช่การโฆษณาขายสินค้าแบรนด์ตรงๆ",
                "เขียนด้วยน้ำเสียงที่อบอุ่น มุ่งมั่น และเห็นอกเห็นใจเพื่อนมนุษย์",
                "สร้างแฮชแท็กเชิงสังคม รณรงค์ หรือปลุกจิตสาธารณะจำนวน 5-8 รายการ หลีกเลี่ยงคำเชิงขายของ เช่น #โปรเด็ด #ซื้อเลย #ลดราคา โดยเด็ดขาด และต้องไม่มี HTML tags"
            ]
        },
        "outputs": {
            "seo_article": "📰 บทความโครงการเพื่อสังคม (CSR Campaign)",
            "facebook_post": "📘 โพสต์ชวนร่วมแคมเปญ (CSR Post)",
            "tiktok_script": "🎵 สคริปต์เล่าเรื่องสะกดใจ (TikTok)",
            "youtube_script": "🔴 สคริปต์วิดีโอสรุปผลกระทบ (YouTube)",
            "image_prompt": "🎨 ภาพแนวคิดแคมเปญสังคม"
        }
    },

    "education": {
        "label": "🎓 การศึกษา",
        "description": "เหมาะสำหรับบทเรียน ข่าวกิจกรรม โรงเรียน มหาวิทยาลัย และคอร์สอบรม",
        "form_fields": [
            "topic",
            "keyword",
            "institution_name",
            "learner_group",
            "learning_objective",
            "core_knowledge",
            "expected_outcome",
            "content_format",
            "tone"
        ],
        "prompt_strategy": {
            "role": "Academic Educator & Content Curriculum Designer",
            "focus": ["Academic Integrity", "Easy-to-Understand", "Structured Knowledge", "Educational Value"],
            "rules": [
                "เขียนข้อมูลด้วยความถูกต้องทางวิชาการ มีการอ้างอิงหรือใช้เหตุผลเชิงตรรกะที่น่าเชื่อถือ",
                "เรียบเรียงเนื้อหาให้เข้าใจง่าย แบ่งประเด็นชัดเจนและเหมาะกับช่วงวัยหรือระดับของผู้เรียน",
                "หลีกเลี่ยงการขายของเชิงพาณิชย์ เน้นการแบ่งปันความรู้และการให้คุณค่าทางการศึกษาอย่างเป็นรูปธรรม",
                "มีการแบ่งขั้นตอนการทำความเข้าใจเป็นข้อย่อยชัดเจน",
                "สร้างแฮชแท็กส่งเสริมความรู้ สาระการศึกษา หรือคอร์สอบรมจำนวน 5-8 รายการ หลีกเลี่ยงคำเชิงขายของ เช่น #โปรเด็ด #ซื้อเลย #ลดราคา โดยเด็ดขาด และต้องไม่มี HTML tags"
            ]
        },
        "outputs": {
            "seo_article": "📰 บทความคลังความรู้ (Educational Content)",
            "facebook_post": "📘 โพสต์แบ่งปันความรู้ (Knowledge Share)",
            "tiktok_script": "🎵 สคริปต์สั้นสรุปบทเรียน (TikTok)",
            "youtube_script": "🔴 สคริปต์เล่าความรู้เชิงลึก (YouTube)",
            "image_prompt": "🎨 ภาพประกอบการเรียนการสอน"
        }
    },

    "event": {
        "label": "🎉 ประชาสัมพันธ์กิจกรรม",
        "description": "เหมาะสำหรับงานสัมมนา งานประกวด แคมเปญ และกิจกรรมพิเศษ",
        "form_fields": [
            "topic",
            "keyword",
            "event_name",
            "organizer_name",
            "event_objective",
            "date_time_location",
            "event_highlights",
            "attendee_benefits",
            "registration_channel",
            "tone"
        ],
        "prompt_strategy": {
            "role": "Event Marketer & Campaign PR Consultant",
            "focus": ["Excitement", "Clarity", "Urgency", "Call-to-Registration"],
            "rules": [
                "สร้างความตื่นเต้น น่าสนใจ และชี้จุดเด่นของงานอีเวนต์ให้น่าเข้าร่วม",
                "บอกรายละเอียดที่ชัดเจน ครบถ้วน (วัน เวลา สถานที่ ช่องทางจองบัตร/ลงทะเบียน)",
                "เน้นการชูผลประโยชน์หรือสิ่งที่ผู้เข้าร่วมจะได้รับจากการสละเวลามางาน",
                "ใช้น้ำเสียงกระฉับกระเฉง เชื้อเชิญ และเป็นกันเองกับกลุ่มเป้าหมาย",
                "สร้างแฮชแท็กที่เกี่ยวกับกิจกรรม ชื่องาน และการลงทะเบียนประชาสัมพันธ์จำนวน 5-8 รายการ ปลอดภัยจาก HTML tags"
            ]
        },
        "outputs": {
            "seo_article": "📰 ข่าวประกาศกิจกรรม (Event Announcement)",
            "facebook_post": "📘 โพสต์เชิญชวนจองสิทธิ์ (Event PR)",
            "tiktok_script": "🎵 สคริปต์สั้นชวนลงทะเบียน (TikTok)",
            "youtube_script": "🔴 สคริปต์ไฮไลท์ภาพงานอีเวนต์ (YouTube)",
            "image_prompt": "🎨 ภาพโปสเตอร์กิจกรรม"
        }
    },

    "personal_brand": {
        "label": "👤 Personal Brand",
        "description": "เหมาะสำหรับผู้เชี่ยวชาญ โค้ช ที่ปรึกษา และผู้ที่ต้องการสร้างความน่าเชื่อถือ",
        "form_fields": [
            "topic",
            "keyword",
            "expert_niche",
            "target_followers",
            "experience_story",
            "core_identity",
            "key_takeaway",
            "tone",
            "cta"
        ],
        "prompt_strategy": {
            "role": "Executive Personal Branding Coach & Storyteller",
            "focus": ["Thought Leadership", "Authenticity", "Expert Positioning", "Storytelling"],
            "rules": [
                "เน้นการเล่าเรื่องผ่านประสบการณ์จริง (Storytelling) มีความน่าสนใจตั้งแต่ย่อหน้าแรก",
                "วางบทบาทให้ผู้เขียนเป็นผู้นำทางความคิด (Thought Leadership) ในสาขานั้นอย่างถ่อมตัวแต่เปี่ยมด้วยความรู้",
                "เขียนด้วยน้ำเสียงที่เป็นธรรมชาติ เป็นกันเอง มีความเข้าอกเข้าใจ และน่าเชื่อถือ (Authentic)",
                "ให้ข้อคิดหรือความรู้ที่มีคุณค่าแก่ผู้ติดตาม (Key Takeaway) โดยไม่โฆษณาบริการหรือขายของโต้งๆ",
                "สร้างแฮชแท็กสร้างตัวตน ความรู้ และทัศนคติจำนวน 5-8 รายการ ปลอดภัยจาก HTML tags"
            ]
        },
        "outputs": {
            "seo_article": "📰 บทความสร้างความน่าเชื่อถือ (Thought Leadership Article)",
            "facebook_post": "📘 โพสต์สไตล์บอกเล่าเรื่องราว (Story Post)",
            "tiktok_script": "🎵 สคริปต์แบ่งปันมุมมองโค้ช (TikTok)",
            "youtube_script": "🔴 สคริปต์สั้นถอดบทเรียนชีวิต (YouTube)",
            "image_prompt": "🎨 ภาพประกอบสร้างแบรนด์ตัวบุคคล"
        }
    }
}
