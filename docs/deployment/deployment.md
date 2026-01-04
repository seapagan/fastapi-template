# Deployment

## Production Environment Checklist

Before deploying to production, ensure you've configured all critical settings properly. Missing or incorrect configuration can lead to security vulnerabilities or broken functionality.

### Critical Security Settings

!!! danger "Required - Security Risk if Skipped"
    These settings are **critical** for security. Never deploy without configuring them.

- **SECRET_KEY** ⚠️ **MUST CHANGE**
  - Generate a new secret key: `openssl rand -hex 32`
  - **Never** use the default or example value
  - Keep this secret - don't commit to version control
  - Used for JWT token signing and session security

- **CORS_ORIGINS**
  - For browser clients, set to your actual frontend domain(s)
  - For public APIs using Bearer tokens, `*` is acceptable but will log a warning
  - Example: `CORS_ORIGINS=https://app.example.com,https://www.example.com`
  - Multiple origins separated by commas

### Database Configuration

- **DB_USER**, **DB_PASSWORD**, **DB_NAME** - Must match your production database
- **DB_ADDRESS**, **DB_PORT** - Point to your production database server
- **Database must exist** - Create it before running migrations
- **Run migrations** - `api-admin db init --force` (see [Database Migration Strategy](#database-migration-strategy) below)
- Consider using connection pooling for better performance
- Enable SSL/TLS for database connections if available

### Email Settings (Required for Password Reset)

!!! warning "Email Required in Production"
    Password reset and verification emails won't work without proper email configuration.

- **MAIL_USERNAME**, **MAIL_PASSWORD** - SMTP credentials
- **MAIL_FROM** - Sender email address (e.g., `noreply@yourdomain.com`)
- **MAIL_SERVER**, **MAIL_PORT** - SMTP server details (usually port 587 for TLS)
- **MAIL_FROM_NAME** - Friendly sender name
- **Test email functionality** before going live

### Admin Panel Configuration

- **ADMIN_PAGES_ENABLED** - Set to `True` if using admin panel
- **ADMIN_PAGES_ENCRYPTION_KEY** - Generate with:
  ```bash
  python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
  ```
  - Leave empty to auto-generate (regenerates on each restart - sessions lost)
  - Set explicitly for persistent sessions across restarts
- **ADMIN_PAGES_TIMEOUT** - Session timeout in seconds (default: 86400 = 24 hours)

### Observability & Monitoring

- **METRICS_ENABLED** - Set to `true` for production monitoring
  - Enables `/metrics` endpoint for Prometheus scraping
  - Essential for tracking performance and errors
  - See [Metrics Documentation](../usage/metrics.md)
- Configure your monitoring system to scrape `/metrics`
- Set up health check monitoring on `/heartbeat`

### Logging Configuration

- **LOG_LEVEL** - Set to `INFO` or `WARNING` in production (not `DEBUG`)
- **LOG_PATH** - Ensure path exists and is writable
- **LOG_ROTATION** - Consider `1 day` or `500 MB` for production
- **LOG_RETENTION** - Balance between disk space and audit requirements
- **LOG_COMPRESSION** - Use `zip` or `gz` to save disk space
- **LOG_CATEGORIES** - Recommend `ERRORS,AUTH,DATABASE,REQUESTS` for production

### Optional Settings

- **BASE_URL** - Your production API URL (e.g., `https://api.example.com`)
- **FRONTEND_URL** - If using custom frontend for password reset
- **API_ROOT** - If serving API from subpath (e.g., `/api/v1`)
- **ACCESS_TOKEN_EXPIRE_MINUTES** - Default 120 (2 hours), adjust as needed

### Pre-Deployment Verification

Before going live, verify:

- [ ] SECRET_KEY is unique and secure
- [ ] Database is accessible and migrated
- [ ] Email sending works (test password reset)
- [ ] CORS is configured for your frontend domain(s)
- [ ] Admin panel accessible (if enabled)
- [ ] Metrics endpoint returns data (if enabled)
- [ ] Logs are being written correctly
- [ ] At least one admin user exists
- [ ] SSL/TLS certificate is valid
- [ ] Health check endpoint (`/heartbeat`) responding
- [ ] All external dependencies (database, SMTP) are accessible

## Deploying to Production

There are quite a few ways to deploy a FastAPI app to production. There is a
very good discussion about this on the FastAPI [Deployment
Guide][fastapi-deployment]{: target="_blank"} which covers
using Uvicorn, Gunicorn and Containers.

!!! info "Environment Setup"
    Whichever method you choose, you still need to set up a virtual environment,
    install all the dependencies, setup your `.env` file (or use Environment
    variables if your hosting provider uses these - for example Railway or Heroku)
    and set up and migrate your Database.

## Database Migration Strategy

Proper database migration management is crucial for production deployments.

### Initial Deployment

1. **Create the database** on your production server:
   ```bash
   psql -U postgres
   CREATE DATABASE your_production_db;
   ```

2. **Run migrations** to create tables:
   ```bash
   api-admin db init --force
   ```

3. **Create your first admin user**:
   ```bash
   api-admin user create --admin
   ```

### Updating an Existing Deployment

When deploying code changes that include new migrations:

!!! danger "Critical - Do NOT use 'db init' on existing databases"
    **Never** run `api-admin db init --force` on an existing production database -
    it will **clear all data**! Use `api-admin db upgrade` instead.

1. **Backup your database first** (critical!):
   ```bash
   pg_dump -U postgres your_production_db > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Test migrations locally** on a copy of production data if possible

3. **Put application in maintenance mode** (if zero-downtime is not required)

4. **Pull latest code** and install dependencies:
   ```bash
   git pull origin main
   uv sync  # or pip install -r requirements.txt
   ```

5. **Run migrations** (applies new migrations only):
   ```bash
   api-admin db upgrade
   ```

6. **Restart the application**

7. **Verify** the application is working correctly

### Rollback Procedure

If a migration fails or causes issues:

1. **Restore from backup**:
   ```bash
   psql -U postgres your_production_db < backup_YYYYMMDD_HHMMSS.sql
   ```

2. **Revert to previous code version**:
   ```bash
   git checkout <previous-commit>
   uv sync
   ```

3. **Restart the application**

### Best Practices

- **Always backup** before running migrations
- **Test migrations** on a staging environment first
- **Review migration files** generated by Alembic before deployment
- **Plan for rollback** - have a tested rollback procedure ready
- **Monitor logs** during and after migration
- Consider **scheduled maintenance windows** for complex migrations

## Managed Platform Options

These platforms offer straightforward FastAPI deployment with managed infrastructure:

- **[Railway](https://railway.app/)** - Simple deploys from GitHub, generous free tier, automatic HTTPS
- **[Fly.io](https://fly.io/)** - Edge deployment, global distribution, Dockerfile-based
- **[Render](https://render.com/)** - Auto-deploy from Git, managed PostgreSQL, free tier available
- **[DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform)** - Managed platform with databases and scaling
- **[Heroku](https://www.heroku.com/)** - Classic PaaS, easy deployment, many add-ons available
- **[Vercel](https://vercel.com/)** - Serverless deployment, edge functions (requires ASGI adapter)

All support PostgreSQL databases and environment variables. Refer to their documentation for FastAPI-specific deployment instructions.

## Self-Hosted Deployment

### Nginx

My Personal preference is to serve with Gunicorn, using uvicorn workers behind
an Nginx proxy, though this does require you having your own server. There is a
pretty decent tutorial on this at [Vultr][vultr]{: target="_blank"}.

### AWS Lambda

For deploying to AWS Lambda with API Gateway, there is a really excellent
Medium post (and it's followup) [Here][medium]{: target="_blank"}

### AWS Elastic Beanstalk

For AWS Elastic Beanstalk there is a very comprehensive tutorial at
[testdriven.io][testdriven]{: target="_blank"}

### Docker Container

Deploy a Docker container or Kubernetes cluster. There are many services which
allow this including AWS, Google Cloud and more. See [Develop with
Docker](../development/docker.md) in this documentation for how to containerize
this project, and the
[Offical FastAPI docs section][fastapi-docker]{: target="_blank"}
for more information.

[vultr]:  https://www.vultr.com/docs/how-to-deploy-fastapi-applications-with-gunicorn-and-nginx-on-ubuntu-20-04/
[medium]: https://medium.com/towards-data-science/fastapi-aws-robust-api-part-1-f67ae47390f9
[testdriven]: https://testdriven.io/blog/fastapi-elastic-beanstalk/
[fastapi-docker]: https://fastapi.tiangolo.com/deployment/docker/
[fastapi-deployment]: https://fastapi.tiangolo.com/deployment/
