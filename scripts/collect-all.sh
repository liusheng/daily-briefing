#!/usr/bin/env bash
# collect-all.sh — Run all source fetchers and combine output
# Each script exits 0 on success, prints [SKIP] to stderr on error.
# Disable -e so one failure doesn't kill the whole collection.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "========================================"
echo "📡 监听站1379 · 数据采集"
echo "Date: $(date '+%Y-%m-%d %H:%M')"
echo "========================================"
echo ""

sources=(
    "GitHub HEAD:fetch-github-head.py"
    "GitHub RISING:fetch-github-rising.py"
    "Hacker News:fetch-hackernews.py"
    "TechCrunch:fetch-techcrunch.py"
    "雷锋网:fetch-leiphone.py"
    "IT之家:fetch-ithome.py"
)

success=0
failed=0

for entry in "${sources[@]}"; do
    name="${entry%%:*}"
    script="${entry##*:}"
    echo "--- [$name] ---"
    if python3 "$SCRIPT_DIR/$script" 2>/dev/null; then
        echo "✓ $name: OK"
        ((success++))
    else
        echo "— $name: skipped (no data or error)"
        ((failed++))
    fi
    echo ""
done

echo "========================================"
echo "采集完成: $success 成功, $failed 跳过/失败"
echo "来源: GitHub(头部+新锐) · Hacker News · TechCrunch · 雷锋网 · IT之家"
echo "========================================"
