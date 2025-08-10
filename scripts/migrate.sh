# scripts/migrate.sh
#!/bin/bash

echo "🔄 Running database migrations..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
until docker-compose exec db pg_isready -U gigerlyio_user -d gigerlyio_db; do
  sleep 2
done

# Run migrations
echo "📊 Running Alembic migrations..."
docker-compose exec api alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully!"
else
    echo "❌ Migration failed!"
    exit 1
fi
