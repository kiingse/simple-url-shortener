FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install --no-cache-dir --upgrade poetry

COPY . .
COPY .env.test .env.test

RUN poetry config virtualenvs.create false
RUN poetry install --no-root

EXPOSE 8000

RUN chmod +x /app/docker/entrypoint.sh

ENTRYPOINT ["sh", "/app/docker/entrypoint.sh"]

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
