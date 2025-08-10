# scripts/seed.sh
#!/bin/bash

echo "🌱 Seeding database with sample data..."

# Wait for API to be ready
echo "⏳ Waiting for API..."
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
  sleep 2
done

# Run seed script
echo "📊 Inserting sample data..."
docker-compose exec api python -m app.scripts.seed_data

if [ $? -eq 0 ]; then
    echo "✅ Database seeded successfully!"
else
    echo "❌ Seeding failed!"
    exit 1
fi