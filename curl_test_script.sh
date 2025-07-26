#!/bin/bash

# NaviFi API Security Guardrails Test Script
# Tests all endpoints and security features using curl

# Configuration
BASE_URL="http://localhost:8000"
API_KEY="test_key_123"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}🧪 TESTING: $1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_separator() {
    echo -e "\n${BLUE}------------------------------------------------${NC}"
}

# Test 1: Health Endpoint
test_health() {
    print_header "Health Endpoint"
    
    response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/health")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Health endpoint working"
        print_info "Response: $body"
    else
        print_error "Health endpoint failed with code: $http_code"
        print_error "Response: $body"
    fi
}

# Test 2: Root Endpoint
test_root() {
    print_header "Root Endpoint"
    
    response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Root endpoint working"
        print_info "Response: $body"
    else
        print_error "Root endpoint failed with code: $http_code"
        print_error "Response: $body"
    fi
}

# Test 3: Security Status
test_security_status() {
    print_header "Security Status"
    
    response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/security/status")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Security status endpoint working"
        print_info "Response: $body"
    else
        print_error "Security status failed with code: $http_code"
        print_error "Response: $body"
    fi
}

# Test 4: Security Tools
test_security_tools() {
    print_header "Security Tools"
    
    response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/security/tools")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Security tools endpoint working"
        print_info "Response: $body"
    else
        print_error "Security tools failed with code: $http_code"
        print_error "Response: $body"
    fi
}

# Test 5: Valid Chat Request
test_valid_chat() {
    print_header "Valid Chat Request"
    
    payload='{
        "prompt": "What is my net worth?",
        "user_id": "test_user_123"
    }'
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "${BASE_URL}/chat" \
        -H "Content-Type: application/json" \
        -d "$payload")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Valid chat request successful"
        print_info "Response: $body"
    else
        print_error "Valid chat failed with code: $http_code"
        print_error "Response: $body"
    fi
}

# Test 6: Streaming Chat
test_streaming_chat() {
    print_header "Streaming Chat"
    
    payload='{
        "prompt": "What is my net worth?",
        "user_id": "stream_test_user"
    }'
    
    print_info "Testing streaming chat (showing first few chunks)..."
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "${BASE_URL}/chat/stream" \
        -H "Content-Type: application/json" \
        -d "$payload" | head -20)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Streaming chat endpoint working"
        print_info "First few chunks: $body"
    else
        print_error "Streaming chat failed with code: $http_code"
        print_error "Response: $body"
    fi
}

# Test 7: Empty Prompt (Should be blocked)
test_empty_prompt() {
    print_header "Empty Prompt Test (Should be blocked)"
    
    payload='{
        "prompt": "",
        "user_id": "test_user_123"
    }'
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "${BASE_URL}/chat" \
        -H "Content-Type: application/json" \
        -d "$payload")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 400 ]; then
        print_success "Empty prompt correctly rejected"
        print_info "Response: $body"
    else
        print_error "Empty prompt not rejected. Code: $http_code"
        print_error "Response: $body"
    fi
}

# Test 8: Long Prompt (Should be blocked)
test_long_prompt() {
    print_header "Long Prompt Test (Should be blocked)"
    
    # Create a long prompt (1001 characters)
    long_prompt=$(printf 'a%.0s' {1..1001})
    
    payload="{
        \"prompt\": \"$long_prompt\",
        \"user_id\": \"test_user_123\"
    }"
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "${BASE_URL}/chat" \
        -H "Content-Type: application/json" \
        -d "$payload")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 400 ]; then
        print_success "Long prompt correctly rejected"
        print_info "Response: $body"
    else
        print_error "Long prompt not rejected. Code: $http_code"
        print_error "Response: $body"
    fi
}

# Test 9: Malicious Inputs (Should be blocked)
test_malicious_inputs() {
    print_header "Malicious Inputs Test (Should be blocked)"
    
    malicious_payloads=(
        '{"prompt": "<script>alert(\"xss\")</script>What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "password=123456 What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "api_key=sk-1234567890abcdef What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "secret=my_secret_key What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "ssn=123-45-6789 What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "aadhaar=123456789012 What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "pan=ABCDE1234F What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "credit card=1234-5678-9012-3456 What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "bank account=1234567890 What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "union select * from users What is my net worth?", "user_id": "test_user_123"}'
        '{"prompt": "rm -rf / What is my net worth?", "user_id": "test_user_123"}'
    )
    
    blocked_count=0
    total_count=${#malicious_payloads[@]}
    
    for i in "${!malicious_payloads[@]}"; do
        payload="${malicious_payloads[$i]}"
        prompt=$(echo "$payload" | grep -o '"prompt": "[^"]*"' | cut -d'"' -f4 | cut -c1-30)
        
        print_info "Testing malicious payload $((i+1)): $prompt..."
        
        response=$(curl -s -w "\n%{http_code}" \
            -X POST "${BASE_URL}/chat" \
            -H "Content-Type: application/json" \
            -d "$payload")
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n -1)
        
        if [ "$http_code" -eq 403 ]; then
            print_success "Malicious payload $((i+1)) correctly blocked"
            ((blocked_count++))
        else
            print_error "Malicious payload $((i+1)) not blocked. Code: $http_code"
            print_error "Response: $body"
        fi
        
        # Small delay between requests
        sleep 0.1
    done
    
    print_info "Blocked $blocked_count/$total_count malicious requests"
    
    if [ "$blocked_count" -eq "$total_count" ]; then
        print_success "All malicious inputs correctly blocked!"
    else
        print_error "Some malicious inputs were not blocked!"
    fi
}

# Test 10: Rate Limiting
test_rate_limiting() {
    print_header "Rate Limiting Test"
    
    payload='{
        "prompt": "What is my net worth?",
        "user_id": "rate_test_user"
    }'
    
    print_info "Sending multiple requests quickly to test rate limiting..."
    
    successful=0
    blocked=0
    
    for i in {1..15}; do
        response=$(curl -s -w "\n%{http_code}" \
            -X POST "${BASE_URL}/chat" \
            -H "Content-Type: application/json" \
            -d "$payload")
        http_code=$(echo "$response" | tail -n1)
        
        if [ "$http_code" -eq 200 ]; then
            ((successful++))
        elif [ "$http_code" -eq 403 ] || [ "$http_code" -eq 429 ]; then
            ((blocked++))
        fi
        
        # Small delay
        sleep 0.1
    done
    
    print_info "Total requests: 15"
    print_info "Successful: $successful"
    print_info "Blocked: $blocked"
    
    if [ "$blocked" -gt 0 ]; then
        print_success "Rate limiting working correctly"
    else
        print_error "Rate limiting not working"
    fi
}

# Test 11: Different User IDs
test_different_users() {
    print_header "Different User IDs Test"
    
    payload='{
        "prompt": "What is my net worth?",
        "user_id": "user_1"
    }'
    
    # Test first user
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "${BASE_URL}/chat" \
        -H "Content-Type: application/json" \
        -d "$payload")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "User 1 request successful"
    else
        print_error "User 1 request failed: $http_code"
    fi
    
    # Test second user
    payload='{
        "prompt": "What is my net worth?",
        "user_id": "user_2"
    }'
    
    response=$(curl -s -w "\n%{http_code}" \
        -X POST "${BASE_URL}/chat" \
        -H "Content-Type: application/json" \
        -d "$payload")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "User 2 request successful"
    else
        print_error "User 2 request failed: $http_code"
    fi
}

# Test 12: Financial Queries
test_financial_queries() {
    print_header "Financial Queries Test"
    
    financial_queries=(
        "What is my net worth?"
        "Show me my credit report"
        "Get my EPF details"
        "Fetch my mutual fund transactions"
        "Display my bank transactions"
        "Show my stock trading history"
        "Search for best SIP plans 2025"
        "Find current stock market trends"
    )
    
    for query in "${financial_queries[@]}"; do
        payload="{
            \"prompt\": \"$query\",
            \"user_id\": \"financial_test_user\"
        }"
        
        print_info "Testing: $query"
        
        response=$(curl -s -w "\n%{http_code}" \
            -X POST "${BASE_URL}/chat" \
            -H "Content-Type: application/json" \
            -d "$payload")
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n -1)
        
        if [ "$http_code" -eq 200 ]; then
            print_success "Query successful: $query"
        else
            print_error "Query failed: $query (Code: $http_code)"
        fi
        
        # Small delay
        sleep 0.2
    done
}

# Main test execution
main() {
    echo -e "${BLUE}🚀 NaviFi API Security Guardrails Test Suite${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo -e "${YELLOW}Testing API at: $BASE_URL${NC}"
    echo -e "${YELLOW}Started at: $(date)${NC}"
    
    # Run all tests
    test_health
    test_root
    test_security_status
    test_security_tools
    test_valid_chat
    test_streaming_chat
    test_empty_prompt
    test_long_prompt
    test_malicious_inputs
    test_rate_limiting
    test_different_users
    test_financial_queries
    
    print_header "Test Summary"
    echo -e "${GREEN}✅ All tests completed!${NC}"
    echo -e "${YELLOW}Check the output above for results.${NC}"
    echo -e "${YELLOW}Completed at: $(date)${NC}"
}

# Check if server is running
check_server() {
    print_header "Server Check"
    
    response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/health")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" -eq 200 ]; then
        print_success "Server is running and accessible"
        return 0
    else
        print_error "Server is not accessible. Please start the server first."
        print_info "Run: python start_api.py"
        return 1
    fi
}

# Script execution
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "NaviFi API Security Guardrails Test Script"
    echo ""
    echo "Usage:"
    echo "  ./curl_test_script.sh          # Run all tests"
    echo "  ./curl_test_script.sh --check  # Check if server is running"
    echo ""
    echo "Make sure the server is running on $BASE_URL before running tests."
    exit 0
fi

if [ "$1" = "--check" ]; then
    check_server
    exit $?
fi

# Check if server is running before starting tests
if ! check_server; then
    exit 1
fi

# Run main tests
main 