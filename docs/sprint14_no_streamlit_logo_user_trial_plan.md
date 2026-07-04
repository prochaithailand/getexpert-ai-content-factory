# Sprint 14 No-Streamlit-Logo User Trial Plan

This document maps the operational plan to recruit, onboarding, and audit real user trials specifically targeting the clean, no-Streamlit-logo interface on `https://app.getexpert.biz`.

---

## 1. Trial Focus & Metrics

The goal of this trial is to measure user trust and mobile usability improvements:

*   **Target Group:** 5–10 active users who have previously accessed the Streamlit Cloud version (`getexpert-ai-content-factory1.streamlit.app`).
*   **Key Metrics:**
    *   *Visual Cleanliness:* Do users notice that the Streamlit logo/deploy button is gone?
    *   *Credibility Score:* Does the custom domain and logo-free UI increase their perception of GetExpert AI as a professional, paid SaaS?
    *   *Checkout Completion:* Do users deplete free credits and follow the payment steps without getting confused by Streamlit's native reload loops?

---

## 2. Server Monitoring Procedures

To guarantee server stability during the trial:

### tail container logs
```bash
# Monitor generation logs and sheets updates
docker compose logs -f --tail=200
```

### tail Nginx access and error logs
Confirm WebSocket upgrades and check for connection dropouts:
```bash
tail -f /var/log/nginx/error.log
```

### Sheets database integrity
- [ ] Confirm user emails register.
- [ ] Verify content strategist pack history updates columns correctly.
