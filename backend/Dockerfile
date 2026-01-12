FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev python3-dev pkg-config \
    libffi-dev libssl-dev \
    libjpeg62-turbo zlib1g libpng16-16 libfreetype6 \
  && rm -rf /var/lib/apt/lists/*



WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

EXPOSE 8000

RUN sed -i 's/\r$//' auto-migrate.sh && chmod +x auto-migrate.sh

ENTRYPOINT ["./auto-migrate.sh"]
CMD ["uv", "run", "uvicorn", "app.main:app", "--host","0.0.0.0","--port","8000", "--proxy-headers","--forwarded-allow-ips=*"]
