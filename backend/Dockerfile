FROM python:3.12-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev
COPY app ./app
COPY scripts ./scripts
EXPOSE 8000
CMD ["bash", "-c", "uv run bash scripts/prestart.sh && uv run fastapi run app/main.py --port 8000 --host 0.0.0.0"]
