FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /srv/evospec

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && python -m playwright install --with-deps chromium \
 && rm -rf /var/lib/apt/lists/*

COPY . .

# Railway define PORT; localmente usa 8000
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 4 --timeout 180 web:app
