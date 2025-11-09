# Haickathon 2025 - Backend API
This repository contains the backend API for the Haickathon 2025 event. The API is built using FastAPI and is designed to handle various functionalities required for the event, mainly talking to different APIs & light number crunching.

## Setup Instructions
Make sure you have UV installed. You are able to then create a virtual environment and install dependencies using the following commands:'

```bash
uv sync
```
This will create a virtual environment and install all necessary dependencies as specified in the `pyproject.toml` file.

##  Running the API
You will need to set some environment variables for the API to function correctly. You can create a `.env` file in the root directory of the project and add the necessary variables there. Follow .env.template.
After setting up the environment variables, you can run the API using Uvicorn with the following command:

```bash
uv run uvicorn src.backend_api.fast_api_server:app --host 0.0.0.0
```

If you prefer to use Docker, you can build the Docker image and run the container with the following commands:

```bash
docker build -t haickathon-2025 .
docker run -p 8000:8000 haickathon-2025
```

##  Deployment
We used Render to deploy the backend API. The deployment process is automated through Render's integration with GitHub, allowing for seamless updates whenever changes are pushed to the main branch.
For this, you have to set the same environment variables in Render as you did in your local `.env` file. You also need a requirements.txt file, which can be generated from the `pyproject.toml` using UV's pip compile command:

```bash
uv pip compile pyproject.toml -o requirements.txt
```
