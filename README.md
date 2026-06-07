# avry-n8n

n8n workflow automation for the Aivory platform — self-hosted automation server with custom integrations.

## Tech Stack

- n8n (Node.js workflow engine)
- Docker
- Custom Python app modules

## Directory Structure

```
avry-n8n/
├── app/                    # Custom Python modules
├── n8n-as-code-service/    # n8n workflow definitions
└── docker-compose.yml
```

## Run Locally

n8n is Docker-based. Start with:

```bash
docker compose up --build
```

The service runs on port **5678**.

## VPS Deployment

```bash
docker compose -f docker-compose.yml up -d --build
```

Ensure `.env` is configured on the server with production credentials.

## Part of Aivory

This service is part of the [Aivory platform](https://github.com/ClementHansel/aivory).
