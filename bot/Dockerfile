FROM python:3.14.2-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Copy bot source code
COPY bot/ ./bot/

# Install dependencies using uv (sync only bot package)
RUN uv sync --frozen --package lms-bot

# Run the bot
CMD ["uv", "run", "bot/bot.py"]
