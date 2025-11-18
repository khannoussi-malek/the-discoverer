#!/usr/bin/env python3
"""Python-based feature testing script."""
import asyncio
import httpx
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_RESULTS = []


class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_test(name: str, status: str, details: str = ""):
    """Print test result."""
    color = Colors.GREEN if status == "PASS" else Colors.RED
    print(f"{color}[{status}]{Colors.NC} {name}")
    if details:
        print(f"      {details}")


async def test_feature(name: str, method: str, endpoint: str, 
                      data: Optional[Dict] = None, expected_status: int = 200,
                      requires_llm: bool = False):
    """Test a single feature endpoint."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method == "GET":
                response = await client.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = await client.post(f"{BASE_URL}{endpoint}", json=data or {})
            elif method == "PUT":
                response = await client.put(f"{BASE_URL}{endpoint}", json=data or {})
            elif method == "DELETE":
                response = await client.delete(f"{BASE_URL}{endpoint}")
            
            if response.status_code == expected_status:
                print_test(name, "PASS", f"HTTP {response.status_code}")
                TEST_RESULTS.append(("PASS", name, requires_llm))
                try:
                    result = response.json()
                    if isinstance(result, dict) and len(str(result)) < 200:
                        print(f"      Response: {json.dumps(result, indent=2)[:150]}...")
                except:
                    pass
                return True
            else:
                print_test(name, "FAIL", f"HTTP {response.status_code} (expected {expected_status})")
                TEST_RESULTS.append(("FAIL", name, requires_llm))
                print(f"      Error: {response.text[:200]}")
                return False
        except Exception as e:
            print_test(name, "FAIL", f"Exception: {str(e)[:100]}")
            TEST_RESULTS.append(("FAIL", name, requires_llm))
            return False


async def test_all_features(skip_llm: bool = False):
    """Test all features systematically."""
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}The Discoverer - Feature Testing Suite{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"Base URL: {BASE_URL}")
    if skip_llm:
        print(f"{Colors.YELLOW}⚠️  Skipping LLM-required tests{Colors.NC}")
    print()
    
    # Check server
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✓ Server is running{Colors.NC}\n")
            else:
                print(f"{Colors.RED}✗ Server returned status {response.status_code}{Colors.NC}")
                return
    except Exception as e:
        print(f"{Colors.RED}✗ Cannot connect to server: {e}{Colors.NC}")
        print("   Start server with: make run")
        return
    
    print(f"{Colors.YELLOW}Starting feature tests...{Colors.NC}\n")
    
    # ============================================
    # FEATURE 1: Health & Status (No LLM)
    # ============================================
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 1: Health & Status{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("Root endpoint", "GET", "/", requires_llm=False)
    await test_feature("Health check", "GET", "/health", requires_llm=False)
    await test_feature("Database health", "GET", "/api/health/databases", requires_llm=False)
    await test_feature("Check all databases", "POST", "/api/health/databases/check-all", {}, requires_llm=False)
    
    # ============================================
    # FEATURE 2: Database Discovery (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 2: Database Discovery{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List databases", "GET", "/api/discovery/databases", requires_llm=False)
    await test_feature("Search databases", "GET", "/api/discovery/search?query=test", requires_llm=False)
    
    # ============================================
    # FEATURE 3: Query Execution (Requires LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 3: Query Execution{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    if not skip_llm:
        await test_feature("Execute query", "POST", "/api/query/execute", 
                          {"query": "show me all users", "database_ids": []}, requires_llm=True)
    else:
        print(f"{Colors.YELLOW}⏭️  Skipped (requires LLM){Colors.NC}")
        TEST_RESULTS.append(("SKIP", "Execute query", True))
    
    # ============================================
    # FEATURE 4: Query History (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 4: Query History{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("Get query history", "GET", "/api/history/queries?limit=5", requires_llm=False)
    await test_feature("Get history stats", "GET", "/api/history/statistics", requires_llm=False)
    
    # ============================================
    # FEATURE 5: Statistics & Analytics (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 5: Statistics & Analytics{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("Performance stats", "GET", "/api/stats/performance", requires_llm=False)
    await test_feature("Usage analytics", "GET", "/api/analytics/stats?days=7", requires_llm=False)
    await test_feature("Top queries", "GET", "/api/analytics/top-queries?limit=5", requires_llm=False)
    
    # ============================================
    # FEATURE 6: Query Templates (No LLM for listing)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 6: Query Templates{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List templates", "GET", "/api/templates", requires_llm=False)
    
    # ============================================
    # FEATURE 7: Batch Queries (Requires LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 7: Batch Queries{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    if not skip_llm:
        await test_feature("Batch execute", "POST", "/api/batch/execute",
                          {"queries": [{"query": "test1"}, {"query": "test2"}], "database_ids": []}, requires_llm=True)
    else:
        print(f"{Colors.YELLOW}⏭️  Skipped (requires LLM){Colors.NC}")
        TEST_RESULTS.append(("SKIP", "Batch execute", True))
    
    # ============================================
    # FEATURE 8: Scheduler (No LLM for listing)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 8: Scheduled Queries{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List schedules", "GET", "/api/scheduler", requires_llm=False)
    
    # ============================================
    # FEATURE 9: Optimization (No LLM - SQL analysis only)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 9: Query Optimization{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("Analyze query", "POST", "/api/optimization/analyze",
                      {"query": "SELECT * FROM users WHERE id = 1"}, requires_llm=False)
    
    # ============================================
    # FEATURE 10: Caching (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 10: Caching{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("Cache stats", "GET", "/api/cache/stats", requires_llm=False)
    
    # ============================================
    # FEATURE 11: Sharing (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 11: Query Sharing{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List shares", "GET", "/api/sharing", requires_llm=False)
    
    # ============================================
    # FEATURE 12: Webhooks (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 12: Webhooks{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List webhooks", "GET", "/api/webhooks", requires_llm=False)
    
    # ============================================
    # FEATURE 13: API Keys (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 13: API Keys{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List API keys", "GET", "/api/api-keys", requires_llm=False)
    
    # ============================================
    # FEATURE 14: Connection Pools (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 14: Connection Pool Management{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List pools", "GET", "/api/pools", requires_llm=False)
    
    # ============================================
    # FEATURE 15: Dashboards (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 15: Dashboards{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List dashboards", "GET", "/api/dashboards", requires_llm=False)
    
    # ============================================
    # FEATURE 16: Chart Templates (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 16: Chart Templates{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List chart templates", "GET", "/api/chart-templates", requires_llm=False)
    
    # ============================================
    # FEATURE 17: Export Templates (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 17: Export Templates{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List export templates", "GET", "/api/export-templates", requires_llm=False)
    
    # ============================================
    # FEATURE 18: Scheduled Exports (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 18: Scheduled Exports{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("List scheduled exports", "GET", "/api/scheduled-exports", requires_llm=False)
    
    # ============================================
    # FEATURE 19: Metrics (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 19: Prometheus Metrics{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("Get metrics", "GET", "/api/metrics/prometheus", requires_llm=False)
    
    # ============================================
    # FEATURE 20: Versioning (No LLM)
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}FEATURE 20: Query Versioning{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    await test_feature("Versioning endpoint", "GET", "/api/versioning/queries/test/versions", requires_llm=False)
    
    # ============================================
    # Summary
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    
    total = len(TEST_RESULTS)
    passed = sum(1 for status, _, _ in TEST_RESULTS if status == "PASS")
    failed = sum(1 for status, _, _ in TEST_RESULTS if status == "FAIL")
    skipped = sum(1 for status, _, _ in TEST_RESULTS if status == "SKIP")
    no_llm_tests = sum(1 for _, _, req_llm in TEST_RESULTS if not req_llm)
    no_llm_passed = sum(1 for status, _, req_llm in TEST_RESULTS if not req_llm and status == "PASS")
    
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.NC}")
    print(f"{Colors.RED}Failed: {failed}{Colors.NC}")
    if skipped > 0:
        print(f"{Colors.YELLOW}Skipped: {skipped}{Colors.NC}")
    print(f"\nNon-LLM Tests: {no_llm_tests}")
    print(f"{Colors.GREEN}Non-LLM Passed: {no_llm_passed}{Colors.NC}")
    if no_llm_tests > 0:
        print(f"Non-LLM Success Rate: {(no_llm_passed/no_llm_tests*100):.1f}%")
    
    if failed > 0:
        print(f"\n{Colors.RED}Failed Tests:{Colors.NC}")
        for status, name, _ in TEST_RESULTS:
            if status == "FAIL":
                print(f"  - {name}")
    
    print()
    
    # Return appropriate exit code
    if failed == 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    skip_llm = "--skip-llm" in sys.argv
    exit_code = asyncio.run(test_all_features(skip_llm=skip_llm))
    sys.exit(exit_code)

