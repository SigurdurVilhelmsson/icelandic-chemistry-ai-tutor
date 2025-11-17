#!/bin/bash
# Renew SSL certificates
# This script should be run periodically (e.g., via cron)
# Add to crontab: 0 0 1 * * /path/to/renew_ssl.sh >> /var/log/ssl-renewal.log 2>&1

set -e

echo "================================================"
echo "  SSL Certificate Renewal"
echo "  $(date)"
echo "================================================"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "⚠️  This script must be run as root (use sudo)"
   exit 1
fi

# Renew certificates
echo "🔒 Checking and renewing SSL certificates..."
certbot renew --nginx --quiet

# Check if renewal was successful
if [ $? -eq 0 ]; then
    echo "✅ Certificate renewal completed successfully"

    # Reload nginx to use new certificates
    echo "🔄 Reloading nginx..."
    systemctl reload nginx

    echo "✅ Nginx reloaded with new certificates"

    # Show certificate expiration dates
    echo ""
    echo "Certificate status:"
    certbot certificates
else
    echo "❌ Certificate renewal failed!"
    exit 1
fi

echo ""
echo "================================================"
echo "  Renewal Complete - $(date)"
echo "================================================"
