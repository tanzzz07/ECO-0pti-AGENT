FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN groupadd --system app \
    && useradd --system --gid app --create-home app

COPY --chown=app:app . .

RUN mkdir -p backend/instance backend/reports/generated_pdfs \
    && chown -R app:app backend/instance backend/reports

USER app

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '7860') + '/ping', timeout=3)"

CMD ["gunicorn", "--chdir", "backend", "--workers", "1", "--threads", "4", "--timeout", "120", "--bind", "0.0.0.0:7860", "main:app"]
