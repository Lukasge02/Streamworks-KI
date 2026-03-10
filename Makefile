.PHONY: dev dev-backend dev-frontend infra install docker-up docker-down docker-logs docker-rebuild docker-status deploy

# ── Docker (Production / Server-Deployment) ──────────────────────────

# Alles starten: Postgres + Qdrant + MinIO + Backend + Frontend + Nginx
docker-up:
	docker compose up --build -d
	@echo ""
	@echo "Streamworks-KI laeuft:"
	@echo "  App:           http://localhost (via Nginx)"
	@echo "  Backend API:   http://localhost/api"
	@echo "  Health Check:  http://localhost/health"
	@echo ""
	@echo "Logs: make docker-logs"

# Alles stoppen
docker-down:
	docker compose down

# Logs aller Services verfolgen
docker-logs:
	docker compose logs -f

# Neu bauen (nach Code-Aenderungen)
docker-rebuild:
	docker compose up --build -d --force-recreate backend frontend nginx

# Status aller Container anzeigen
docker-status:
	docker compose ps

# ── Lokale Entwicklung ───────────────────────────────────────────────

# Nur Infrastruktur starten (Qdrant + MinIO, optional Postgres)
infra:
	docker compose up qdrant minio -d

# Infra mit Postgres (wenn man lokal auch PostgreSQL nutzen will)
infra-full:
	docker compose up postgres qdrant minio -d
	@echo "PostgreSQL laeuft auf localhost:5432"
	@echo "DATABASE_URL=postgresql://streamworks:streamworks123@localhost:5432/streamworks"

# Alle Dependencies installieren
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# Backend starten (eigenes Terminal)
dev-backend:
	cd backend && python main.py

# Frontend starten (eigenes Terminal)
dev-frontend:
	cd frontend && npm run dev

# Hinweise fuer lokale Entwicklung
dev:
	@echo "Lokale Entwicklung (3 Terminals):"
	@echo "  1. make infra        # Qdrant + MinIO starten"
	@echo "  2. make dev-backend  # FastAPI auf :8000"
	@echo "  3. make dev-frontend # Next.js auf :3000"
	@echo ""
	@echo "Mit PostgreSQL lokal:"
	@echo "  1. make infra-full   # Postgres + Qdrant + MinIO"
	@echo "  2. DATABASE_URL=postgresql://streamworks:streamworks123@localhost:5432/streamworks make dev-backend"
	@echo ""
	@echo "Oder alles in Docker:  make docker-up"

# Server-Deployment (auf VPS ausfuehren)
deploy:
	git pull
	docker compose up --build -d
	@echo "Deployment abgeschlossen!"
	docker compose ps
