FROM python:3.12-slim AS builder
WORKDIR /app
ADD requirements.txt /app
RUN pip install --target=/app -r requirements.txt
ADD src /app/src

FROM gcr.io/distroless/python3-debian12

COPY --from=builder /app /app

WORKDIR /app
ENV PYTHONPATH=/app
