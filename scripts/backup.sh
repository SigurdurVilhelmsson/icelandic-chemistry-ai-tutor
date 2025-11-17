#!/bin/bash
# Backup Chroma database and configuration

set -e

BACKUP_DIR="$HOME/backups/chemistry-ai"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="chemistry-ai-backup-${DATE}"

echo "💾 Creating backup: $BACKUP_NAME"

# Create backup directory
mkdir -p $BACKUP_DIR

# Stop backend container
echo "⏸️  Stopping backend..."
docker-compose -f backend/docker-compose.yml stop backend

# Create backup
echo "📦 Backing up data..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" \
    backend/data/chroma_db \
    backend/.env \
    frontend/.env

# Restart backend
echo "▶️  Restarting backend..."
docker-compose -f backend/docker-compose.yml start backend

echo "✅ Backup created: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# Keep only last 7 backups
cd $BACKUP_DIR
ls -t chemistry-ai-backup-*.tar.gz | tail -n +8 | xargs -r rm
echo "📦 Backups retained: $(ls -1 chemistry-ai-backup-*.tar.gz 2>/dev/null | wc -l)"

# Create backup log
echo "$(date): Backup ${BACKUP_NAME} completed" >> backup.log
