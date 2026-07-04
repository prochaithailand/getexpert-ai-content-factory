# Sprint 8 VPS, Nginx, & SSL Deployment Checklist

This checklist guides system administrators through configuring a clean Hostinger VPS, setting up UFW firewalls, configuring Nginx proxy routing with WebSocket support, installing SSL certificates, and preparing a rollback plan.

---

## 1. VPS Initial Setup
- [ ] Log in to your VPS via SSH as root user.
- [ ] Update repository listings and upgrade core libraries:
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```
- [ ] Install Docker and Docker Compose:
  ```bash
  sudo apt install docker.io docker-compose -y
  sudo systemctl enable --now docker
  ```
- [ ] Install Nginx and Git:
  ```bash
  sudo apt install nginx git -y
  ```

---

## 2. Firewall Protection (UFW)
- [ ] Permit SSH connection:
  ```bash
  sudo ufw allow 22/tcp
  ```
- [ ] Permit HTTP & HTTPS:
  ```bash
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  ```
- [ ] Explicitly block Streamlit port 8501 from the open internet to ensure users go through Nginx:
  ```bash
  sudo ufw deny 8501/tcp
  ```
- [ ] Enable firewall:
  ```bash
  sudo ufw enable
  ```

---

## 3. Nginx Reverse Proxy Configuration (With WebSockets)
Streamlit requires active WebSockets to keep state alive. Configure the site file `/etc/nginx/sites-available/app.getexpert.biz`:

```nginx
server {
    listen 80;
    server_name app.getexpert.biz;

    location / {
        proxy_pass http://127.0.0.1:8501;
        
        # Required headers for WebSocket support (Streamlit lifecycle)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Standard proxy parameters
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for long-running AI content pack generations
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }
}
```

- [ ] Enable the site configuration:
  ```bash
  sudo ln -s /etc/nginx/sites-available/app.getexpert.biz /etc/nginx/sites-enabled/
  ```
- [ ] Test syntax correctness:
  ```bash
  sudo nginx -t
  ```
- [ ] Reload Nginx to apply changes:
  ```bash
  sudo systemctl reload nginx
  ```

---

## 4. Let's Encrypt SSL Installation
- [ ] Install Certbot package:
  ```bash
  sudo apt install certbot python3-certbot-nginx -y
  ```
- [ ] Request SSL certificate for the domain:
  ```bash
  sudo certbot --nginx -d app.getexpert.biz
  ```
- [ ] Complete validation prompts. Certbot will automatically inject SSL parameters and redirect rules into the Nginx configuration.

---

## 5. Rollback Plan

If the self-hosted deployment encounters issues (e.g., performance degradation, database sync locks, or network outages), perform the following rollback immediately:

1.  **DNS Switchback:**
    *   Log in to your domain management console (DNS manager).
    *   Locate the CNAME record for `app.getexpert.biz`.
    *   Change the target back to the stable Streamlit Cloud URL (e.g. `getexpert-ai-content-factory1.streamlit.app`).
2.  **TTL Settings:** Ensure the TTL (Time-To-Live) on the DNS records is set to 300 seconds (5 minutes) before the migration, enabling rapid DNS switchback.
3.  **Audit Logs:** Leave the VPS running in debug mode to collect Nginx logs and Docker logs for audit analysis.
