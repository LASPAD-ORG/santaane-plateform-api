# Santaane API - Deployment on Coolify

This guide explains how to deploy the Santaane Platform API on Coolify using Docker Compose.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Deployment Steps](#deployment-steps)
- [Environment Variables Configuration](#environment-variables-configuration)
- [Domain & SSL Configuration](#domain--ssl-configuration)
- [Post-Deployment](#post-deployment)
- [Monitoring & Logs](#monitoring--logs)
- [Troubleshooting](#troubleshooting)
- [Scaling & Performance](#scaling--performance)

---

## Prerequisites

Before deploying to Coolify, ensure you have:

1. **Coolify Instance**: A running Coolify instance (self-hosted or cloud)
2. **Git Repository**: Your code pushed to a Git repository (GitHub, GitLab, etc.)
3. **Domain Name**: A domain pointing to your Coolify server
4. **SSL Certificate**: Coolify will automatically provision Let's Encrypt certificates

---

## Architecture Overview

The production stack consists of three services:

```
┌─────────────────────────────────────────────────┐
│                  Internet                       │
└────────────────┬────────────────────────────────┘
                 │
                 │ HTTPS (443)
                 ▼
         ┌───────────────┐
         │ Coolify Proxy │ (Traefik)
         │ + Let's Encrypt│
         └───────┬────────┘
                 │
                 │ HTTP (8000)
                 ▼
         ┌───────────────┐
         │   API Service │ (FastAPI + Uvicorn)
         │   Port 8000   │
         └───┬───────────┘
             │
             │ PostgreSQL Protocol
             ▼
         ┌───────────────┐
         │   PGBouncer   │ (Connection Pooler)
         │   Port 5432   │
         └───┬───────────┘
             │
             │ PostgreSQL Protocol
             ▼
         ┌───────────────┐
         │  PostgreSQL   │ (Database)
         │   Port 5432   │
         └───────────────┘
```

### Service Details

| Service | Image | Purpose | Exposed |
|---------|-------|---------|---------|
| **api** | Built from Dockerfile.prod | FastAPI application | Yes (via Coolify proxy) |
| **db** | postgres:16-alpine | PostgreSQL database | No (internal only) |
| **pgbouncer** | edoburu/pgbouncer | Connection pooling | No (internal only) |

---

## Deployment Steps

### Step 1: Create a New Resource in Coolify

1. Log in to your Coolify dashboard
2. Click **+ New Resource**
3. Select **Docker Compose** as the deployment type
4. Choose your Git source (GitHub, GitLab, etc.)

### Step 2: Configure the Resource

1. **Repository**: Select or add your Git repository
2. **Branch**: Choose `prod` or your production branch
3. **Docker Compose File**: Specify `docker-compose.prod.yml`
4. **Build Pack**: Select "Docker Compose"

### Step 3: Set Environment Variables

In Coolify's Environment Variables section, configure the following:

#### Required Variables (MUST be set)

These will appear with a red border in Coolify's UI if not configured:

```env
POSTGRES_PASSWORD=your-secure-database-password
SECRET_KEY=your-secure-jwt-secret-key
```

**Generate a secure SECRET_KEY:**
```bash
openssl rand -hex 32
```

#### Database Configuration

```env
DATABASE_URL=postgresql+psycopg2://postgres:your-password@pgbouncer:5432/santaane
POSTGRES_USER=postgres
POSTGRES_DB=santaane
```

#### Application Configuration

```env
APP_NAME=Santaane API
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

#### CORS Configuration

**Important**: Set this to your frontend domain(s)

```env
CORS_ORIGINS=https://app.yourdomain.com,https://www.yourdomain.com
```

For development/testing, you can use:
```env
CORS_ORIGINS=*
```

#### Optional Configuration

```env
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Step 4: Configure Domain

1. In Coolify, navigate to the **api** service
2. Click on **Domains**
3. Add your domain (e.g., `api.yourdomain.com`)
4. Coolify will automatically:
   - Configure Traefik reverse proxy
   - Issue SSL certificate via Let's Encrypt
   - Set up automatic HTTPS redirect

### Step 5: Deploy

1. Click **Deploy** in Coolify's UI
2. Monitor the build logs
3. Wait for all services to become healthy

Expected deployment time: 3-5 minutes (first build may take longer)

---

## Environment Variables Configuration

### Variables Detection

Coolify automatically detects environment variables from `docker-compose.prod.yml` and displays them in the UI. Variables are categorized as:

- **Required** (`:?` syntax): Must be set before deployment
- **With Defaults** (`:-` syntax): Pre-filled but editable
- **Optional**: Can be left empty

### Variable Precedence

1. Coolify UI variables (highest priority)
2. Variables in docker-compose.prod.yml
3. Default values in compose file

### Shared Variables

If you need to share variables across multiple deployments:

1. Create a shared variable in Coolify (Settings → Shared Variables)
2. Reference it in your compose file:
   ```yaml
   - MY_VAR={{environment.SHARED_VAR_NAME}}
   ```

---

## Domain & SSL Configuration

### DNS Setup

Before deploying, ensure your DNS is configured:

1. Add an **A record** pointing to your Coolify server's IP:
   ```
   api.yourdomain.com  →  123.45.67.89
   ```

2. Wait for DNS propagation (can take up to 48 hours, usually faster)

3. Verify DNS:
   ```bash
   dig api.yourdomain.com
   nslookup api.yourdomain.com
   ```

### SSL Certificate

Coolify automatically provisions SSL certificates using Let's Encrypt:

- Certificates are auto-renewed before expiration
- Supports wildcard certificates (if using Cloudflare DNS)
- HTTPS is enforced by default (HTTP → HTTPS redirect)

### Custom SSL Certificate

To use your own certificate:

1. Go to Coolify → Settings → Certificates
2. Upload your certificate files
3. Select the certificate in your service configuration

---

## Post-Deployment

### Verify Deployment

1. **Check Service Health**:
   ```bash
   curl https://api.yourdomain.com/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0"
   }
   ```

2. **Test API Documentation**:
   - Swagger UI: `https://api.yourdomain.com/docs`
   - ReDoc: `https://api.yourdomain.com/redoc`

3. **Check Database Connection**:
   - The API should successfully connect through PGBouncer
   - Migrations should run automatically on startup

### Initial Data Seeding

If you need to seed initial data:

1. Access the API container:
   ```bash
   # In Coolify, go to api service → Terminal
   ```

2. Run seeding commands:
   ```bash
   ./santaane seed-countries /path/to/slim-2.json
   ./santaane seed-cities /path/to/cities.json
   ```

   **Note**: You may need to upload JSON files to the container first.

---

## Monitoring & Logs

### View Logs

In Coolify UI:

1. Navigate to your resource
2. Click on a service (api, db, or pgbouncer)
3. Click **Logs** tab
4. View real-time or historical logs

### Log Levels

The API uses structured logging with the following levels:

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

Change log level via environment variable:
```env
LOG_LEVEL=DEBUG  # or INFO, WARNING, ERROR, CRITICAL
```

### Health Checks

The compose file includes health checks for all services:

| Service | Endpoint/Command | Interval | Timeout |
|---------|-----------------|----------|---------|
| **api** | `curl -f http://localhost:8000/health` | 30s | 10s |
| **db** | `pg_isready -U postgres` | 10s | 5s |
| **pgbouncer** | N/A (excluded from healthcheck) | - | - |

### Monitoring Best Practices

1. **Set up alerts** in Coolify for service failures
2. **Monitor resource usage** (CPU, memory, disk)
3. **Enable backup** for PostgreSQL data
4. **Check logs regularly** for errors or warnings

---

## Troubleshooting

### Common Issues

#### 1. Service Fails to Start

**Symptom**: API service shows as "unhealthy" or "exited"

**Solutions**:

1. Check logs for errors:
   ```
   Coolify → api service → Logs
   ```

2. Verify environment variables are set correctly

3. Ensure database connection is working:
   ```bash
   # In API container
   pg_isready -h db -p 5432 -U postgres
   ```

#### 2. Database Connection Failed

**Symptom**: `FATAL: password authentication failed`

**Solutions**:

1. Verify `POSTGRES_PASSWORD` matches in:
   - API service (`DATABASE_URL`)
   - db service
   - pgbouncer service

2. Check if database is ready:
   ```bash
   # In db container
   pg_isready -U postgres
   ```

#### 3. Migrations Fail

**Symptom**: API container exits with "Migration failed!"

**Solutions**:

1. Check Alembic configuration:
   ```bash
   # In API container
   alembic current
   alembic history
   ```

2. Manually run migrations:
   ```bash
   alembic upgrade head
   ```

3. Check database connectivity

#### 4. CORS Errors

**Symptom**: Frontend can't connect to API (CORS policy errors in browser)

**Solutions**:

1. Update `CORS_ORIGINS` environment variable:
   ```env
   CORS_ORIGINS=https://your-frontend.com
   ```

2. Restart the API service after changing CORS settings

#### 5. SSL Certificate Issues

**Symptom**: "Your connection is not private" or certificate errors

**Solutions**:

1. Wait for Let's Encrypt certificate provisioning (can take a few minutes)

2. Check DNS is pointing correctly:
   ```bash
   dig api.yourdomain.com
   ```

3. Verify domain is set in Coolify UI

4. Check Traefik logs in Coolify

---

## Scaling & Performance

### Horizontal Scaling

The current setup runs with 4 Uvicorn workers (see `entrypoint.sh`). To adjust:

1. Modify `entrypoint.sh`:
   ```bash
   exec uvicorn app.main:app \
     --host 0.0.0.0 \
     --port 8000 \
     --workers 8 \  # Increase workers
     --log-level ${LOG_LEVEL:-info}
   ```

2. Redeploy the stack

**Worker Calculation**: `(2 x CPU cores) + 1`

### Database Connection Pooling

PGBouncer is configured for optimal performance:

```env
POOL_MODE=transaction       # Transaction-level pooling
MAX_CLIENT_CONN=100         # Max client connections
DEFAULT_POOL_SIZE=20        # Connections per database
MIN_POOL_SIZE=10            # Minimum pool size
RESERVE_POOL_SIZE=10        # Reserved connections
```

Adjust these in `docker-compose.prod.yml` if needed.

### Volume Persistence

PostgreSQL data is persisted in a Docker volume (`pgdata`):

- Data survives container restarts
- Coolify automatically manages volume lifecycle
- **Important**: Set up regular backups (see below)

### Backup Strategy

#### Automated Backups

Coolify doesn't have built-in database backups. Set up external backups:

1. **Using pg_dump** (recommended):
   ```bash
   # Create backup script
   docker exec santaane_db pg_dump -U postgres santaane > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Schedule with cron**:
   ```bash
   0 2 * * * /path/to/backup-script.sh
   ```

3. **Store backups externally** (S3, Backblaze, etc.)

#### Manual Backup

```bash
# In Coolify terminal
./santaane db-dump
```

#### Restore from Backup

```bash
# In Coolify terminal
./santaane db-restore
```

---

## Security Checklist

Before going to production:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Set `DEBUG=False`
- [ ] Configure `CORS_ORIGINS` to specific domains (not `*`)
- [ ] Enable HTTPS (automatic with Coolify)
- [ ] Set up database backups
- [ ] Review and restrict API rate limiting (if applicable)
- [ ] Use environment-specific .env files
- [ ] Never commit `.env` files to version control
- [ ] Set up monitoring and alerting
- [ ] Review Docker image security (done via multi-stage build)

---

## Additional Resources

- [Coolify Documentation](https://coolify.io/docs)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)
- [Uvicorn Worker Processes](https://www.uvicorn.org/deployment/#running-with-gunicorn)

---

## Support

If you encounter issues:

1. Check Coolify logs
2. Review this troubleshooting guide
3. Consult Coolify community/Discord
4. Open an issue in your project repository

---

**Deployment Date**: {{ deployment_date }}
**Last Updated**: 2025-12-26
