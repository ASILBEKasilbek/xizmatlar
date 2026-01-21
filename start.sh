#!/bin/bash
# Quick Start Script - Bot-ni tez ishga tushirish

echo "🚀 Xizmatlar Bot - Quick Start"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env fayli topilmadi!"
    echo "📝 .env.example-dan nusxa olinmoqda..."
    cp .env.example .env
    echo "✅ .env fayli yaratildi"
    echo ""
    echo "❗ MUHIM: .env faylini to'ldiring:"
    echo "   1. BOT_TOKEN (BotFather-dan)"
    echo "   2. ADMIN_IDS (Sizning Telegram ID)"
    echo "   3. CHANNEL_ID va GROUP_IDs"
    echo ""
    echo "Keyin qayta ishga tushiring: ./start.sh"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment yaratilmoqda..."
    python3 -m venv venv
    echo "✅ Virtual environment yaratildi"
fi

# Activate venv and install dependencies
echo "📚 Dependencies o'rnatilmoqda..."
source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Dependencies o'rnatildi"
echo ""

# Check BOT_TOKEN
source .env
if [ "$BOT_TOKEN" = "YOUR_BOT_TOKEN_HERE" ]; then
    echo "❌ BOT_TOKEN o'rnatilmagan!"
    echo "   .env faylida BOT_TOKEN ni to'ldiring"
    exit 1
fi

# Initialize database
echo "🗄️  Database yaratilmoqda..."
python3 -c "from database import init_db; init_db()" 2>/dev/null
echo "✅ Database tayyor"
echo ""

# Start bot
echo "🤖 Bot ishga tushmoqda..."
echo "   Ctrl+C bilan to'xtatish mumkin"
echo "================================"
echo ""
python main.py
