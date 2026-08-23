FROM python:3.10-slim

# Install system dependencies required by OpenCV and image processing
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create and switch to non-root user required by Hugging Face Spaces
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Install Python requirements
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application files
COPY --chown=user:user . .

# Expose standard Hugging Face port
EXPOSE 7860

# Support dynamic port assignment from Render/Cloud Run/Railway ($PORT) with fallback to 7860
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-7860}"]
