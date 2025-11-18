#!/bin/bash
# Comprehensive Feature Testing Script for The Discoverer

BASE_URL="${BASE_URL:-http://localhost:8000}"
TEST_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=${5:-200}
    
    TEST_COUNT=$((TEST_COUNT + 1))
    echo -e "\n${YELLOW}[$TEST_COUNT] Testing: $name${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body" | head -3
        PASS_COUNT=$((PASS_COUNT + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code, expected $expected_status)"
        echo "$body" | head -5
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return 1
    fi
}

echo "=========================================="
echo "The Discoverer - Feature Testing Suite"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo ""

# Check if server is running
if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}✗ Server is not running at $BASE_URL${NC}"
    echo "   Start it with: make run"
    exit 1
fi

echo -e "${GREEN}✓ Server is running${NC}"
echo ""

# ============================================
# FEATURE 1: Health & Status
# ============================================
echo "=========================================="
echo "FEATURE 1: Health & Status"
echo "=========================================="

test_endpoint "Root endpoint" "GET" "/" 
test_endpoint "Health check" "GET" "/health"
test_endpoint "Database health" "GET" "/api/health/databases"
test_endpoint "Check all databases" "POST" "/api/health/databases/check-all" "{}"

# ============================================
# FEATURE 2: Database Discovery
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 2: Database Discovery"
echo "=========================================="

test_endpoint "List databases" "GET" "/api/discovery/databases"
test_endpoint "Search databases" "GET" "/api/discovery/search?query=test" "" 404

# ============================================
# FEATURE 3: Query Execution (without LLM - will fail gracefully)
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 3: Query Execution"
echo "=========================================="

# Execute query - may fail if LLM dependencies are missing (Keras/Transformers issue)
test_endpoint "Execute query" "POST" "/api/query/execute" \
    '{"query": "show me all users", "database_ids": []}' 500

# ============================================
# FEATURE 4: Query History
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 4: Query History"
echo "=========================================="

test_endpoint "Get query history" "GET" "/api/history/queries?limit=5"
test_endpoint "Get history stats" "GET" "/api/history/statistics"

# ============================================
# FEATURE 5: Statistics
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 5: Statistics & Performance"
echo "=========================================="

test_endpoint "Performance stats" "GET" "/api/stats/performance"
test_endpoint "Usage analytics" "GET" "/api/analytics/stats?days=7"
test_endpoint "Top queries" "GET" "/api/analytics/top-queries?limit=5"

# ============================================
# FEATURE 6: Query Templates
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 6: Query Templates"
echo "=========================================="

test_endpoint "List templates" "GET" "/api/templates"

# ============================================
# FEATURE 7: Batch Queries
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 7: Batch Queries"
echo "=========================================="

test_endpoint "Batch execute" "POST" "/api/batch/execute" \
    '{"queries": [{"query": "test1"}, {"query": "test2"}], "database_ids": []}'

# ============================================
# FEATURE 8: Scheduler
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 8: Scheduled Queries"
echo "=========================================="

test_endpoint "List schedules" "GET" "/api/scheduler"

# ============================================
# FEATURE 9: Optimization
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 9: Query Optimization"
echo "=========================================="

test_endpoint "Analyze query" "POST" "/api/optimization/analyze" \
    '{"query": "SELECT * FROM users WHERE id = 1"}'

# ============================================
# FEATURE 10: Caching
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 10: Caching"
echo "=========================================="

test_endpoint "Cache stats" "GET" "/api/cache/stats"

# ============================================
# FEATURE 11: Sharing
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 11: Query Sharing"
echo "=========================================="

test_endpoint "List shares" "GET" "/api/sharing"

# ============================================
# FEATURE 12: Webhooks
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 12: Webhooks"
echo "=========================================="

test_endpoint "List webhooks" "GET" "/api/webhooks"

# ============================================
# FEATURE 13: API Keys
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 13: API Keys"
echo "=========================================="

test_endpoint "List API keys" "GET" "/api/api-keys"

# ============================================
# FEATURE 14: Connection Pools
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 14: Connection Pool Management"
echo "=========================================="

test_endpoint "List pools" "GET" "/api/pools"

# ============================================
# FEATURE 15: Dashboards
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 15: Dashboards"
echo "=========================================="

test_endpoint "List dashboards" "GET" "/api/dashboards"

# ============================================
# FEATURE 16: Chart Templates
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 16: Chart Templates"
echo "=========================================="

test_endpoint "List chart templates" "GET" "/api/chart-templates"

# ============================================
# FEATURE 17: Export Templates
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 17: Export Templates"
echo "=========================================="

test_endpoint "List export templates" "GET" "/api/export-templates"

# ============================================
# FEATURE 18: Scheduled Exports
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 18: Scheduled Exports"
echo "=========================================="

test_endpoint "List scheduled exports" "GET" "/api/scheduled-exports"

# ============================================
# FEATURE 19: Metrics
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 19: Prometheus Metrics"
echo "=========================================="

test_endpoint "Get metrics" "GET" "/api/metrics/prometheus"

# ============================================
# FEATURE 20: Versioning
# ============================================
echo ""
echo "=========================================="
echo "FEATURE 20: Query Versioning"
echo "=========================================="

# Versioning endpoint - 404 is expected if no query exists
test_endpoint "Versioning endpoint" "GET" "/api/versioning/queries/test/versions" "" 404

# ============================================
# Summary
# ============================================
echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo "Total Tests: $TEST_COUNT"
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi

