# Sprint 16 Instagram Carousel Implementation Report

This document reports on the design choices, architectural integration, and implementation details of the new Instagram Carousel Blueprint MVP.

---

## 1. Design & Mapping Decisions

To maintain absolute production stability and prevent database schema migrations or spreadsheet updates, we devised an elegant mapping system to reuse existing storage layouts:

1.  **Slide Outputs (Slide 1–6):** Stored inside the existing `article_html` column (Column R). Prompt directives instruct Gemini to structure slides cleanly as HTML heading/paragraph formats:
    ```html
    <h2>Slide 1: Hook</h2>
    <p>3 นิสัยทำลายการเงินของคนรุ่นใหม่</p>
    ```
    On rendering, `strip_html_tags` strips HTML markers, resulting in clean, copy-friendly text block outputs inside the Streamlit copyable code container.
2.  **Caption & Hashtags:** Stored inside the existing `facebook_post` and `facebook_hashtags` columns (Columns Y and Z). Prompt directives instruct Gemini to write an Instagram-style Caption instead of a generic Facebook post.
3.  **Bonus social scripts:** The TikTok and YouTube scripts remain populated as optional video/Shorts scripts.

---

## 2. Integrated Code Paths

*   **Config Dictionary:** Added the `"instagram_carousel"` config inside [`config/content_blueprints.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/config/content_blueprints.py):
    *   Form fields: `topic`, `keyword`, `target_audience`, `core_story`, `key_insight`, `tone`, `cta`.
    *   Output labels mapping: `"seo_article" -> "📸 Instagram Slides (1-6)"`, `"facebook_post" -> "📝 IG Caption & Hashtags"`.
*   **System Prompt:** Added custom conditional rules inside [`prompts/blogger_seo_prompt.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/prompts/blogger_seo_prompt.py) for target formatting if `content_type == "instagram_carousel"`.
*   **Form inputs UI:** Injected form blocks for `"instagram_carousel"` inside both Demo Mode (line 766) and Credits/Queue Mode (line 1202) of [`web_app.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/web_app.py).
*   **Field Mapping Labels:** Mapped display names for `core_story` and `key_insight` in [`services/blueprint_service.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/services/blueprint_service.py).
