# services/notification_service.py
# Modular service to handle real-time LINE OA push notifications for important business events.
import urllib.request
import json
import logging
import time
from datetime import datetime
from config.settings import Settings

class NotificationService:
    @staticmethod
    def send_event_notification(event_name: str, email: str, package_name: str = None, credits: int = None):
        """
        Sends a real-time LINE OA push notification to the configured user ID.
        Retries once if the API request fails.
        """
        token = Settings.LINE_CHANNEL_ACCESS_TOKEN
        to_user = Settings.LINE_USER_ID
        
        if not token or not to_user:
            logging.info(f"[LINE Notification skipped] Settings not configured for event: {event_name}")
            return False
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build concise notification text (LINE buttons template limit is 160 chars)
        lines = [
            f"🔔 Event: {event_name}",
            f"📧 Email: {email}",
            f"⏰ Time: {timestamp}"
        ]
        if package_name:
            lines.append(f"📦 Package: {package_name}")
        if credits is not None:
            lines.append(f"💎 Credits: {credits}")
            
        message_text = "\n".join(lines)
        if len(message_text) > 160:
            # Fallback if somehow too long
            message_text = message_text[:157] + "..."
            
        # GTM / CEO Dashboard URL
        dashboard_url = "https://app.getexpert.biz"
        
        # Construct LINE Messaging API Template message payload
        payload = {
            "to": to_user,
            "messages": [
                {
                    "type": "template",
                    "altText": f"แจ้งเตือน: {event_name}",
                    "template": {
                        "type": "buttons",
                        "text": message_text,
                        "actions": [
                            {
                                "type": "uri",
                                "label": "เปิด Dashboard",
                                "uri": dashboard_url
                            }
                        ]
                    }
                }
            ]
        }
        
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = json.dumps(payload).encode('utf-8')
        
        # Helper function to perform post
        def perform_post():
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_code = response.getcode()
                res_body = response.read().decode('utf-8')
                return res_code, res_body

        # Try with one retry if failed
        for attempt in range(2):
            try:
                code, body = perform_post()
                if code == 200:
                    logging.info(f"[LINE Notification Success] Event: {event_name}")
                    return True
                else:
                    logging.warning(f"[LINE Notification Attempt {attempt+1} Failed] Status: {code}, Body: {body}")
            except Exception as e:
                logging.error(f"[LINE Notification Attempt {attempt+1} Error] {e}")
            
            # Wait 1s before retry
            if attempt == 0:
                time.sleep(1)
                
        logging.error(f"[LINE Notification Failed] Exhausted retries for event: {event_name}")
        return False
