FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 curl git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs
RUN cd wheat-frontend && npm install && npm run build-only


ENV FLASK_ENV=production
ENV PORT=5000

# Railway auto-assigns PORT env

COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD /start.sh


