# Docker Deployment Guide

This guide explains how to deploy the Retail Product Placement Agent using Docker.

## Quick Start

### Prerequisites
- Docker 20.10+ installed
- Docker Compose V2+ installed
- 4GB+ RAM available
- (Optional) NVIDIA Docker for GPU support with Ollama

### Option 1: BYOM (Bring Your Own Model) - Recommended for Production

Use this option if you have an OpenAI API key, OpenRouter key, or any external LLM API.

```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env and add your API key

# 2. Build and start services
docker-compose up -d

# 3. Check health
curl http://localhost:8000/api/health

# 4. Access API docs
open http://localhost:8000/docs
```

### Option 2: Standalone with Ollama - No API Keys Required

Use this option for local/offline deployment with included LLM.

```bash
# 1. Start services (includes Ollama)
docker-compose -f docker-compose.ollama.yml up -d

# 2. Wait for model download (first time only, ~5-10 minutes)
docker-compose -f docker-compose.ollama.yml logs -f ollama-setup

# 3. Check health
curl http://localhost:8000/api/health

# 4. Access API docs
open http://localhost:8000/docs
```

## Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

**For BYOM (OpenAI/OpenRouter):**
```env
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1500
```

**For Ollama (Local):**
```env
OPENAI_API_KEY=ollama
OPENAI_API_BASE=http://ollama:11434/v1
LLM_MODEL=deepseek-r1:latest
```

### Supported Models

**BYOM Options:**
- OpenAI: `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`
- OpenRouter: `anthropic/claude-3.5-sonnet`, `google/gemini-pro`, `meta-llama/llama-3-70b-instruct`

**Ollama Options:**
- `deepseek-r1:latest` (default, 8B parameters)
- `qwen2.5:latest` (7B parameters)
- `llama3.1:latest` (8B parameters)
- Any model from [Ollama Library](https://ollama.com/library)

## Docker Commands

### Basic Operations

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Remove everything including volumes
docker-compose down -v
```

### Ollama-Specific Commands

```bash
# Start with Ollama
docker-compose -f docker-compose.ollama.yml up -d

# Pull a different model
docker-compose -f docker-compose.ollama.yml exec ollama ollama pull llama3.1:latest

# List available models
docker-compose -f docker-compose.ollama.yml exec ollama ollama list

# Check Ollama logs
docker-compose -f docker-compose.ollama.yml logs ollama
```

### Troubleshooting

**Check service health:**
```bash
docker-compose ps
curl http://localhost:8000/api/health
```

**View API logs:**
```bash
docker-compose logs api -f
```

**Restart API only:**
```bash
docker-compose restart api
```

**Check Ollama connection:**
```bash
curl http://localhost:11434/api/tags
```

## Production Deployment

### Security Best Practices

1. **Use secrets management**
   ```bash
   # Don't commit .env to git
   echo ".env" >> .gitignore
   ```

2. **Set proper file permissions**
   ```bash
   chmod 600 .env
   ```

3. **Use reverse proxy (nginx/traefik)**
   ```yaml
   # Add to docker-compose.yml
   services:
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - ./certs:/etc/nginx/certs
   ```

4. **Enable HTTPS**
   - Use Let's Encrypt certificates
   - Configure SSL in reverse proxy

### Resource Limits

Add resource constraints in docker-compose.yml:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Monitoring

```bash
# View resource usage
docker stats

# Export metrics (Prometheus format)
curl http://localhost:8000/metrics
```

## GPU Support (Ollama)

For faster inference with Ollama:

1. Install NVIDIA Docker:
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

2. Uncomment GPU section in `docker-compose.ollama.yml`:
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]
   ```

3. Restart services:
   ```bash
   docker-compose -f docker-compose.ollama.yml up -d
   ```

## Data Persistence

### Volumes

The following directories are persisted:

- `./data` - Product, location, and computed metrics
- `./config` - Configuration files
- `ollama-data` - Ollama models (docker volume)

### Backup

```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Backup Ollama models
docker run --rm -v retail-ollama-data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-models.tar.gz /data
```

### Restore

```bash
# Restore data
tar -xzf backup-20250118.tar.gz

# Restore Ollama models
docker run --rm -v retail-ollama-data:/data -v $(pwd):/backup alpine tar xzf /backup/ollama-models.tar.gz -C /
```

## Performance Tuning

### API Optimization

```env
# Increase worker count (in Dockerfile or env)
UVICORN_WORKERS=4

# Adjust timeouts
UVICORN_TIMEOUT_KEEP_ALIVE=30
```

### Ollama Optimization

```bash
# Use smaller models for faster inference
LLM_MODEL=qwen2.5:1.5b

# Reduce max tokens for faster responses
LLM_MAX_TOKENS=500

# Increase temperature for more varied responses
LLM_TEMPERATURE=0.9
```

## Updating

### Update Application Code

```bash
git pull
docker-compose up -d --build
```

### Update Ollama Models

```bash
docker-compose -f docker-compose.ollama.yml exec ollama ollama pull deepseek-r1:latest
docker-compose restart api
```

## Logs and Debugging

### Enable Debug Logging

```env
LOG_LEVEL=debug
```

### Access Container Shell

```bash
# API container
docker-compose exec api /bin/bash

# Ollama container
docker-compose -f docker-compose.ollama.yml exec ollama /bin/bash
```

### Export Logs

```bash
docker-compose logs > logs-$(date +%Y%m%d-%H%M%S).txt
```

## Cost Optimization

### BYOM (API-based)
- Use `gpt-4o-mini` instead of `gpt-4o` (10x cheaper)
- Reduce `LLM_MAX_TOKENS` to minimum needed
- Cache responses when possible
- Set lower `LLM_TEMPERATURE` for more deterministic (cacheable) outputs

### Ollama (Local)
- Use smaller models (1.5B-7B parameters)
- Enable GPU for faster inference
- Batch requests when possible
- Consider CPU-only deployment for lower costs

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Health endpoint: `http://localhost:8000/api/health`
- API documentation: `http://localhost:8000/docs`
- GitHub Issues: [Your repo URL]
