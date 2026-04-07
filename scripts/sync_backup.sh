#!/bin/bash
# Sync database backup from Windows machine
# Usage: ./scripts/sync_backup.sh [import]
#   No args  → just downloads the backup
#   import   → downloads and imports into local MySQL

WINDOWS_IP="192.168.1.237"
WINDOWS_PORT="8000"
BACKUP_DIR="./backups"
BACKUP_URL="http://${WINDOWS_IP}:${WINDOWS_PORT}/backup/"

mkdir -p "$BACKUP_DIR"

echo "Downloading backup from ${BACKUP_URL}..."
FILENAME=$(curl -sS -w '%{filename_effective}' -OJ "$BACKUP_URL" --output-dir "$BACKUP_DIR")

if [ $? -ne 0 ]; then
    echo "Error: Could not connect to ${BACKUP_URL}"
    echo "Make sure the Windows machine is running and accessible."
    exit 1
fi

FILEPATH="${BACKUP_DIR}/${FILENAME}"
echo "Saved: ${FILEPATH}"

# Decompress to show size info
SQL_FILE="${FILEPATH%.gz}"
gunzip -k "$FILEPATH"
echo "Decompressed: ${SQL_FILE} ($(du -h "$SQL_FILE" | cut -f1))"

if [ "$1" = "import" ]; then
    echo ""
    echo "Importing into local database..."
    # Adjust these to match your local Mac DB settings
    DB_NAME="${DB_NAME:-tiktok_db}"
    DB_USER="${DB_USER:-root}"
    DB_HOST="${DB_HOST:-127.0.0.1}"
    DB_PORT="${DB_PORT:-3306}"

    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p "$DB_NAME" < "$SQL_FILE"

    if [ $? -eq 0 ]; then
        echo "Import complete."
    else
        echo "Import failed. You can import manually with:"
        echo "  mysql -u root -p tiktok_db < ${SQL_FILE}"
    fi
fi
