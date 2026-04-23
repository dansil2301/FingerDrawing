FROM --platform=linux/arm64 python:3.11-slim-bookworm

WORKDIR /app

# System deps mediapipe needs on ARM
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.pi.txt .
RUN pip install --no-cache-dir -r requirements.pi.txt

COPY . .

CMD ["python", "main.py"]