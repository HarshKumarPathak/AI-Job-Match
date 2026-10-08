$ErrorActionPreference = "Stop"

Write-Host "Starting AI Job Match with Docker Compose..." -ForegroundColor Cyan
docker compose -f infra/docker/docker-compose.yml up --build
