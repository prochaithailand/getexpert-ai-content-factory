# utils/sanitize.py

import re

def strip_html_tags(html_text: str) -> str:
    """
    ล้างรหัส HTML tags ออกทั้งหมดเพื่อให้เหลือเฉพาะข้อความธรรมดา (Plain Text)
    """
    if not html_text:
        return ""
    # เปลี่ยนแท็กขึ้นบรรทัดใหม่ต่าง ๆ เป็น \n เพื่อรักษาโครงสร้างของย่อหน้า
    text = re.sub(r'</?(p|br|div|li|h1|h2|h3|h4|h5|h6)[^>]*>', '\n', html_text)
    # ลบแท็กอื่นๆ ที่เหลือ
    text = re.sub(r'<[^>]+>', '', text)
    # ลบ HTML entities ทั่วไป เช่น &nbsp;
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    # แทนที่การขึ้นบรรทัดใหม่ซ้ำๆ ให้เหลือบรรทัดว่าง 1 บรรทัด
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()
