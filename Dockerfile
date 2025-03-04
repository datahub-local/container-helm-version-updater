FROM python:3.12-slim AS builder
WORKDIR /app
ADD requirements.txt /app
RUN pip install --target=/app -r requirements.txt
ADD update_versions /app/update_versions

FROM gcr.io/distroless/python3-debian12

COPY --from=builder /app /app

WORKDIR /app
ENV PYTHONPATH=/app
