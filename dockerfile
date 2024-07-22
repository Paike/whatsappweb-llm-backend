# temp stage
FROM python:3.12.2-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ["requirements.txt", "./"]

RUN pip install -r requirements.txt

COPY ["backend.py", "/app/"]

# final stage
FROM python:3.12.2-slim AS deploy 

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

COPY --from=builder /app ./

ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT ["/tini", "--"]
CMD ["python", "/app/backend.py"]