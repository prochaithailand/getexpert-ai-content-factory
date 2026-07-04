# services/blueprint_service.py

from config.content_blueprints import CONTENT_BLUEPRINTS

class BlueprintService:
    """
    บริการจัดการ AI Content Blueprints คอยควบคุมกติกา ฟิลด์ ฟอร์ม และ Prompt Strategy ตามประเภทงาน
    """
    
    @staticmethod
    def get_all_blueprints() -> dict:
        """
        ดึงข้อมูล Blueprint ทั้งหมดที่มีในระบบ
        """
        return CONTENT_BLUEPRINTS

    @staticmethod
    def get_blueprint(content_type: str) -> dict:
        """
        ดึงข้อมูล Blueprint รายตัว โดยจะ Fallback กลับไปหา 'business' หากระบุคีย์ไม่ถูกต้อง
        """
        if not content_type or content_type not in CONTENT_BLUEPRINTS:
            return CONTENT_BLUEPRINTS["business"]
        return CONTENT_BLUEPRINTS[content_type]

    @staticmethod
    def get_form_fields(content_type: str) -> list:
        """
        ดึงข้อมูลรายการฟิลด์ฟอร์มของแต่ละประเภท
        """
        bp = BlueprintService.get_blueprint(content_type)
        return bp.get("form_fields", [])

    @staticmethod
    def get_output_types(content_type: str) -> dict:
        """
        ดึงประเภทผลลัพธ์แสดงผล (Output Labels)
        """
        bp = BlueprintService.get_blueprint(content_type)
        return bp.get("outputs", {})

    @staticmethod
    def get_output_requirements_description(content_type: str) -> str:
        """
        คำอธิบายการแมปป้อนผลลัพธ์โซเชียลมีเดียใน JSON เพื่อส่งต่อให้ Gemini เขียนข้อมูลให้ถูกประเภทงาน
        """
        bp = BlueprintService.get_blueprint(content_type)
        outputs = bp.get("outputs", {})
        
        desc = ""
        desc += f"1. facebook_post: เขียนข้อความสำหรับโพสต์ลงโซเชียลหลัก (เช่น Facebook/LinkedIn/Twitter) ในหัวข้อ: {outputs.get('facebook_post', 'Social Post')}\n"
        desc += f"2. facebook_hashtags: แฮชแท็กที่เหมาะสม 5-10 ตัว\n"
        desc += f"3. tiktok_hook: ประโยคเปิดตัวคลิปสั้นดึงดูดสายตา 3 วินาทีแรก\n"
        desc += f"4. tiktok_script: สคริปต์สั้นบทพูดและแนวภาพสำหรับ: {outputs.get('tiktok_script', 'Short Video Script')}\n"
        desc += f"5. youtube_shorts_script: สคริปต์สั้นหรือแนวข้อความสั้นสำหรับ: {outputs.get('youtube_script', 'Video Script')} (จัดรูปแบบขึ้นบรรทัดใหม่เว้นระยะห่างระหว่างแต่ละฉาก [Scene] หรือฉากบทพูดแต่ละฉากให้ชัดเจนและเว้นวรรคกว้างเพื่อให้อ่านง่ายบนมือถือ)\n"
        desc += f"6. youtube_title: หัวแนะนำชื่อคลิปวิดีโอหรือหัวข้อสั้นที่เกี่ยวข้อง\n"
        desc += f"7. youtube_description: คำอธิบายประกอบสรุปความยาวไม่เกิน 150 คำ"
        return desc

    @staticmethod
    def build_blueprint_context(content_type: str, user_inputs: dict) -> str:
        """
        สร้างและรวมข้อมูลอินพุตไดนามิกของแต่ละ Blueprint ให้กลายเป็นข้อความส่งต่อให้ Gemini เข้าใจบริบท
        """
        bp = BlueprintService.get_blueprint(content_type)
        fields = bp.get("form_fields", [])
        
        # ฟิลด์ป้ายชื่อภาษาไทยสำหรับสร้างโครงสร้างประมวลผล
        field_labels_map = {
            "topic": "หัวข้อหลัก",
            "keyword": "คำค้นหาหลัก / Focus Keyword",
            "business_name": "ชื่อธุรกิจ / สินค้า",
            "target_audience": "กลุ่มเป้าหมายลูกค้า / ผู้รับชม",
            "customer_problem": "ปัญหาหลักของลูกค้า",
            "unique_value": "จุดเด่น / จุดแข็งผลิตภัณฑ์",
            "marketing_goal": "เป้าหมายการสื่อสาร",
            "tone": "โทนน้ำเสียงการนำเสนอ",
            "cta": "ข้อความชวนดำเนินการ (CTA)",
            "agency_name": "ชื่อหน่วยงานรัฐ",
            "public_target": "ประชาชนกลุ่มเป้าหมาย",
            "project_objective": "วัตถุประสงค์โครงการ",
            "public_benefit": "ประโยชน์ที่ประชาชนจะได้รับ",
            "key_information": "ข้อมูลสำคัญที่ต้องแจ้ง",
            "contact_channel": "ช่องทางการติดต่อ / ลงทะเบียน",
            "campaign_name": "ชื่อโครงการเพื่อสังคม / CSR",
            "social_problem": "ปัญหาสังคมที่ต้องการแก้ไข",
            "affected_group": "กลุ่มเป้าหมายที่ได้รับผลกระทบ",
            "campaign_goal": "เป้าหมายแคมเปญ",
            "expected_impact": "ผลกระทบสังคมที่คาดหวัง",
            "participation_invite": "สิ่งที่อยากชวนประชาชนมาร่วมกัน",
            "organization_name": "องค์กรผู้ดำเนินการ",
            "institution_name": "ชื่อสถาบันการศึกษา / มหาวิทยาลัย",
            "learner_group": "ระดับชั้น / กลุ่มผู้เรียนรู้",
            "learning_objective": "วัตถุประสงค์การเรียนรู้",
            "core_knowledge": "สาระสำคัญทางการศึกษา",
            "expected_outcome": "ผลลัพธ์ของนักเรียนหลังจบบทเรียน",
            "content_format": "รูปแบบการสอนที่ชอบ",
            "event_name": "ชื่องานกิจกรรม / อีเวนต์",
            "organizer_name": "ผู้จัดงานกิจกรรม",
            "event_objective": "เป้าหมายการจัดงาน",
            "date_time_location": "วัน เวลา สถานที่จัดกิจกรรม",
            "event_highlights": "ไฮไลต์ / จุดเด่นของงานกิจกรรม",
            "attendee_benefits": "สิ่งที่ผู้ร่วมงานจะได้รับ",
            "registration_channel": "ช่องทางการลงทะเบียน",
            "expert_niche": "ความเชี่ยวชาญ / กลุ่มวิชาชีพของคุณ",
            "target_followers": "ผู้ติดตามที่คุณต้องการคุยด้วย",
            "experience_story": "ประสบการณ์สำคัญที่ต้องการบอกเล่า",
            "core_identity": "ภาพลักษณ์หรือจุดยืนแบรนด์บุคคล",
            "key_takeaway": "ข้อคิดที่ต้องการมอบให้ผู้ฟัง"
        }
        
        context_lines = []
        for field in fields:
            value = user_inputs.get(field, "")
            if hasattr(value, "strip"):
                value = value.strip()
            else:
                value = str(value).strip()
            if value:
                label = field_labels_map.get(field, field)
                context_lines.append(f"- {label} ({field}): {value}")
                
        return "\n".join(context_lines)
