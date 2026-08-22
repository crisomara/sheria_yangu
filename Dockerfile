FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py .
COPY main.py .
COPY agents/ agents/
COPY knowledge/ knowledge/
COPY mcp_tools/ mcp_tools/
COPY utils/ utils/

# GOOGLE_API_KEY (or OPENAI_API_KEY / OPENROUTER_API_KEY) is supplied at run time via
# -e / --env-file, never baked into the image. See .env.example for the full list.

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
