#!/bin/bash
# SCHNELLSTART - EINFACH UND FUNKTIONIERT!

echo "🚀 StreamWorks-KI - Schnellstart"
echo "================================"

# Cleanup alte Container
docker compose -f docker-compose.simple-db.yml down 2>/dev/null || true

# Starte nur DB
echo "📦 Starte PostgreSQL..."
docker compose -f docker-compose.simple-db.yml up -d postgres

# Warte auf DB
echo "⏳ Warte auf PostgreSQL..."
sleep 10

# Prüfe DB
if docker compose -f docker-compose.simple-db.yml exec postgres pg_isready -U streamworks -d streamworks_ki_dev; then
    echo "✅ PostgreSQL läuft!"
else
    echo "❌ PostgreSQL Problem - versuche nochmal in 10 Sekunden..."
    sleep 10
    if docker compose -f docker-compose.simple-db.yml exec postgres pg_isready -U streamworks -d streamworks_ki_dev; then
        echo "✅ PostgreSQL läuft jetzt!"
    else
        echo "❌ PostgreSQL startet nicht - prüfe Docker"
        exit 1
    fi
fi

# Starte pgAdmin
echo "📊 Starte pgAdmin..."
docker compose -f docker-compose.simple-db.yml up -d pgadmin

echo ""
echo "🎉 BEREIT ZUM ENTWICKELN!"
echo "========================"
echo ""
echo "🔗 Datenbank:"
echo "  Host: localhost:5432"
echo "  DB: streamworks_ki_dev"
echo "  User: streamworks"
echo "  Pass: streamworks_dev_2025"
echo ""
echo "🌐 pgAdmin: http://localhost:8080"
echo "  Email: admin@example.com"
echo "  Pass: admin123"
echo ""
echo "💻 Jetzt kannst du entwickeln:"
echo "  cd backend && python -m uvicorn app.main:app --reload"
echo "  cd frontend && npm run dev"
echo ""

# Öffne pgAdmin
if command -v open >/dev/null 2>&1; then
    sleep 5
    open http://localhost:8080
fi