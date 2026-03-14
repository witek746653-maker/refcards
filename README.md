# Refcards

Редактор справочных карточек с экспортом в A4 PDF.

## Структура

```
refcards/
├── backend/
│   ├── server.py          ← Flask API + WeasyPrint + SQLite
│   └── requirements.txt
├── frontend/
│   └── index.html         ← весь UI
├── scripts/
│   ├── deploy.sh          ← первый деплой на сервер (один раз)
│   ├── push.sh            ← отправить изменения на сервер
│   └── backup-github.sh   ← сохранить копию на GitHub
└── README.md
```

## Рабочий процесс

```
Правишь файлы локально
        ↓
bash scripts/push.sh root@155.212.185.27    ← загружаешь на сервер
        ↓
bash scripts/backup-github.sh   ← сохраняешь копию на GitHub (отдельно)
```

**Золотое правило:** файлы на сервере никогда не правятся напрямую.
Все изменения — только с твоего компьютера.

---

## Первый запуск (один раз)

```bash
bash scripts/deploy.sh root@155.212.185.27
```

Устанавливает nginx, systemd, зависимости Python.

## Обновление после правок

```bash
bash scripts/push.sh root@YOUR_IP
```

Синхронизирует `backend/` и `frontend/` на сервер через rsync,
перезапускает сервис. База данных (`refcards.db`) не трогается.

## Бэкап на GitHub

```bash
bash scripts/backup-github.sh "что изменил"
```

Делай когда хочешь — хоть после каждой правки, хоть раз в неделю.

---

## Локальная разработка

```bash
cd backend
pip3 install -r requirements.txt --break-system-packages
REFCARDS_FRONTEND=../frontend python3 server.py
# → http://localhost:5100
```

## Бэкап базы данных

```bash
scp root@155.212.185.27:/opt/refcards/backend/refcards.db ./backup-$(date +%Y%m%d).db
```

## Логи сервера

```bash
ssh root@155.212.185.27 'journalctl -u refcards -f'
```
