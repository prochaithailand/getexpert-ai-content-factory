# patch_streamlit.py
# GTM integration script to inject Google Tag Manager into Streamlit index.html template.
import os
import streamlit

# Locate static index.html
streamlit_dir = os.path.dirname(streamlit.__file__)
index_path = os.path.join(streamlit_dir, 'static', 'index.html')

if not os.path.exists(index_path):
    raise FileNotFoundError(f"Streamlit index.html not found at: {index_path}")

print(f"Found Streamlit index.html at: {index_path}")

with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# GTM Container ID
gtm_id = "GTM-TGJG5ZPT"

# GTM head script
gtm_head = f"""<!-- Google Tag Manager (GTM integration) -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{gtm_id}');</script>
<!-- End Google Tag Manager -->"""

# GTM body script
gtm_body = f"""<!-- Google Tag Manager (noscript) (GTM integration) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm_id}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->"""

# Insert head script right after <head>
if gtm_head not in html:
    html = html.replace("<head>", f"<head>\n    {gtm_head}")
    print("Injected GTM head script.")
else:
    print("GTM head script already present.")

# Insert body script right after <body>
if gtm_body not in html:
    html = html.replace("<body>", f"<body>\n    {gtm_body}")
    print("Injected GTM body script.")
else:
    print("GTM body script already present.")

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Streamlit index.html patched successfully!")
