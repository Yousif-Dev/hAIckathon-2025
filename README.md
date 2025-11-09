uv run uvicorn src.backend_api.fast_api_server:app --host 0.0.0.0
docker run -p 8000:8000 haickathon-2025
To sync uv's toml to requirements.txt:
uv pip compile pyproject.toml -o requirements.txt