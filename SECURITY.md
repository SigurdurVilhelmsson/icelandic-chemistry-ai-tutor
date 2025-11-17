# Security Policy

## Security Features

### Network Security

1. **Backend Isolation**
   - Backend exposed only to `127.0.0.1:8000`
   - Not directly accessible from the internet
   - All traffic goes through nginx reverse proxy

2. **Firewall Configuration**
   ```bash
   # Recommended UFW rules
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

### SSL/TLS Configuration

1. **Certificate Management**
   - Let's Encrypt certificates
   - TLS 1.2 and 1.3 only
   - Strong cipher suites
   - SSL stapling enabled
   - HSTS with preload

2. **Certificate Renewal**
   - Automatic renewal via certbot timer
   - Manual renewal: `sudo certbot renew`
   - Monitoring: `sudo certbot certificates`

### HTTP Security Headers

All responses include:

- `Strict-Transport-Security`: Forces HTTPS for 1 year
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME sniffing
- `X-XSS-Protection`: Enables browser XSS protection
- `Content-Security-Policy`: Restricts resource loading
- `Referrer-Policy`: Controls referrer information
- `Permissions-Policy`: Restricts browser features

### Rate Limiting

1. **API Endpoints** (`/ask`)
   - 10 requests/second per IP
   - Burst: 20 requests
   - 429 status on limit exceeded

2. **General Traffic**
   - 30 requests/second per IP
   - Burst: 50 requests

### CORS Configuration

- Configured in `backend/.env`
- Default: localhost only
- Production: specific domain only
- No wildcard (*) in production

### Authentication & Authorization

**Current Status**: No authentication implemented

**Recommended for Production**:
- JWT tokens
- API key authentication
- Rate limiting per user
- OAuth2 integration

### Input Validation

1. **Backend Validation**
   - Pydantic models for request validation
   - Type checking on all inputs
   - Length limits on text fields

2. **Recommended Additions**:
   - Input sanitization
   - SQL injection prevention (if using SQL)
   - XSS prevention
   - Command injection prevention

### Docker Security

1. **Container Isolation**
   - Non-root user (TODO)
   - Read-only root filesystem (TODO)
   - No privileged mode
   - Limited capabilities

2. **Resource Limits**
   ```yaml
   # Add to docker-compose.yml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

### Environment Variables

1. **Secrets Management**
   - Never commit `.env` files
   - Use `.env.example` for templates
   - Store production secrets securely
   - Rotate API keys regularly

2. **Required Secrets**:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
   - Database credentials (if applicable)

### File Permissions

```bash
# Nginx configuration
sudo chmod 644 /etc/nginx/nginx.conf
sudo chmod 644 /etc/nginx/sites-available/chemistry-ai

# SSL certificates
sudo chmod 644 /etc/letsencrypt/live/*/fullchain.pem
sudo chmod 600 /etc/letsencrypt/live/*/privkey.pem

# Application files
chmod 755 /var/www/chemistry-ai
chmod 644 /var/www/chemistry-ai/frontend/dist/*

# Scripts
chmod 700 scripts/*.sh

# Environment files
chmod 600 backend/.env
```

### Logging and Monitoring

1. **Access Logs**
   - Location: `/var/log/nginx/chemistry-ai-access.log`
   - Rotation: Configured via logrotate
   - Retention: 14 days

2. **Error Logs**
   - Location: `/var/log/nginx/chemistry-ai-error.log`
   - Backend: Docker logs
   - Monitor for suspicious activity

3. **Monitoring Recommendations**
   - Log analysis tools (fail2ban)
   - Uptime monitoring
   - SSL expiry alerts
   - Resource usage monitoring

### Backup and Recovery

1. **What to Backup**
   - Nginx configuration files
   - SSL certificates
   - Environment variables
   - Database/ChromaDB data
   - Application code

2. **Backup Script**
   ```bash
   #!/bin/bash
   BACKUP_DIR="/backups/$(date +%Y%m%d)"
   mkdir -p $BACKUP_DIR

   # Config files
   cp -r /etc/nginx/sites-available $BACKUP_DIR/
   cp backend/.env $BACKUP_DIR/

   # SSL certificates
   cp -r /etc/letsencrypt $BACKUP_DIR/

   # Database
   docker-compose exec backend tar -czf /tmp/chroma_backup.tar.gz /app/data/chroma_db
   docker cp <container>:/tmp/chroma_backup.tar.gz $BACKUP_DIR/
   ```

## Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead, email security concerns to: [your-security-email@example.com]

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours.

## Security Checklist for Production

Before deploying to production:

### Infrastructure
- [ ] Firewall configured (only ports 22, 80, 443)
- [ ] SSH key-based authentication only
- [ ] Root login disabled
- [ ] Regular system updates scheduled
- [ ] Fail2ban installed and configured
- [ ] Backups configured and tested

### Application
- [ ] All secrets in environment variables
- [ ] No hardcoded credentials
- [ ] CORS configured for production domain only
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies up to date
- [ ] Security headers configured

### SSL/TLS
- [ ] Valid SSL certificate installed
- [ ] Auto-renewal configured
- [ ] HSTS enabled
- [ ] TLS 1.2+ only
- [ ] Strong cipher suites
- [ ] SSL Labs A+ rating

### Monitoring
- [ ] Log rotation configured
- [ ] Error monitoring in place
- [ ] Uptime monitoring active
- [ ] SSL expiry alerts set up
- [ ] Resource usage monitoring
- [ ] Security scanning scheduled

### Docker
- [ ] Images from trusted sources
- [ ] Regular image updates
- [ ] No privileged containers
- [ ] Resource limits configured
- [ ] Non-root user in containers
- [ ] Minimal base images

### Nginx
- [ ] Server tokens hidden
- [ ] Access to hidden files blocked
- [ ] Request size limits
- [ ] Timeout configurations
- [ ] Buffer overflow protection
- [ ] DDoS protection (rate limiting)

## Security Updates

### Regular Maintenance

**Weekly:**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
cd backend
docker-compose pull
docker-compose up -d
```

**Monthly:**
```bash
# Review security logs
sudo journalctl -u nginx --since "1 month ago" | grep -i "error\|attack\|denied"

# Update dependencies
cd frontend && npm audit fix
cd backend && pip list --outdated

# Rotate credentials (if needed)
```

**Quarterly:**
```bash
# Security audit
# - Review all configurations
# - Test backups
# - Penetration testing
# - Dependency security scan
```

## Known Security Considerations

1. **No Authentication**
   - Current implementation has no user authentication
   - API is open to anyone
   - Recommend implementing JWT or API keys before production

2. **AI Model Prompts**
   - Potential for prompt injection
   - Implement input filtering
   - Rate limit per user/IP

3. **Third-Party APIs**
   - Dependent on Anthropic/OpenAI security
   - API keys must be protected
   - Monitor for unauthorized usage

4. **Data Storage**
   - ChromaDB data not encrypted at rest
   - Consider encryption for sensitive data
   - Implement data retention policies

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Mozilla Observatory](https://observatory.mozilla.org/)
- [SSL Labs](https://www.ssllabs.com/ssltest/)
- [Security Headers](https://securityheaders.com/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Nginx Security](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)

## Compliance

Ensure compliance with:
- GDPR (if handling EU user data)
- Local data protection laws
- Educational data privacy requirements
- API provider terms of service

## Incident Response

In case of security incident:

1. **Immediate Actions**
   - Disconnect affected systems
   - Preserve logs and evidence
   - Notify stakeholders
   - Change all credentials

2. **Investigation**
   - Determine scope of breach
   - Identify attack vector
   - Document timeline

3. **Remediation**
   - Patch vulnerabilities
   - Update security measures
   - Test fixes

4. **Post-Incident**
   - Update security policies
   - Improve monitoring
   - Train team
   - Document lessons learned

## Contact

For security concerns: [your-security-email@example.com]

For general issues: [GitHub Issues](https://github.com/your-repo/issues)

---

**Last Updated**: 2025-11-17
**Next Review**: 2025-12-17
