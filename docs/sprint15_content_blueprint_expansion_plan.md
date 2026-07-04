# Sprint 15 Content Blueprint Expansion Plan

This document details the roadmap to expand Content Blueprints to satisfy user requests for social marketing and e-commerce descriptions.

---

## 1. Blueprint Request Backlog

During user trials, testers requested specialized copywriting formats. We have planned the integration of the following blueprints:

1.  **Instagram Carousel Blueprint (`instagram_carousel`):**
    *   *Purpose:* Visual storytelling carousel slides for IG.
    *   *Format:* 6-slide structure + caption + hashtags.
2.  **E-commerce Description Blueprint (`ecommerce_product`):**
    *   *Purpose:* High-conversion product listings for Shopee, Lazada, or TikTok Shop.
    *   *Inputs:* Product name, specs, unique selling points.
    *   *Outputs:* Product title, bullet benefits list, target customer pain points.
3.  **Google Maps Local SEO Article (`local_seo_post`):**
    *   *Purpose:* PR posts to increase Google Maps localized business rankings.
    *   *Inputs:* Store name, local keywords, coordinates/district description.

---

## 2. Dynamic UI Integration Path

To safely add these blueprints in subsequent sprints without breaking the current core python logic:

1.  **Define spec inside [`config/content_blueprints.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/config/content_blueprints.py):**
    *   Add `"instagram_carousel"` key mapping details (form fields, prompt strategy, outputs list).
2.  **Add Form Fields inside [`web_app.py`](file:///c:/AI%20Automate/getexpert-ai-content-factory/web_app.py):**
    *   Add an `elif selected_content_type == "instagram_carousel":` branch inside the Streamlit form block to render specific inputs.
3.  **Validate Output Mapping:**
    *   Ensure the output tabs map the new outputs dynamically.
