#!/bin/bash

# 🚀 Start Web Demo - All-in-One Script
# This script starts both backend API and web server, then opens the browser

cd "$(dirname "$0")"

echo "🚀 Starting The Placement Gambit Web Demo..."
echo ""

# Kill any existing servers on these ports
echo "🧹 Cleaning up existing servers..."
pkill -f "python.*api.main" 2>/dev/null
pkill -f "python.*http.server.*8080" 2>/dev/null
sleep 2

# Start Backend API in background
echo "🔧 Starting Backend API on port 8000..."
python3 -m api.main > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend API is running!"
else
    echo "❌ Backend API failed to start. Check /tmp/backend.log"
    exit 1
fi

# Start Web Server in background
echo "🌐 Starting Web Server on port 8080..."
python3 -m http.server 8080 > /tmp/webserver.log 2>&1 &
WEBSERVER_PID=$!
echo "   Web Server PID: $WEBSERVER_PID"

# Wait for web server
sleep 2

echo ""
echo "✅ All servers started successfully!"
echo ""
echo "📊 Server Status:"
echo "   Backend API:  http://localhost:8000"
echo "   Web Server:   http://localhost:8080"
echo "   Planogram:    http://localhost:8080/demo/planogram_final.html"
echo ""
echo "📝 Logs:"
echo "   Backend:      /tmp/backend.log"
echo "   Web Server:   /tmp/webserver.log"
echo ""
echo "🛑 To stop servers: pkill -f python"
echo ""

# Open browser
echo "🌐 Opening planogram in browser..."
sleep 2
open http://localhost:8080/demo/planogram_final.html 2>/dev/null || \
    xdg-open http://localhost:8080/demo/planogram_final.html 2>/dev/null || \
    echo "   Please open: http://localhost:8080/demo/planogram_final.html"

echo ""
echo "✨ Demo is ready! Enjoy! ✨"
echo ""
echo "Press Ctrl+C to stop (or run: pkill -f python)"
echo ""

# Keep script running so user can see output
wait
