FROM python:3.12

WORKDIR /app

# Install Google Chrome and its dependencies
RUN apt-get update && apt-get install -y \
    wget \
    cron \
    tzdata \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    fonts-liberation \
  && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
  && apt install -y ./google-chrome-stable_current_amd64.deb \
  && rm -f google-chrome-stable_current_amd64.deb \
  && rm -rf /var/lib/apt/lists/*

# Set timezone if you want cron logs to match Asia/Kolkata
ENV TZ=Asia/Kolkata

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your scraper and the crontab definition
COPY . .
COPY scraper-cron /etc/cron.d/scraper-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/scraper-cron \
    && crontab /etc/cron.d/scraper-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run cron in the foreground (so Docker doesn’t exit)
CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]
