# Sprint 9 Rollback Plan

This rollback plan details the step-by-step procedure to revert user traffic from the self-hosted VPS trial environment back to the managed Streamlit Cloud production setup in the event of failure.

---

## 1. Trigger Conditions for Rollback

A rollback should be executed immediately if any of the following occur during the trial deployment:
*   **Websocket Connection Failures:** Users get stuck on the Streamlit "Connecting..." or "Connection timed out" screen on mobile devices.
*   **API Outage:** Google Sheets or Gemini API requests fail consistently due to SSL, network configuration, or memory limit issues.
*   **VPS Outage:** The Hostinger VPS server crashes or becomes unresponsive under concurrent load.

---

## 2. Step-by-Step Rollback Procedure

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│  1. Access DNS Console  ├────>│ 2. Modify CNAME Record  ├────>│  3. Save DNS Settings   │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
                                                                             │
┌─────────────────────────┐     ┌─────────────────────────┐     ┌────────────▼────────────┐
│  6. Validate Switchback │<────│  5. Monitor propagation │<────│   4. Clear Local Cache  │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

Follow these steps to redirect users back to the stable Streamlit Cloud environment:

### Step 1: Access DNS Provider Console
Log in to your DNS provider account (e.g., Cloudflare, GoDaddy, or Namecheap) where the domain `getexpert.biz` is managed.

### Step 2: Locate CNAME Record
Navigate to the DNS records table and locate the record for the subdomain:
*   **Type:** `CNAME`
*   **Name:** `app` (representing `app.getexpert.biz`)
*   **Current Target:** VPS IP address or alias.

### Step 3: Modify CNAME Target
Change the target value of the `app` CNAME record back to the Streamlit Cloud deployment:
*   **New Target:** `getexpert-ai-content-factory1.streamlit.app`
*   **TTL:** Set to `2 minutes` (or `Automatic` if using Cloudflare proxy).
*   **Cloudflare Proxy Status:** Set proxy status to `DNS only` or `Proxied` depending on previous configuration (reverting to Streamlit Cloud standard setup).

### Step 4: Save Record Changes
Click **Save** or **Update** to apply the changes.

---

## 3. Propagation & Validation Checks

1.  **Monitor DNS Propagation:** Open a terminal and run `nslookup` or `dig` to verify the DNS record has updated:
    ```bash
    nslookup app.getexpert.biz
    ```
    Confirm that the returned domain name points to Streamlit Cloud's servers.
2.  **Clear Local Cache:** On your mobile device, clear the browser cache or open an Incognito window.
3.  **End-to-End Test:** Open `https://app.getexpert.biz` on mobile. Verify that:
    - [ ] The app loads successfully.
    - [ ] The default Streamlit deploy toolbar/menu is visible at the top (confirming it is indeed the Streamlit Cloud environment).
    - [ ] Users can enter email, verify credit balance, and complete generations.
