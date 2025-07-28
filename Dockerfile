FROM python:3-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /cerebro

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd --system app && \
    useradd --system --no-create-home --gid app app && \
    chown -R app:app /cerebro

USER app

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "python3 manage.py migrate && \
                         python3 manage.py loaddata data.json && \
                         python3 manage.py runserver 0.0.0.0:8000"]
