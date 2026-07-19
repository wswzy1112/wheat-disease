FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 curl git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs
RUN cd wheat-frontend && npm install && npm run build

RUN mkdir -p /data/uploads

ENV PORT=7860
ENV DATABASE_URL=sqlite:////data/database.db
ENV UPLOAD_FOLDER=/data/uploads
ENV FLASK_ENV=production
ENV SECRET_KEY=please-change-me-in-production

EXPOSE 7860

COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD /start.sh
