FROM python:3.9-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg wget && rm -rf /var/lib/apt/lists/*
RUN wget -O /usr/local/bin/yt-dlp https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py .
CMD ["python","-u","bot.py"]