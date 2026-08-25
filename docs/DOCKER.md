# MuleShield PRO V2 - Containerization

Docker Compose configuration for local development and deployment.

## Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | Next.js dashboard |
| api | 8000 | Flask API gateway |
| ml-service | 8080 | ML inference service |
| graph-service | 8081 | Transaction graph analysis |
| reporting-service | 8082 | PDF report generation |
| postgres | 5432 | PostgreSQL database |

## Quick Start

```bash
# Copy environment configuration
cp .env.example .env

# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

## Prerequisites

- Docker Engine 24+
- Docker Compose v2.20+
- 4 GB available disk space

## First-Time Setup

```bash
# 1. Clone repository
git clone https://github.com/Ashwinkumar-k10/Muleshield-Fraud-Dedection.git
cd Muleshield-Fraud-Dedection

# 2. Configure environment
cp .env.example .env
# Edit .env to set secure passwords

# 3. Launch stack
docker compose up -d --build

# 4. Verify health
docker compose ps

# 5. Open dashboard
# Frontend: http://localhost:3000
# API: http://localhost:8000/health
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| POSTGRES_USER | muleshield | Database username |
| POSTGRES_PASSWORD | muleshield_secure | Database password (required) |
| POSTGRES_DB | muleshield_db | Database name |
| DATABASE_URL | postgresql://... | Full connection string |
| JWT_SECRET_KEY | change-me-in-production | JWT signing secret |
| NEXT_PUBLIC_API_URL | http://localhost:8000 | Frontend API base URL |

## Volumes

- `pgdata`: PostgreSQL persistent storage
- `./modeling:/app/modeling:ro`: Model artifacts (read-only)
- `./data:/app/data:ro`: Dataset files (read-only)

## Health Checks

All services expose health endpoints:

```bash
curl http://localhost:8000/health
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
```

## Troubleshooting

```bash
# View service logs
docker compose logs -f api
docker compose logs -f ml-service

# Rebuild after code changes
docker compose up -d --build api

# Reset database volume
docker compose down -v
docker compose up -d

# Shell into container
docker compose exec api bash
docker compose exec ml-service bash
```

## Production Notes

- Change `JWT_SECRET_KEY` and `POSTGRES_PASSWORD`
- Remove volume mounts for modeling/data and COPY into images
- Add reverse proxy (nginx/traefik) for TLS termination
- Configure resource limits per service
- Enable Docker secrets for credentials
