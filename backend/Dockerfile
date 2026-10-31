FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app


# System dependencies + CA certificate store
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# Non-root user
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser


COPY requirements.txt .


RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app
COPY entrypoint.sh .


RUN chmod +x /app/entrypoint.sh \
    && chown -R appuser:appgroup /app


USER appuser


EXPOSE 8000


ENTRYPOINT ["/app/entrypoint.sh"]