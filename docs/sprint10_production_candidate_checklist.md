# Sprint 10 Production Candidate Checklist

This document details the checklist to audit system configurations on the self-hosted VPS, verify process daemons, and conduct end-to-end smoke testing before starting the controlled beta phase.

---

## 1. Host VPS Configuration Audits

### Container Policies
- [ ] **Docker Restart Policy:** Confirm `restart: always` is defined for both `app` and `worker` services inside `docker-compose.yml`.
- [ ] **Logs volume binding:** Verify host directory `./logs` exists, is writable, and contains recent application logs.
- [ ] **Worker stability:** Run `docker compose top worker` to verify the background python process `main.py` is actively polling.

### Nginx Proxy & Encryption
- [ ] **WebSocket Protocol:** Verify Nginx config includes `Upgrade` and `Connection` headers mapping.
- [ ] **Custom Timeouts:** Confirm `proxy_read_timeout` is set to `600s` to prevent connection breaks.
- [ ] **Certbot Timer:** Confirm Certbot auto-renew cron is active on host OS:
  ```bash
  sudo systemctl status certbot.timer
  ```

---

## 2. End-to-End User Flow Smoke Testing

Test the following user flows on `https://app.getexpert.biz`:

### A. Demo Mode Flow
- [ ] Open page, check that it loads instantly under 1.6s.
- [ ] Enter a test keyword and blueprint (e.g., Real Estate).
- [ ] Click generate; verify immediate results load in the browser.
- [ ] Inspect the 5 strategy output tabs and click copy button on code containers.

### B. Credit Gate & Trial Depletion Flow
- [ ] Verify credits eligibility verification button: Enter test email, click **🔍 ตรวจสอบเครดิตและสิทธิ์ใช้งาน**.
- [ ] Generate 3 consecutive Content Packs.
- [ ] Verify that on the 4th attempt, the application blocks generation and displays the **Payment Gate**.

### C. Payment Gate & LINE OA Redirect Flow
- [ ] Verify that the Payment QR Code fits the screen.
- [ ] Tap the green button **💬 เปิด LINE OA เพื่อส่งสลิป**:
  *   Confirm it redirects in the same tab (`target="_self"`).
  *   Verify it successfully redirects to `https://lin.ee/TZgX4CD`.
- [ ] Long-press the fallback URL block to verify it can be copied cleanly.

### D. Admin & Referral Commissions Flow
- [ ] Log in as admin, search for the test email.
- [ ] **Activate Partner:** Set the referral code to `PROCHAIT001`. Confirm validation triggers (no duplicates, no raw emails allowed).
- [ ] **Simulate Sale:** Select "แพ็กเริ่มต้น 99 บาท" and click deposit.
- [ ] Check Google Sheets:
  *   Confirm `Users` worksheet columns update (is_partner=TRUE, referral_link set).
  *   Confirm `Payments` worksheet logs the payment transaction.
  *   Confirm `Referral Logs` worksheet automatically records a **20 Baht** commission entry mapped to the referrer.
