# scripts/setup.sh (güncellenmiş)
#!/bin/bash

echo "🚀 Gigerly.io Platform Setup Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Create environment files from examples
if [ ! -f "api/.env" ]; then
    print_status "Creating API environment file..."
    cp .env.example api/.env
fi

if [ ! -f "web/.env.local" ]; then
    print_status "Creating Web environment file..."
    cat > web/.env.local << EOF
NEXT_PUBLIC_API_BASE=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-change-this
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
EOF
fi

# Create necessary directories
print_status "Creating project directories..."
mkdir -p api/app/{core,auth,models,schemas,routes,services,utils,scripts}
mkdir -p api/alembic/versions
mkdir -p api/tests
mkdir -p api/logs
mkdir -p web/app/{admin,freelancer,customer,api}
mkdir -p web/{components,lib,hooks,types}
mkdir -p web/components/{ui,forms,layout,project,contract,common}
mkdir -p nginx/conf.d
mkdir -p db/{init,seeds}
mkdir -p docs/{api,deployment,development}
mkdir -p logs
mkdir -p backups

# Create __init__.py files for Python packages
print_status "Creating Python package files..."
find api/app -type d -exec touch {}/__init__.py \;
find api/tests -type d -exec touch {}/__init__.py \;

# Set executable permissions for scripts
chmod +x scripts/*.sh

# Create docker-compose override for development
if [ ! -f "docker-compose.override.yml" ]; then
    print_status "Creating development docker-compose override..."
    cat > docker-compose.override.yml << EOF
version: "3.9"

services:
  api:
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      - ./api:/app
      - /app/__pycache__
      
  web:
    environment:
      - NODE_ENV=development
    volumes:
      - ./web:/app
      - /app/node_modules
      - /app/.next
EOF
fi

print_success "Setup complete!"
print_status "Next steps:"
echo "1. Update .env files with your actual values"
echo "2. Run: make start (or docker-compose up --build)"
echo "3. Run migrations: make migrate"
echo "4. Seed data: make migrate-seed"
echo ""
echo "Access points:"
echo "  - API docs: http://localhost:8000/docs"
echo "  - Web app: http://localhost:3000"
echo "  - Admin: http://localhost:3000/admin"