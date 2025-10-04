#!/bin/bash
# Libral Core Production Startup Script
# 本番環境起動スクリプト

set -e

echo "🚀 Libral Core Production Startup"
echo "=================================="
echo ""

# 環境変数チェック
echo "📋 Checking environment variables..."
if [ -f .env ]; then
    echo "✅ .env file found, loading..."
    set -a
    source .env
    set +a
else
    echo "⚠️  .env file not found, using defaults"
fi

# Python環境確認
echo ""
echo "🐍 Checking Python environment..."
python --version
echo ""

# 依存関係確認
echo "📦 Checking dependencies..."
PYTHONPATH=. python -c "
import fastapi
import asyncpg
import redis
print('✅ All core dependencies available')
" || {
    echo "❌ Missing dependencies. Please run: pip install -r requirements.txt"
    exit 1
}

echo ""
echo "🏗️ Starting Libral Core Services..."
echo ""

# デフォルト設定
export PYTHONPATH=.
export DATABASE_URL=${DATABASE_URL:-"postgresql://localhost/libral_core"}
export REDIS_URL=${REDIS_URL:-"redis://localhost:6379"}

# 起動オプション
case "${1:-all}" in
    "main")
        echo "Starting Main Application (Port 8000)..."
        python main.py
        ;;
    
    "ai")
        echo "Starting AI Module (Port 8001)..."
        python -m libral_core.modules.ai.app
        ;;
    
    "app")
        echo "Starting APP Module (Port 8002)..."
        python -m libral_core.modules.app.app
        ;;
    
    "all")
        echo "⚠️  Note: 'all' mode starts Python backend services only."
        echo "   Frontend must be started separately:"
        echo "   - Development: npm run dev (from root directory)"
        echo "   - Production: npm run build && npm start (from root directory)"
        echo ""
        echo "Starting Python backend services in background..."
        echo ""
        
        # Create logs directory if it doesn't exist
        mkdir -p logs
        
        # Main Application
        echo "🔷 Starting Main Application (Port 8000)..."
        PYTHONPATH=. python main.py > logs/main.log 2>&1 &
        MAIN_PID=$!
        echo "   PID: $MAIN_PID"
        
        sleep 2
        
        # AI Module
        echo "🤖 Starting AI Module (Port 8001)..."
        PYTHONPATH=. python -m libral_core.modules.ai.app > logs/ai.log 2>&1 &
        AI_PID=$!
        echo "   PID: $AI_PID"
        
        sleep 2
        
        # APP Module
        echo "📱 Starting APP Module (Port 8002)..."
        PYTHONPATH=. python -m libral_core.modules.app.app > logs/app.log 2>&1 &
        APP_PID=$!
        echo "   PID: $APP_PID"
        
        sleep 3
        
        echo ""
        echo "✅ Python backend services started!"
        echo ""
        echo "📊 Service Status:"
        echo "   Main App:  http://localhost:8000/docs"
        echo "   AI Module: http://localhost:8001/docs"
        echo "   APP Module: http://localhost:8002/docs"
        echo ""
        echo "⚠️  Frontend NOT started - start separately:"
        echo "   cd .. && npm run dev"
        echo ""
        echo "📝 Logs:"
        echo "   Main:  logs/main.log"
        echo "   AI:    logs/ai.log"
        echo "   APP:   logs/app.log"
        echo ""
        echo "🛑 To stop all services:"
        echo "   kill $MAIN_PID $AI_PID $APP_PID"
        echo ""
        
        # Wait for user interrupt
        trap "echo ''; echo '🛑 Stopping all services...'; kill $MAIN_PID $AI_PID $APP_PID; exit 0" INT
        
        echo "Press Ctrl+C to stop all services..."
        wait
        ;;
    
    "test")
        echo "Running production tests..."
        echo ""
        
        # Test imports
        echo "1. Testing imports..."
        PYTHONPATH=. python -c "
from libral_core.modules.ai.service import LibralAI
from libral_core.modules.app.service import LibralApp
print('✅ All imports successful')
"
        
        # Test AI Module
        echo ""
        echo "2. Testing AI Module..."
        PYTHONPATH=. python tests/test_ai_module.py | grep -E "✅|❌|Tests passed" | tail -5
        
        # Test APP Module
        echo ""
        echo "3. Testing APP Module..."
        PYTHONPATH=. python tests/test_app_module.py | grep -E "✅|❌|Tests passed" | tail -5
        
        echo ""
        echo "🎉 Production tests completed!"
        ;;
    
    *)
        echo "Usage: $0 [main|ai|app|all|test]"
        echo ""
        echo "Options:"
        echo "  main  - Start Main Application only (Port 8000)"
        echo "  ai    - Start AI Module only (Port 8001)"
        echo "  app   - Start APP Module only (Port 8002)"
        echo "  all   - Start all services (default)"
        echo "  test  - Run production tests"
        exit 1
        ;;
esac
