FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN sed -i 's/Components: main/Components: main contrib/' \
        /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        smartmontools \
        util-linux \
        lm-sensors \
        zfsutils-linux \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 9111

CMD ["gunicorn", "--bind", "0.0.0.0:9111", "--workers", "1", "--threads", "4", "--timeout", "120", "--chdir", "src", "exporter:app"]
