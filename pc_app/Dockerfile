FROM debian:trixie

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip libgl1-mesa-dev libglib2.0 && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/

WORKDIR /app
COPY requirements.txt .

ENV UV_HTTP_TIMEOUT 500

RUN uv pip install -r requirements.txt --system --no-cache-dir --break-system-packages

COPY . .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python3", "-u", "pc-main.py"]
