# Sprint 15 Instagram Carousel Blueprint Specification

This document defines the specification sheet, parameters, Pydantic schemas, and prompts to build the new Instagram Carousel Blueprint.

---

## 1. Specification & Field Parameters

*   **Key ID:** `"instagram_carousel"`
*   **Label:** `"📸 Instagram Carousel"`
*   **Description:** `"เหมาะสำหรับสไลด์คอนเทนต์เล่าเรื่อง ทีละภาพปัดข้างสำหรับลง Instagram หรือ LinkedIn Carousel"`
*   **Form Input Fields:**
    1.  `topic`: หัวข้อเรื่องหลัก (เช่น 3 นิสัยทำลายการเงินของคนรุ่นใหม่)
    2.  `keyword`: คำค้นหาหลัก (เช่น การเงินส่วนบุคคล, วิธีเก็บเงิน)
    3.  `target_audience`: กลุ่มผู้ใช้เป้าหมาย (เช่น พนักงานจบใหม่ช่วงอายุ 22-26 ปี)
    4.  `core_story`: แกนเรื่องเล่าที่ใช้โยงประเด็น (เช่น จากคนที่เงินเดือนหมดตั้งแต่สัปดาห์ที่สอง)
    5.  `key_insight`: ข้อมูลเจาะลึกที่คนทั่วไปมักเข้าใจผิด (เช่น ความจริงคือเงินออมไม่ได้ขึ้นอยู่กับรายได้ แต่ขึ้นอยู่กับการตัดรายจ่ายประจำ)
    6.  `tone`: สไตล์น้ำเสียงน้ำคํา (เช่น เป็นกันเอง สนุกสนาน คล้ายเพื่อนเล่าให้เพื่อนฟัง)
    7.  `cta`: ข้อความปิดท้ายเชิญชวน (เช่น กดเซฟเก็บไว้ หรือแท็กเพื่อนเพื่อตักเตือนกัน)

---

## 2. Output Schema Definition (Pydantic / JSON)

The JSON structure returned by the Gemini API will map onto a dedicated Pydantic class:

```python
class InstagramCarouselPack(BaseModel):
    slide_1_hook: str = Field(description="หัวข้อสั้นสะดุดตาสำหรับสไลด์แรก (Slide 1: Hook)")
    slide_2_problem: str = Field(description="เล่าปัญหาหรือ Pain point ที่ขยี้ให้คนสนใจ (Slide 2: Problem)")
    slide_3_insight: str = Field(description="ให้แง่คิดเจาะลึกหรือเปิดประเด็นข้อมูลใหม่ (Slide 3: Insight)")
    slide_4_solution: str = Field(description="เสนอทางออกหรือคำแนะนำแนวทางปฏิบัติ (Slide 4: Solution)")
    slide_5_benefit: str = Field(description="สรุปคุณค่าหรือผลลัพธ์ที่จะได้รับ (Slide 5: Benefit)")
    slide_6_cta: str = Field(description="ป้าย CTA ชวนแชร์ กดติดตาม หรือสั่งซื้อ (Slide 6: Call to Action)")
    caption: str = Field(description="เนื้อหาแคปชั่นหลักสำหรับพิมพ์บรรยายใต้ภาพความยาว 100-200 คำ")
    hashtags: List[str] = Field(description="แฮชแท็กหลักสนับสนุนแบรนด์จำนวน 5-8 ตัว")
```
---

## 3. Gemini Prompt strategy rules
*   *Role:* Instagram Copywriter & Visual Storyteller.
*   *Rules:*
    1.  Keep text on slides extremely short (maximum 15-20 words per slide) to ensure readability when designed onto graphics.
    2.  Slide titles must be bold and catchy.
    3.  Caption must be engaging and expand on slide points.
