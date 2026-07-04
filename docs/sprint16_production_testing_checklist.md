# Sprint 16 Production Testing Checklist

This checklist verifies the readiness of the Instagram Carousel blueprint MVP on the live server (`https://app.getexpert.biz`).

---

## Production Verification Checklist

### 1. App Service Status
*   [ ] Verify the Streamlit portal is online at `https://app.getexpert.biz`.
*   [ ] Verify the queue worker container is running normally.
*   [ ] Verify fallback url `https://getexpert-ai-content-factory1.streamlit.app/?demo=true` loads.

### 2. Instagram Carousel Option Visibility
*   [ ] Open portal in Demo Mode. Confirm "📸 Instagram Carousel" appears in the Content Type radio options.
*   [ ] Input email with active credits. Confirm "📸 Instagram Carousel" appears in the Production Queue selector.

### 3. Input Field Display Check
*   [ ] Confirm the following inputs display correctly:
    - หัวข้อสไลด์หลัก
    - คำค้นหาหลัก
    - กลุ่มเป้าหมายผู้รับชม
    - แกนเรื่องเล่าที่ใช้โยงประเด็น
    - ข้อมูลเจาะลึกที่คนทั่วไปมักเข้าใจผิด
    - สไตล์น้ำเสียง
    - ข้อความปิดท้ายเชิญชวน (CTA)

### 4. Output Structure & Formatting
*   [ ] Verify the generated output contains 6 slides (Hook, Problem, Insight, Solution, Benefit, CTA).
*   [ ] Verify the Caption and Hashtags are formatted cleanly without HTML tag styling.
*   [ ] Verify slide outputs render in copyable raw text boxes inside Tab 1.

### 5. Regression Check on Existing Functions
*   [ ] Verify "📈 ธุรกิจ / สินค้า" blueprint still writes Blogger draft articles, Facebook posts, TikTok/YouTube scripts, and Image prompts.
*   [ ] Verify credit deduction subtracts 1 credit per successful generation.
*   [ ] Verify payment gate triggers once credit limit is reached.
*   [ ] Verify referred by code continues to capture query arguments.
*   [ ] Verify mobile layouts are clean and scroll fluidly.
