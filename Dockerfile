FROM python:3.10-slim

# Instala FFmpeg de forma nativa para evitar el error 500
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app", "-c", "gunicorn.conf.py"]
