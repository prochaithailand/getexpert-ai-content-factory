# utils/gtm.py
# Helper utility to push measurement events to Google Tag Manager (GTM) dataLayer in Streamlit.
import json
import logging
import streamlit.components.v1 as components

def push_event_to_gtm(event_name: str, parameters: dict = None):
    """
    Push an event and its parameters to the GTM dataLayer on the client browser.
    Log only the event name on the server to prevent PII exposure.
    """
    if parameters is None:
        parameters = {}
    
    # Sanitize parameter values to ensure they are JSON serializable
    safe_params = {}
    for k, v in parameters.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            safe_params[k] = v
        else:
            safe_params[k] = str(v)
            
    # Prepare dataLayer payload
    payload = {"event": event_name}
    payload.update(safe_params)
    
    payload_json = json.dumps(payload, ensure_ascii=False)
    
    # Generate inline JS script to execute in parent window (top-level document)
    js_code = f"""
    <script>
    try {{
        window.parent.dataLayer = window.parent.dataLayer || [];
        window.parent.dataLayer.push({payload_json});
        console.log("GTM Event Pushed:", {payload_json});
    }} catch (e) {{
        console.error("GTM Push Failed:", e);
    }}
    </script>
    """
    
    # Log only the event name on the server to protect privacy
    logging.info(f"GTM Event: {event_name}")
    
    # Render invisible component to execute the JavaScript in the browser
    components.html(js_code, height=0, width=0)
