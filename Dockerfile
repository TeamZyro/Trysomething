FROM python:3.10-slim-bullseye

# Step 1: Install Curl and GPG
RUN apt-get update && \
    apt-get install -y --fix-missing \
    curl \
    gnupg2 \
    ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y --no-install-recommends --fix-missing \
    ffmpeg \
    aria2 \
    wkhtmltopdf \
    git \
    nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


COPY . /app/
WORKDIR /app/
RUN pip3 install --no-cache-dir -U -r requirements.txt

CMD bash start
