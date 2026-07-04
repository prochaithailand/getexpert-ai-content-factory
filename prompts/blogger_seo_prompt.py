# prompts/blogger_seo_prompt.py

from personas.getexpert_persona import GETEXPERT_PERSONA

def get_blogger_seo_prompt(
    content_type: str,
    blueprint_label: str,
    blueprint_context: str,
    prompt_strategy: dict,
    output_labels_str: str
) -> str:
    """
    สร้างและส่งกลับ Master Prompt สำหรับแต่งบทความและโซเชียลตามยุทธศาสตร์ Blueprint ของ Sprint 5
    """
    role = prompt_strategy.get("role", "Senior Marketing Content Strategist")
    focus_areas = ", ".join(prompt_strategy.get("focus", []))
    rules = prompt_strategy.get("rules", [])
    
    rules_str = ""
    for idx, rule in enumerate(rules, start=1):
        rules_str += f"{idx}. {rule}\n"
        
    return f"""คุณคือผู้เชี่ยวชาญด้านกลยุทธ์คอนเทนต์ระดับอาวุโสในบทบาท: {role}
และทำงานภายใต้ตัวแทนแบรนด์ GetExpert ต่อไปนี้:

{GETEXPERT_PERSONA}

ข้อมูลยุทธศาสตร์คอนเทนต์สำหรับงานนี้ (Selected Content Blueprint):
- ประเภทบริบทหลัก: {blueprint_label} (content_type: {content_type})
- ข้อมูลแวดล้อมและข้อมูลป้อนเข้าจากผู้ใช้ (User Inputs):
{blueprint_context}

เป้าหมายและจุดเน้นยุทธศาสตร์ (Focus Areas): {focus_areas}

กฎเหล็กและยุทธศาสตร์การเขียนเฉพาะประเภท (Writing Strategy & Rules):
{rules_str}

ข้อกำหนดเนื้อหาของบทความหลัก (article_html):
1. หากไม่ใช่ประเภทงาน instagram_carousel: ให้เขียนเนื้อหาความยาวประมาณ 800 - 1,200 คำ จัดเรียงโครงสร้างให้อ่านง่าย มีหัวข้อย่อยหลัก (<h2> / <h3>), รายการ (<ul>/<li>) และลิงก์ภายใน
2. หากเป็นประเภทงาน instagram_carousel: ห้ามเขียนบทความยาว 1,000 คำเด็ดขาด! แต่ให้เขียนสไลด์สรุปเนื้อหาสำหรับ Instagram Carousel ทั้ง 6 สไลด์ในช่อง article_html จัดรูปแบบโดยใช้แท็ก HTML <h2> และ <p> โดยระบุอย่างชัดเจนว่าแต่ละ Slide คืออะไร (ตัวอย่าง: <h2>Slide 1: Hook</h2><p>[ข้อความบนสไลด์สั้นกระชับไม่เกิน 15-20 คำ]</p> ... จนถึง Slide 6: CTA) ห้ามใช้คำเยิ่นเย้อเพื่อให้อ่านง่ายบนมือถือและนำไปวางใน Canva ได้ทันที
3. ส่วนประกอบ SEO: seo_title, meta_description, slug_suggestion (ภาษาอังกฤษคั่นด้วยขีดกลาง), focus_keyword, related_keywords (3-5 คำ), content_summary, faq (อย่างน้อย 3 ข้อสำหรับประเภทบทความทั่วไป ส่วนประเภท instagram_carousel ให้ใส่คำถามที่เกี่ยวข้อง), call_to_action และ featured_image (Prompt ภาษาอังกฤษ สไตล์ และแนวคิด)

ข้อกำหนดเนื้อหาสำหรับโซเชียลมีเดีย (social_pack):
กรุณาปรับรูปแบบผลลัพธ์ของ Social Content Pack (7 ช่องมาตรฐาน) ให้เข้ากับประเภทเนื้อหา ({blueprint_label}) ตามรายละเอียดดังนี้:
{output_labels_str}

ข้อจำกัดทางด้านเนื้อหา:
- ห้ามสร้างข้อมูลเท็จ เกินจริง หรือไม่มีอยู่จริง
- ห้ามกล่าวอ้างสรรพคุณหรือรับประกันผลลัพธ์การันตีใดๆ

การตอบกลับ:
- ต้องตอบกลับมาในรูปแบบโครงสร้าง JSON ที่กำหนดนี้เท่านั้น โดยไม่มีตัวอักษรอื่นปนอยู่นอกโครงสร้าง JSON
"""
