#!/bin/bash
# Quick test script for threat modeling API
# Usage: ./test-threat-modeling.sh [username] [password]

USERNAME=${1:-"testuser"}
PASSWORD=${2:-"testpass123"}
API_URL="http://localhost/api"

echo "=== Threat Modeling API Test ==="
echo ""

# Step 1: Login
echo "1. Logging in as $USERNAME..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"$PASSWORD\"
  }")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful!"
echo ""

# Step 2: Test High-Risk SQL Injection Threat
echo "2. Testing High-Risk SQL Injection Threat..."
THREAT_RESPONSE=$(curl -s -X POST "$API_URL/threats/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "User Authentication API Endpoint",
    "flow": "User submits login credentials via POST request. Backend queries PostgreSQL database using string concatenation without parameterized queries. Attacker injects malicious SQL payload in username field.",
    "trust_boundary": "Public Internet -> Application Server -> Database",
    "damage": 9,
    "reproducibility": 8,
    "exploitability": 9,
    "affected_users": 10,
    "discoverability": 7
  }')

THREAT_ID=$(echo $THREAT_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$THREAT_ID" ]; then
  echo "❌ Threat analysis failed!"
  echo "Response: $THREAT_RESPONSE"
  exit 1
fi

echo "✅ Threat analyzed successfully! Threat ID: $THREAT_ID"
echo "Response:"
echo $THREAT_RESPONSE | python3 -m json.tool 2>/dev/null || echo $THREAT_RESPONSE
echo ""

# Step 3: List all threats
echo "3. Listing all threats..."
LIST_RESPONSE=$(curl -s -X GET "$API_URL/threats" \
  -H "Authorization: Bearer $TOKEN")

echo "✅ Threats retrieved:"
echo $LIST_RESPONSE | python3 -m json.tool 2>/dev/null || echo $LIST_RESPONSE
echo ""

# Step 4: Get specific threat details
if [ ! -z "$THREAT_ID" ]; then
  echo "4. Getting threat details for ID: $THREAT_ID..."
  DETAIL_RESPONSE=$(curl -s -X GET "$API_URL/threats/$THREAT_ID" \
    -H "Authorization: Bearer $TOKEN")
  
  echo "✅ Threat details:"
  echo $DETAIL_RESPONSE | python3 -m json.tool 2>/dev/null || echo $DETAIL_RESPONSE
  echo ""
fi

echo "=== Test Complete ==="

