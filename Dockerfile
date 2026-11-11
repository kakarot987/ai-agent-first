FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY setup.py pyproject.toml README.md ./
COPY src/ ./src/
RUN python -m pip install --no-cache-dir .

RUN useradd --create-home --shell /bin/sh agent \
    && mkdir -p /app/conversations \
    && chown -R agent:agent /app/conversations
USER agent

CMD ["ai-agent", "chat"]
