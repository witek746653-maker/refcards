#!/bin/bash
# ══════════════════════════════════════════════════════════════════
#  Refcards — бэкап кода на GitHub (запускай когда хочешь)
#
#  Использование:
#    bash scripts/backup-github.sh "описание изменений"
# ══════════════════════════════════════════════════════════════════
set -e

MSG="${1:-backup $(date '+%Y-%m-%d %H:%M')}"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_ROOT"

git add .

if git diff --cached --quiet; then
  echo ""
  echo "  Нет изменений — GitHub уже актуален."
  echo ""
else
  git commit -m "$MSG"
  git push origin main
  echo ""
  echo "  ✓ Запушено: $MSG"
  echo ""
fi
