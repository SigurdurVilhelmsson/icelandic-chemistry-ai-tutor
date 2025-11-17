#!/bin/bash
# Renew SSL certificates

set -e

echo "🔐 Renewing SSL certificates..."

# Renew certificates
sudo certbot renew --nginx --quiet

# Reload nginx
sudo systemctl reload nginx

echo "✅ SSL certificates renewed"
echo "Next expiry: $(sudo certbot certificates | grep 'Expiry Date')"

# Log renewal
echo "$(date): SSL certificates renewed" >> /var/log/ssl-renewal.log
