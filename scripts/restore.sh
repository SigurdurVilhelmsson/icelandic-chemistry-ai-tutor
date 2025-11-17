#!/bin/bash
# Restore from backup

set -e

BACKUP_DIR="$HOME/backups/chemistry-ai"

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup-file>"
    echo ""
    echo "Available backups:"
    ls -1 $BACKUP_DIR/chemistry-ai-backup-*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will overwrite current data!"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Stop backend
echo "⏸️  Stopping backend..."
docker-compose -f backend/docker-compose.yml stop backend

# Backup current data (safety)
SAFETY_BACKUP="backend/data/chroma_db.before_restore.$(date +%Y%m%d_%H%M%S)"
echo "💾 Safety backup: $SAFETY_BACKUP"
mv backend/data/chroma_db $SAFETY_BACKUP

# Extract backup
echo "📂 Restoring from backup..."
tar -xzf $BACKUP_FILE

# Restart backend
echo "▶️  Restarting backend..."
docker-compose -f backend/docker-compose.yml start backend

# Wait for health check
echo "⏳ Checking health..."
sleep 5
curl -f http://localhost:8000/health || {
    echo "❌ Health check failed after restore!"
    exit 1
}

echo "✅ Restore complete!"
echo "⚠️  Previous data saved to: $SAFETY_BACKUP"
