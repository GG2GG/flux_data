# Docker Quick Start Guide

## TL;DR

**Option 1: With your own API key (OpenAI/OpenRouter)**
```bash
cp .env.example .env
# Edit .env and add your API key
docker-compose up -d
```

**Option 2: Standalone with local LLM (no API keys needed)**
```bash
docker-compose -f docker-compose.ollama.yml up -d
```

Then visit: http://localhost:8000/docs

## Deployment Options

### 🔑 BYOM (Bring Your Own Model)

**Best for:** Production, fast responses, best quality

**Requirements:** OpenAI or OpenRouter API key

```bash
# 1. Configure
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY

# 2. Start
docker-compose up -d

# 3. Test
curl http://localhost:8000/api/health
```

**Recommended models:**
- `gpt-4o-mini` - Fast and cheap ($0.15 per 1M tokens)
- `anthropic/claude-3.5-sonnet` - Best quality (via OpenRouter)

---

### 🤖 Standalone with Ollama

**Best for:** Local development, offline use, privacy

**Requirements:** Docker only (no API keys)

```bash
# 1. Start (downloads model on first run)
docker-compose -f docker-compose.ollama.yml up -d

# 2. Wait for model download (~5-10 mins first time)
docker-compose -f docker-compose.ollama.yml logs -f ollama-setup

# 3. Test
curl http://localhost:8000/api/health
```

**Default model:** `deepseek-r1:latest` (8B parameters, ~5GB download)

**Change model:**
```bash
# In docker-compose.ollama.yml or .env
LLM_MODEL=llama3.1:latest

# Restart
docker-compose -f docker-compose.ollama.yml up -d
```

## Quick Commands

### Management

```bash
# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart after code changes
docker-compose up -d --build

# Check status
docker-compose ps
```

### Testing

```bash
# Run test script
./test-docker.sh

# Manual test
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Energy Drink",
    "category": "Beverages",
    "price": 2.99,
    "budget": 5000,
    "target_sales": 1000,
    "target_customers": "Young adults",
    "expected_roi": 1.5
  }'
```

### Ollama Management

```bash
# List downloaded models
docker-compose -f docker-compose.ollama.yml exec ollama ollama list

# Pull a different model
docker-compose -f docker-compose.ollama.yml exec ollama ollama pull llama3.1

# Remove a model
docker-compose -f docker-compose.ollama.yml exec ollama ollama rm deepseek-r1:latest
```

## Troubleshooting

### API won't start

```bash
# Check logs
docker-compose logs api

# Common issues:
# - Missing .env file → Copy from .env.example
# - Invalid API key → Check OPENAI_API_KEY in .env
# - Port 8000 in use → Change PORT in docker-compose.yml
```

### Ollama issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# View Ollama logs
docker-compose -f docker-compose.ollama.yml logs ollama

# Restart Ollama
docker-compose -f docker-compose.ollama.yml restart ollama

# Model download stuck → Increase timeout or pull manually:
docker-compose -f docker-compose.ollama.yml exec ollama ollama pull deepseek-r1:latest
```

### Empty responses from LLM

```bash
# Check LLM is configured
curl http://localhost:8000/api/health | jq .

# View detailed logs
docker-compose logs api | grep -i "llm\|error"

# Try different model
# Edit .env: LLM_MODEL=gpt-3.5-turbo
docker-compose restart api
```

## Performance Tips

### For BYOM
- Use `gpt-4o-mini` for best speed/cost ratio
- Set `LLM_MAX_TOKENS=500` for faster responses
- Lower `LLM_TEMPERATURE=0.5` for more consistent outputs

### For Ollama
- Use smaller models: `qwen2.5:1.5b` or `llama3.1:8b`
- Enable GPU if available (uncomment GPU section in docker-compose.ollama.yml)
- Increase RAM: Add `--memory=4g` to docker-compose

## Next Steps

- 📖 Full documentation: [DOCKER.md](./DOCKER.md)
- 🚀 API documentation: http://localhost:8000/docs
- 🔧 Configuration: See [.env.example](./.env.example)
- 🧪 Test API: Run `./test-docker.sh`

## Support

**Health check:** http://localhost:8000/api/health

**Common endpoints:**
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health
- Analyze: POST http://localhost:8000/api/analyze
- Defend: POST http://localhost:8000/api/defend

For issues, check logs with:
```bash
docker-compose logs -f
```
