# Icelandic Chemistry AI Tutor

An AI-powered chemistry tutor designed for Icelandic students, featuring a React frontend, FastAPI backend, and production-ready nginx deployment.

## Features

- **AI-Powered Tutoring**: Leverages Anthropic Claude and OpenAI for intelligent chemistry assistance
- **Icelandic Language Support**: Native support for Icelandic with fallback to English
- **Production Ready**: Complete nginx configuration with SSL/TLS
- **Dockerized Backend**: Easy deployment with Docker Compose
- **Security Hardened**: Rate limiting, CORS, security headers, and best practices

## Quick Start

### Development

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd icelandic-chemistry-ai-tutor
   ```

2. **Start the backend:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your API keys
   docker-compose up -d
   ```

3. **Start the frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Visit:** `http://localhost:5173`

### Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete production deployment instructions.

**Quick production setup:**
```bash
# 1. Setup nginx
sudo ./scripts/setup_nginx.sh

# 2. Configure environment
cd backend
cp .env.example .env
nano .env  # Add your API keys

# 3. Deploy everything
cd ..
./scripts/complete_deploy.sh

# 4. Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Architecture

```
┌─────────────────┐
│  Linode Server  │
│  (Ubuntu 24.04) │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼───┐  ┌──▼──────┐
│ Nginx │  │ FastAPI │
│ :443  │─▶│ :8000   │
└───────┘  └─────────┘
    │           │
Frontend    Backend+AI
```

## Project Structure

```
icelandic-chemistry-ai-tutor/
├── nginx/                      # Nginx configuration
│   ├── nginx.conf              # Main nginx config
│   ├── chemistry-ai.conf       # Site config
│   └── ssl/                    # SSL certificates
├── scripts/                    # Deployment scripts
│   ├── setup_nginx.sh          # Initial setup
│   ├── build_and_deploy.sh     # Frontend deployment
│   ├── renew_ssl.sh            # SSL renewal
│   └── complete_deploy.sh      # Full deployment
├── backend/                    # FastAPI backend
│   ├── src/
│   │   └── main.py             # Main application
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # React frontend
│   ├── src/
│   ├── dist/                   # Build output
│   └── package.json
└── DEPLOYMENT.md               # Deployment guide
```

## API Endpoints

### Backend (FastAPI)

- `GET /health` - Health check
- `POST /ask` - Ask a chemistry question
- `GET /docs` - API documentation (Swagger)
- `GET /redoc` - API documentation (ReDoc)

**Example request:**
```bash
curl -X POST https://your-domain.com/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Hvað er efnatengi?",
    "language": "is"
  }'
```

## Configuration

### Environment Variables (Backend)

Create `backend/.env`:
```env
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ALLOWED_ORIGINS=https://your-domain.com
LOG_LEVEL=INFO
```

### Nginx Configuration

Update `nginx/chemistry-ai.conf`:
- Replace `your-domain.com` with your actual domain
- Adjust rate limiting if needed
- Configure SSL certificate paths

## Security Features

- **SSL/TLS**: Let's Encrypt certificates with auto-renewal
- **Rate Limiting**: API and general request limits
- **CORS**: Configured allowed origins
- **Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- **Network Isolation**: Backend exposed only to localhost
- **Docker Security**: Non-root user, limited resources

## Monitoring

### Logs

**Backend:**
```bash
cd backend
docker-compose logs -f
```

**Nginx:**
```bash
sudo tail -f /var/log/nginx/chemistry-ai-access.log
sudo tail -f /var/log/nginx/chemistry-ai-error.log
```

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend (through nginx)
curl https://your-domain.com/health
```

## Deployment Scripts

### Complete Deployment
```bash
./scripts/complete_deploy.sh
```
Deploys both backend and frontend, runs health checks.

### Frontend Only
```bash
./scripts/build_and_deploy.sh
```
Builds and deploys just the React frontend.

### SSL Renewal
```bash
sudo ./scripts/renew_ssl.sh
```
Manually renew SSL certificates (auto-renewal is configured).

## Troubleshooting

### Frontend not loading
```bash
# Check nginx logs
sudo tail -f /var/log/nginx/chemistry-ai-error.log

# Verify files exist
ls -la /var/www/chemistry-ai/frontend/dist/

# Test nginx config
sudo nginx -t
```

### Backend not responding
```bash
# Check if running
curl http://localhost:8000/health

# Check logs
cd backend && docker-compose logs --tail=50

# Restart
docker-compose restart
```

### SSL issues
```bash
# Check certificate
sudo certbot certificates

# Renew
sudo certbot renew

# Reload nginx
sudo systemctl reload nginx
```

## Development

### Backend Development

```bash
cd backend
docker-compose up -d
# Edit src/main.py
docker-compose restart
```

### Frontend Development

```bash
cd frontend
npm run dev
# Visit http://localhost:5173
```

## Testing

### Test Backend
```bash
cd backend
docker-compose exec backend pytest
```

### Test Frontend
```bash
cd frontend
npm test
```

### Integration Test
```bash
# Start everything
./scripts/complete_deploy.sh

# Test health endpoint
curl https://your-domain.com/health

# Test API
curl -X POST https://your-domain.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See [LICENSE](./LICENSE) file for details.

## Support

For deployment issues, see [DEPLOYMENT.md](./DEPLOYMENT.md).

For application issues, check:
- Backend logs: `docker-compose logs`
- Nginx logs: `/var/log/nginx/chemistry-ai-*.log`
- Frontend console: Browser developer tools

## Roadmap

- [ ] Add user authentication
- [ ] Implement conversation history
- [ ] Add more chemistry topics
- [ ] Support for chemical formulas and equations
- [ ] Interactive molecular visualizations
- [ ] Multi-language support expansion
- [ ] Mobile application

## Tech Stack

- **Frontend**: React, Vite, Axios
- **Backend**: FastAPI, Python 3.11
- **AI**: Anthropic Claude, OpenAI GPT
- **Database**: ChromaDB (vector store)
- **Web Server**: Nginx
- **Containers**: Docker, Docker Compose
- **SSL**: Let's Encrypt (Certbot)

## Performance

- **Response Time**: < 2s average
- **Uptime**: 99.9% target
- **Concurrent Users**: 100+
- **Rate Limits**: 10 req/s per IP on /ask endpoint

## Credits

Built with modern web technologies and AI models for Icelandic chemistry education.

---

**Made with ❤️ for Icelandic students**
