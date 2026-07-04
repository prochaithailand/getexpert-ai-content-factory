# Sprint 16 Manual Test Cases

This document maps step-by-step manual test cases to verify the Instagram Carousel blueprint MVP on `https://app.getexpert.biz`.

---

## Manual Test Cases

### TC-01: Demo Mode Content Generation
*   **Objective:** Confirm a guest user can generate Instagram Carousel slide packs.
*   **Steps:**
    1. Open a browser and navigate to `https://app.getexpert.biz/?demo=true`.
    2. Enter a test email in the registration email input field.
    3. Choose **"📸 Instagram Carousel"** from the radio options list.
    4. Fill in the input fields (leave defaults or write custom).
    5. Click the **"✨ สร้าง Content Pack"** button.
*   **Expected Outcome:**
    - The status box expands, showing generation progress.
    - Tab 1 displays "📸 Instagram Slides (1-6)" with the 6 slides cleanly separated.
    - Tab 2 displays "📝 IG Caption & Hashtags" with description text and hashtags.
    - No raw HTML tags are visible in the copyable code blocks.

---

### TC-02: Credit/Queue Mode & Deduction
*   **Objective:** Confirm credit billing logic is unchanged.
*   **Steps:**
    1. Enter an email with active credits (e.g., 5 credits).
    2. Verify the status message displays: `💎 บัญชีผู้ใช้งานระบบแบบโควตา (คุณเหลือเครดิต 5 Content Packs)`.
    3. Choose **"📸 Instagram Carousel"** and fill in inputs.
    4. Click **"ส่งคำขอเขียนและแพ็คคอนเทนต์ (Add to Queue)"**.
    5. Wait for the background worker to finish, then check credit balance.
*   **Expected Outcome:**
    - Credit balance decreases to 4.
    - Commission logs are recorded in Google Sheets if the account was referred.

---

### TC-03: Copyability & Formatting Verification
*   **Objective:** Confirm slide outputs are easy to paste into Canva/Instagram.
*   **Steps:**
    1. Go to the generated result under Tab 1 "📸 Instagram Slides (1-6)".
    2. Click the **Copy** button on the top-right corner of the code block.
    3. Open a notepad or Canva page and paste.
*   **Expected Outcome:**
    - Copied text is clean plain text.
    - Each slide is formatted with clear blank lines and scene labels.
