# Sprint 15 YouTube Blueprint Spacing Fix Report

This document reports the root cause audit, implementation details, and verification of the spacing optimization for the YouTube Shorts script output.

---

## 1. Root Cause Audit

*   **Identified Issue:** Users reported that generated YouTube Shorts scripts looked cluttered on mobile screens, lacking distinct lines or breaks between scene setups, audio transcripts, and visual directions.
*   **Analysis:** Gemini API returns text directly inside JSON strings. If the system prompt doesn't specify formatting rules, the LLM may output text blocks with dense styling.
*   **Sanitization impact:** `strip_html_tags` sanitizes inputs, converting `<p>` and `<br>` to `\n` and collapsing consecutive carriage returns into `\n\n`. Thus, any missing spacing originates directly from the Gemini generation output format.

---

## 2. Low-Risk Spacing Optimization

Rather than modifying string sanitization algorithms or introducing complex regex operations (which could break other outputs like Blogger articles), we resolved the spacing issue **at the prompt generation source** (prompt engineering).

We updated the instruction string inside [`services/blueprint_service.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/services/blueprint_service.py) (line 55):

```diff
-desc += f"5. youtube_shorts_script: สคริปต์สั้นหรือแนวข้อความสั้นสำหรับ: {outputs.get('youtube_script', 'Video Script')}\n"
+desc += f"5. youtube_shorts_script: สคริปต์สั้นหรือแนวข้อความสั้นสำหรับ: {outputs.get('youtube_script', 'Video Script')} (จัดรูปแบบขึ้นบรรทัดใหม่เว้นระยะห่างระหว่างแต่ละฉาก [Scene] หรือฉากบทพูดแต่ละฉากให้ชัดเจนและเว้นวรรคกว้างเพื่อให้อ่านง่ายบนมือถือ)\n"
```

---

## 3. Spacing Output Verification

The prompt instruction forces Gemini to output scripts using clear paragraph breaks. For example:

```
[ฉากที่ 1: หน้ากล้องโคลสอัพ]
บทพูด: "คุณเคยเงินเดือนหมดตั้งแต่สัปดาห์แรกของเดือนไหม?"
(แนวภาพ: พิธีกรชี้หน้ากล้องด้วยสีหน้าสงสัย)

[ฉากที่ 2: ภาพกราฟิกตารางเงินออม]
บทพูด: "ความจริงคือ เงินออมไม่ได้แปลว่าหาเงินได้เยอะ แต่แปลว่าคุณหักค่าใช้จ่ายคงที่ออกก่อนหรือยัง..."
```

This format renders cleanly in the Streamlit `st.code` block, resolving mobile visual clutter.
