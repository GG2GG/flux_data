#!/bin/bash

# Retail Product Placement Agent - Docker Startup Script

set -e

echo "🚀 Retail Product Placement Agent - Docker Startup"
echo "=================================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and configure your API keys if needed"
    echo ""
fi

# Check if Ollama is running on host
OLLAMA_RUNNING=false
if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
    OLLAMA_RUNNING=true
fi

# Ask user which deployment mode
echo "Select deployment mode:"
echo "1) BYOM - Bring Your Own Model (OpenAI/OpenRouter)"
if [ "$OLLAMA_RUNNING" = true ]; then
    echo "2) Use Host Ollama (detected running on localhost:11434)"
    echo "3) Standalone - With Ollama Container (will use port 11435)"
else
    echo "2) Standalone - With Ollama Container (Local LLM, no API keys needed)"
fi
echo ""
read -p "Enter choice [1, 2, or 3]: " choice

case $choice in
    1)
        echo ""
        echo "📦 Starting BYOM mode (external API)..."
        echo "Make sure you've configured your API keys in .env"
        echo ""
        docker-compose up -d --build
        COMPOSE_FILE="docker-compose.yml"
        ;;
    2)
        if [ "$OLLAMA_RUNNING" = true ]; then
            echo ""
            echo "📦 Using Host Ollama (localhost:11434)..."
            echo "Make sure you have the model pulled: ollama pull ${LLM_MODEL:-deepseek-r1:latest}"
            echo ""
            docker-compose -f docker-compose.host-ollama.yml up -d --build
            COMPOSE_FILE="docker-compose.host-ollama.yml"
        else
            echo ""
            echo "📦 Starting Standalone mode with Ollama..."
            echo "This will download the LLM model on first run (~5-10 minutes)"
            echo ""
            docker-compose -f docker-compose.ollama.yml up -d --build
            COMPOSE_FILE="docker-compose.ollama.yml"
        fi
        ;;
    3)
        if [ "$OLLAMA_RUNNING" = true ]; then
            echo ""
            echo "📦 Starting Ollama Container on port 11435..."
            echo "Note: Your host Ollama is on 11434, container will use 11435"
            echo ""
            # Modify port and start
            sed 's/11434:11434/11435:11434/' docker-compose.ollama.yml > docker-compose.ollama-alt.yml
            sed -i.bak 's|http://ollama:11434|http://ollama:11435|g' docker-compose.ollama-alt.yml
            docker-compose -f docker-compose.ollama-alt.yml up -d --build
            COMPOSE_FILE="docker-compose.ollama-alt.yml"
        else
            echo "❌ Invalid choice. Exiting."
            exit 1
        fi
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Wait for health check
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
        echo ""
        echo "✅ API is healthy!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -n "."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo ""
    echo "❌ API failed to start within expected time"
    echo "Check logs with: docker-compose logs -f"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ Retail Product Placement API is ready!"
echo "=================================================="
echo ""
echo "📍 API Endpoints:"
echo "   - Health: http://localhost:8000/api/health"
echo "   - Docs:   http://localhost:8000/docs"
echo "   - Analyze: POST http://localhost:8000/api/analyze"
echo "   - Defend:  POST http://localhost:8000/api/defend"
echo ""
echo "📊 Useful Commands:"
echo "   - View logs:    docker-compose -f $COMPOSE_FILE logs -f"
echo "   - Stop:         docker-compose -f $COMPOSE_FILE down"
echo "   - Restart:      docker-compose -f $COMPOSE_FILE restart"
echo "   - Status:       docker-compose -f $COMPOSE_FILE ps"
echo ""

if [ "$choice" = "2" ]; then
    echo "🤖 Ollama Info:"
    echo "   - Check models: docker-compose -f docker-compose.ollama.yml exec ollama ollama list"
    echo "   - Ollama logs:  docker-compose -f docker-compose.ollama.yml logs ollama"
    echo ""
fi

echo "🎉 Happy analyzing!"
