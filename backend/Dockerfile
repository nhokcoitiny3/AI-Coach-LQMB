# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN --mount=type=cache,id=lien-quan-pip-cache,target=/root/.cache/pip \
    python -m venv /venv && /venv/bin/pip install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
ENV PATH="/venv/bin:$PATH" PYTHONPATH=/app PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=builder /venv /venv
COPY . .
RUN addgroup --system app && adduser --system --ingroup app app && mkdir -p /app/uploads && chown -R app:app /app
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
