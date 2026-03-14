#!/bin/bash
# ══════════════════════════════════════════════════════════════════
#  Refcards — деплой на VPS
#  Использование: bash scripts/deploy.sh root@155.212.185.27
# ══════════════════════════════════════════════════════════════════
set -e

TARGET="$1"
REMOTE_DIR="/opt/refcards"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ -z "$TARGET" ]; then
  echo ""
  echo "  Использование: bash scripts/deploy.sh root@155.212.185.27"
  echo ""
  exit 1
fi

echo ""
echo "  1/5  Заливаю файлы → $TARGET:$REMOTE_DIR"
ssh "$TARGET" "mkdir -p $REMOTE_DIR/backend/exports $REMOTE_DIR/frontend"
rsync -az --delete \
  --exclude '__pycache__' --exclude '*.pyc' --exclude 'refcards.db' --exclude 'exports/' \
  "$PROJECT_ROOT/backend/" "$TARGET:$REMOTE_DIR/backend/"
rsync -az --delete \
  "$PROJECT_ROOT/frontend/" "$TARGET:$REMOTE_DIR/frontend/"

echo "  2/5  Устанавливаю зависимости..."
ssh "$TARGET" 'bash -s' << 'REMOTE'
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q python3-pip nginx \
  libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
pip3 install -r /opt/refcards/backend/requirements.txt --break-system-packages --ignore-installed -q
REMOTE

echo "  3/5  Настраиваю nginx..."
ssh "$TARGET" 'bash -s' << 'REMOTE'
cat > /etc/nginx/sites-available/refcards << 'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    # Фронтенд — статика напрямую через nginx
    root /opt/refcards/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API — проксируем в Flask
    location /api/ {
        proxy_pass http://127.0.0.1:5100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 30;
        client_max_body_size 5m;
    }
}
NGINX
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/refcards /etc/nginx/sites-enabled/refcards
nginx -t && systemctl enable nginx && systemctl reload nginx
REMOTE

echo "  4/5  Устанавливаю systemd-сервис..."
ssh "$TARGET" 'bash -s' << 'REMOTE'
cat > /etc/systemd/system/refcards.service << 'SERVICE'
[Unit]
Description=Refcards backend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/refcards/backend
ExecStart=/usr/bin/python3 /opt/refcards/backend/server.py
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
SERVICE
chown -R www-data:www-data /opt/refcards
systemctl daemon-reload
systemctl enable refcards
systemctl restart refcards
REMOTE

echo "  5/5  Проверяю..."
sleep 3
ssh "$TARGET" 'bash -s' << 'REMOTE'
echo -n "      flask:  "; systemctl is-active refcards
echo -n "      nginx:  "; systemctl is-active nginx
echo -n "      api:    "; curl -s http://localhost:5100/api/health | grep -o '"ok":true' || echo "не отвечает"
REMOTE

IP=$(echo "$TARGET" | sed 's/.*@//')
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  Готово: http://$IP"
echo ""
echo "  Обновить после git pull:"
echo "  bash scripts/deploy.sh $TARGET"
echo ""
echo "  Логи:"
echo "  ssh $TARGET 'journalctl -u refcards -f'"
echo "══════════════════════════════════════════════════════════════"
