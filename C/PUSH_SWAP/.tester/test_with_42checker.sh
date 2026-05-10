#!/bin/bash

# 42tokyo提供のcheckerを使ったテストスクリプト
# checker_macまたはchecker_linuxが必要です

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# OSの検出とcheckerの選択
if [[ "$OSTYPE" == "darwin"* ]]; then
    CHECKER="./checker_Mac"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CHECKER="./checker_linux"
else
    echo -e "${RED}Unknown OS. Please specify checker manually.${NC}"
    exit 1
fi

PUSH_SWAP="./push_swap"

# ファイルの存在確認
if [ ! -f "$PUSH_SWAP" ]; then
    echo -e "${RED}Error: push_swap not found${NC}"
    exit 1
fi

if [ ! -f "$CHECKER" ]; then
    echo -e "${RED}Error: $CHECKER not found${NC}"
    echo "Download from: https://projects.intra.42.fr/projects/push_swap"
    exit 1
fi

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  42 Checker Tests${NC}"
echo -e "${YELLOW}========================================${NC}\n"

# テスト関数
test_with_checker() {
    local test_name="$1"
    local args="$2"
    
    echo -e "${BLUE}Test: $test_name${NC}"
    echo "Args: $args"
    
    # 操作数をカウント
    local count=$(eval "./push_swap $args | wc -l")
    echo "Operations: $count"
    
    # checkerで検証
    local result=$(eval "./push_swap $args | $CHECKER $args 2>&1")
    echo "Result: $result"
    
    if [ "$result" = "OK" ]; then
        echo -e "${GREEN}✓ PASSED${NC}\n"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}\n"
        return 1
    fi
}

# 基本テスト
echo -e "${YELLOW}=== Basic Tests ===${NC}"
test_with_checker "Example from subject" "4 67 3 87 23"
test_with_checker "2 numbers" "2 1"
test_with_checker "3 numbers" "3 2 1"
test_with_checker "Already sorted" "1 2 3 4 5"
echo ""

# 負の数テスト
echo -e "${YELLOW}=== Negative Numbers ===${NC}"
test_with_checker "Negative numbers" "-1 -2 -3"
test_with_checker "Mixed" "-5 3 -1 0 2"
echo ""

# 5要素テスト
echo -e "${YELLOW}=== 5 Elements Tests ===${NC}"
test_with_checker "5 random #1" "5 4 3 2 1"
test_with_checker "5 random #2" "2 4 1 5 3"
test_with_checker "5 random #3" "1 5 2 4 3"
echo ""

# ベンチマーク（100要素）
echo -e "${YELLOW}=== Benchmark (100 elements) ===${NC}"
for i in {1..5}; do
    ARG=$(seq 1 100 | shuf | tr '\n' ' ')
    COUNT=$(./push_swap $ARG | wc -l)
    RESULT=$(./push_swap $ARG | $CHECKER $ARG)
    
    if [ "$RESULT" = "OK" ]; then
        echo -e "${GREEN}Test $i: $COUNT operations - OK${NC}"
    else
        echo -e "${RED}Test $i: FAILED${NC}"
    fi
done
echo ""

# ベンチマーク（500要素）
echo -e "${YELLOW}=== Benchmark (500 elements) ===${NC}"
for i in {1..3}; do
    ARG=$(seq 1 500 | shuf | tr '\n' ' ')
    COUNT=$(./push_swap $ARG | wc -l)
    RESULT=$(./push_swap $ARG | $CHECKER $ARG)
    
    if [ "$RESULT" = "OK" ]; then
        echo -e "${GREEN}Test $i: $COUNT operations - OK${NC}"
    else
        echo -e "${RED}Test $i: FAILED${NC}"
    fi
done
echo ""

echo -e "${GREEN}All tests completed!${NC}"
