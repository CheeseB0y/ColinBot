FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg
COPY . .
CMD ["python3", "bot.py"]