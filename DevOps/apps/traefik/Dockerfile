FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Add cron job
RUN echo "59 23 * * * /usr/local/bin/python /app/blacklist_updater.py >> /var/log/cron.log 2>&1" > /etc/cron.d/blacklist_updater
RUN chmod 0644 /etc/cron.d/blacklist_updater
RUN crontab /etc/cron.d/blacklist_updater

CMD ["cron", "-f"]
