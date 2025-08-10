# scripts/test-api.sh
#!/bin/bash

# Simple API testing script

API_BASE="http://localhost:8000"

echo "🧪 Testing Gigerly.io Platform API..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local data=$4
    
    echo -e "${BLUE}Testing: $method $endpoint${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE$endpoint")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_BASE$endpoint")
    fi
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS: $endpoint (Status: $response)${NC}"
    else
        echo -e "${RED}❌ FAIL: $endpoint (Expected: $expected_status, Got: $response)${NC}"
    fi
    
    echo ""
}

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
timeout=60
count=0

while [ $count -lt $timeout ]; do
    if curl -s "$API_BASE/api/v1/health" > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    sleep 1
    count=$((count + 1))
done

if [ $count -eq $timeout ]; then
    echo "❌ API failed to start within $timeout seconds"
    exit 1
fi

echo ""

# Test endpoints
test_endpoint "GET" "/" 200
test_endpoint "GET" "/api/v1/health" 200
test_endpoint "GET" "/docs" 200

# Test auth endpoints
test_endpoint "POST" "/api/v1/auth/register" 422  # Should fail validation
test_endpoint "POST" "/api/v1/auth/login" 422     # Should fail validation

# Test protected endpoints (should return 401)
test_endpoint "GET" "/api/v1/auth/me" 401
test_endpoint "GET" "/api/v1/users" 401
test_endpoint "GET" "/api/v1/projects" 200  # Public endpoint
test_endpoint "POST" "/api/v1/projects" 401  # Protected

# Test admin endpoints (should return 401)
test_endpoint "GET" "/api/v1/admin/dashboard" 401

echo "🎉 API testing completed!"
echo ""
echo "To run comprehensive tests:"
echo "  make test"
echo ""
echo "To test with authentication:"
echo "  1. Register a user via /api/v1/auth/register"
echo "  2. Login via /api/v1/auth/login"
echo "  3. Use the token in Authorization header"