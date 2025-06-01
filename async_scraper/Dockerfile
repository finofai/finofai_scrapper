FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
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
  && rm -f google-chrome-stable_current_amd64.deb

ENV TZ=Asia/Kolkata

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run the script every 6 hours in an infinite loop
#CMD ["sh", "-c", "while true; do python /app/business-standard.py; sleep 21600; done"]
CMD ["tail", "-f", "/dev/null"]
