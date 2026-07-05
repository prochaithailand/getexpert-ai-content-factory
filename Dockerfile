# Step 1: Use lightweight Python 3.11 image
FROM python:3.11-slim

# Step 2: Set working directory inside container
WORKDIR /app

# Step 3: Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Copy dependency lists and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4.5: Inject Google Tag Manager (GTM) into Streamlit templates (GTM integration)
COPY patch_streamlit.py .
RUN python patch_streamlit.py

# Step 5: Copy the rest of application code
COPY . .

# Step 6: Expose the default Streamlit port
EXPOSE 8501

# Step 7: Configure Streamlit execution environment
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Step 8: Launch the application
CMD ["streamlit", "run", "web_app.py"]
