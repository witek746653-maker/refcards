#!/bin/bash
# ══════════════════════════════════════════════════════════════════
#  Refcards — публикация на сервер напрямую с твоего компьютера
#
#  Использование:
#    bash scripts/push.sh root@155.212.185.27
# ══════════════════════════════════════════════════════════════════
set -e

TARGET="$1"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE_DIR="/opt/refcards"

if [ -z "$TARGET" ]; then
  echo ""
  echo "  Использование: bash scripts/push.sh root@155.212.185.27"
  echo ""
  exit 1
fi

echo ""
echo "  ▶ Синхронизирую файлы → $TARGET"
rsync -az --delete \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude 'refcards.db' \
  --exclude 'exports/' \
  --exclude '.git/' \
  --exclude '.gitignore' \
  "$PROJECT_ROOT/backend/"  "$TARGET:$REMOTE_DIR/backend/"
rsync -az --delete \
  "$PROJECT_ROOT/frontend/" "$TARGET:$REMOTE_DIR/frontend/"
rsync -az \
  "$PROJECT_ROOT/scripts/"  "$TARGET:$REMOTE_DIR/scripts/"

echo "  ▶ Перезапускаю сервис..."
ssh "$TARGET" "systemctl restart refcards"

sleep 2
echo -n "  ▶ Статус: "
ssh "$TARGET" "systemctl is-active refcards"

echo ""
echo "  Готово. http://$(echo $TARGET | sed 's/.*@//')"
echo ""
