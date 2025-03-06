FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN apt-get update && apt-get install -y ffmpeg
ENV DISCORD_TOKEN=your_discord_token
ENV OPENAI_API_KEY=your_openai_key
ENV AWS_DEFAULT_REGION=your_aws_region
ENV AWS_ACCESS_KEY=your_aws_key
ENV AWS_SECRET_ACCESS_KEY=your_awk_secret_key
ENV BUCKET_NAME=your_bucket_name
ENV MONGODB_URI=your_mongodb_uri
ENV MONGODB_DB=your_mongodb_db
CMD ["python3", "bot.py"]