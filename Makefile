# Gigerly.io Platform - Development Commands
# Usage: make <command>

.PHONY: help build up down restart logs shell migrate seed clean test lint format start health

# Default target
help: ## Show this help message
	@echo "Gigerly.io Platform - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup    # Initial project setup"
	@echo "  make start    # Build + Start + Migrate + Seed"
	@echo "  make health   # Check all services"

# Docker commands
build: ## Build all Docker containers
	@echo "🔨 Building containers..."
	docker-compose build

up: ## Start all services
	@echo "🚀 Starting services..."
	docker-compose up -d

down: ## Stop all services
	@echo "🛑 Stopping services..."
	docker-compose down

restart: ## Restart all services
	@echo "🔄 Restarting services..."
	docker-compose restart

# Logs
logs: ## Show logs from all services
	docker-compose logs -f

logs-api: ## Show API logs only
	docker-compose logs -f api

logs-web: ## Show web logs only
	docker-compose logs -f web

logs-db: ## Show database logs only
	docker-compose logs -f db

logs-redis: ## Show Redis logs only
	docker-compose logs -f redis

# Shell access
shell-api: ## Access API container shell
	docker-compose exec api bash

shell-web: ## Access web container shell
	docker-compose exec web sh

shell-db: ## Access database shell
	docker-compose exec db psql -U gigerlyio_user -d gigerlyio_db

shell-redis: ## Access Redis shell
	docker-compose exec redis redis-cli

# Database operations
migrate: ## Run database migrations
	@echo "🔄 Running migrations..."
	./scripts/migrate.sh

migrate-create: ## Create new migration (usage: make migrate-create name="description")
	@echo "📝 Creating migration..."
	./scripts/migrate.sh create "$(name)"

migrate-reset: ## Reset database (DANGEROUS!)
	@echo "⚠️  Resetting database..."
	./scripts/migrate.sh reset

migrate-seed: ## Run migrations and seed data
	@echo "🌱 Running migrations and seeding data..."
	./scripts/migrate.sh seed

# Database utilities
db-backup: ## Create database backup
	@echo "💾 Creating database backup..."
	./scripts/db-utils.sh backup

db-restore: ## Restore database from backup (usage: make db-restore file="backup.sql")
	@echo "📥 Restoring database..."
	./scripts/db-utils.sh restore "$(file)"

db-stats: ## Show database statistics
	./scripts/db-utils.sh stats

db-size: ## Show database size information
	./scripts/db-utils.sh size

db-vacuum: ## Clean up database
	@echo "🧹 Cleaning database..."
	./scripts/db-utils.sh vacuum

db-test: ## Test database connection
	./scripts/db-utils.sh test

# Development workflow
setup: ## Initial project setup
	@echo "🛠️  Setting up project..."
	./scripts/setup.sh
	make build
	make up
	@echo "⏳ Waiting for services to start..."
	sleep 15
	make migrate-seed
	@echo "✅ Setup complete!"

start: build up ## Quick start (build + up + migrate + seed)
	@echo "⏳ Waiting for services to start..."
	sleep 10
	make migrate
	@echo "✅ Platform started successfully!"
	@echo ""
	@echo "🌐 Access Points:"
	@echo "  API Docs:  http://localhost:8000/docs"
	@echo "  Web App:   http://localhost:3000"
	@echo "  Admin:     http://localhost:3000/admin"

dev: ## Start development environment
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

# Code quality
test: ## Run all tests
	@echo "🧪 Running tests..."
	docker-compose exec api python -m pytest tests/ -v

test-unit: ## Run unit tests only
	docker-compose exec api python -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	docker-compose exec api python -m pytest tests/integration/ -v

test-coverage: ## Run tests with coverage report
	@echo "📊 Running tests with coverage..."
	docker-compose exec api python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

test-api: ## Test API endpoints
	@echo "🔍 Testing API endpoints..."
	./scripts/test-api.sh

# Code formatting and linting
lint: ## Run linting on API code
	@echo "🔍 Running linting..."
	docker-compose exec api flake8 app/ --max-line-length=88 --extend-ignore=E203,W503
	docker-compose exec api mypy app/ --ignore-missing-imports

lint-fix: ## Fix linting issues automatically
	docker-compose exec api black app/
	docker-compose exec api isort app/

format: ## Format all code
	@echo "✨ Formatting code..."
	docker-compose exec api black app/
	docker-compose exec api isort app/
	docker-compose exec web npm run format 2>/dev/null || echo "Web formatting skipped"

format-check: ## Check code formatting
	docker-compose exec api black --check app/
	docker-compose exec api isort --check-only app/

# Health and monitoring
health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@echo ""
	@echo "🔍 API Health:"
	@curl -s http://localhost:8000/api/v1/health | python -m json.tool 2>/dev/null || echo "  ❌ API not responding"
	@echo ""
	@echo "🔍 Web Health:"
	@curl -s http://localhost:3000 >/dev/null 2>&1 && echo "  ✅ Web OK" || echo "  ❌ Web not responding"
	@echo ""
	@echo "🔍 Database Health:"
	@./scripts/db-utils.sh test
	@echo ""
	@echo "🔍 Redis Health:"
	@docker-compose exec redis redis-cli ping 2>/dev/null && echo "  ✅ Redis OK" || echo "  ❌ Redis not responding"

status: ## Show status of all containers
	@echo "📊 Container Status:"
	docker-compose ps

# Cleanup
clean: ## Stop and remove containers, volumes
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Cleanup complete"

clean-all: ## Remove everything including images
	@echo "🗑️  Removing everything..."
	docker-compose down -v --rmi all
	docker system prune -a -f
	@echo "✅ Complete cleanup done"

clean-logs: ## Clear log files
	@echo "📝 Clearing logs..."
	rm -rf logs/*.log
	docker-compose exec api rm -rf logs/*.log 2>/dev/null || true

# Production commands
prod-build: ## Build for production
	@echo "🏭 Building for production..."
	docker-compose -f docker-compose.prod.yml build

prod-up: ## Start production environment
	@echo "🚀 Starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production environment
	@echo "🛑 Stopping production environment..."
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## Show production logs
	docker-compose -f docker-compose.prod.yml logs -f

prod-migrate: ## Run production migrations
	@echo "🔄 Running production migrations..."
	docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Monitoring and debugging
debug-api: ## Debug API with hot reload
	docker-compose up api redis db

debug-web: ## Debug web with hot reload
	docker-compose up web

ps: ## Show running containers
	docker-compose ps

top: ## Show container resource usage
	docker stats $$(docker-compose ps -q)

# Cache operations
cache-clear: ## Clear Redis cache
	@echo "🗑️  Clearing cache..."
	docker-compose exec redis redis-cli FLUSHALL
	@echo "✅ Cache cleared"

cache-info: ## Show Redis cache information
	docker-compose exec redis redis-cli INFO memory

# Backup and restore
backup: ## Create full backup (database + files)
	@echo "💾 Creating full backup..."
	mkdir -p backups/$$(date +%Y%m%d)
	make db-backup
	tar -czf backups/$$(date +%Y%m%d)/files-$$(date +%H%M%S).tar.gz web/uploads api/logs 2>/dev/null || true
	@echo "✅ Backup complete: backups/$$(date +%Y%m%d)/"

# Development helpers
seed: ## Seed database with sample data
	@echo "🌱 Seeding database..."
	docker-compose exec api python -m app.scripts.seed_data

reset-dev: ## Reset development environment
	@echo "🔄 Resetting development environment..."
	make down
	make clean
	make setup

install-hooks: ## Install git hooks
	@echo "🪝 Installing git hooks..."
	cp scripts/pre-commit .git/hooks/
	chmod +x .git/hooks/pre-commit
	@echo "✅ Git hooks installed"

# Documentation
docs: ## Generate API documentation
	@echo "📚 Generating documentation..."
	docker-compose exec api python -m app.docs.generate
	@echo "✅ Documentation generated"

# Quick shortcuts
api: up migrate ## Start API only
	docker-compose up api redis db

web: ## Start web only
	docker-compose up web

worker: ## Start background worker
	docker-compose up worker

.PHONY: test testcov

test:
	ENVIRONMENT=test pytest

testcov:
	ENVIRONMENT=test pytest --cov=app --cov-report=term-missing