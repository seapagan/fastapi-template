# Troubleshooting

Common issues and their solutions when working with the FastAPI Template.

## Database Issues

### Database Connection Refused

**Error:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server: Connection refused
```

**Solutions:**

1. **Check PostgreSQL is running:**
   ```bash
   # Linux/Mac
   sudo systemctl status postgresql

   # Using Docker
   docker ps | grep postgres
   ```

2. **Verify database exists:**
   ```bash
   psql -U postgres -l
   # If missing, create it:
   psql -U postgres
   CREATE DATABASE fastapi_template;
   ```

3. **Check `.env` settings match your database:**
   - `DB_USER`, `DB_PASSWORD` must match PostgreSQL credentials
   - `DB_ADDRESS` should be `localhost` for local dev
   - `DB_PORT` should be `5432` (default PostgreSQL port)

### Migration Errors

**Error:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxxxx'
```

**Solution:** Your migration history is out of sync. For development:
```bash
# Clear and reinitialize (WARNING: Deletes all data)
api-admin db init --force
```

For production, see [Database Migration Strategy](deployment/deployment.md#database-migration-strategy).

## Application Startup Issues

### Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

1. **Find process using port 8000:**
   ```bash
   # Linux/Mac
   lsof -i :8000

   # Kill the process
   kill -9 <PID>
   ```

2. **Use a different port:**
   ```bash
   api-admin serve --port 8080
   ```

### Module Not Found Errors

**Error:**
```
ModuleNotFoundError: No module named 'app'
```

**Solutions:**

1. **Activate virtual environment:**
   ```bash
   # Using uv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows

   # Using pip/venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

2. **Reinstall dependencies:**
   ```bash
   uv sync  # or pip install -r requirements.txt
   ```

## Email Issues

### Password Reset Not Sending Emails

**Problem:** Clicked "forgot password" but no email arrives.

**Solutions:**

1. **Check email is configured in `.env`:**
   - All `MAIL_*` variables must be set
   - Test with: `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`

2. **Check spam folder** - emails may be flagged as spam

3. **Verify SMTP credentials:**
   ```bash
   # Test connection manually
   telnet smtp.gmail.com 587
   ```

4. **For development:** Check application logs at `LOG_PATH` for email errors

### Email Settings Valid But Still Not Working

**Common issues:**

- **Gmail:** Requires "App Password" not your regular password
- **Office365:** May require OAuth2 instead of SMTP
- **2FA enabled:** Need app-specific password
- Check `MAIL_STARTTLS` and `MAIL_SSL_TLS` settings match your provider

## Authentication Issues

### "That token is Invalid" on Every Request

**Causes:**

1. **SECRET_KEY changed** - All existing tokens invalidated
   - Expected after changing SECRET_KEY
   - Users must login again

2. **Clock skew** - Server time incorrect
   ```bash
   # Check server time
   date
   ```

3. **Token expired** - Default 2 hours
   - Use refresh token to get new access token
   - See [Authentication Flow](quick-start.md#authenticate-to-access-protected-endpoints)

### Cannot Access Admin Panel

**Error:** 404 Not Found on `/admin`

**Solutions:**

1. **Check admin panel is enabled in `.env`:**
   ```bash
   ADMIN_PAGES_ENABLED=True
   ```

2. **Verify route in settings** (if customized):
   ```bash
   ADMIN_PAGES_ROUTE=/admin
   ```

3. **Restart application** after changing settings

## Metrics Issues

### `/metrics` Returns 404

**Cause:** Metrics not enabled.

**Solution:** Add to `.env`:
```bash
METRICS_ENABLED=true
```

Restart the application.

### Prometheus Not Scraping Metrics

**Solutions:**

1. **Check `/metrics` endpoint is accessible:**
   ```bash
   curl http://localhost:8000/metrics
   ```

2. **Verify Prometheus configuration** has correct target:
   ```yaml
   scrape_configs:
     - job_name: 'fastapi-template'
       static_configs:
         - targets: ['localhost:8000']
   ```

3. **Check firewall** isn't blocking Prometheus

## Performance Issues

### Application Running Slowly

**Common causes:**

1. **DEBUG logging in production:**
   ```bash
   LOG_LEVEL=INFO  # or WARNING, not DEBUG
   ```

2. **Database not indexed** - Check slow query logs

3. **No connection pooling** - Consider adding pgbouncer for production

### High Memory Usage

**Solutions:**

1. **Check log retention:**
   ```bash
   LOG_RETENTION=7 days  # Don't keep logs forever
   LOG_COMPRESSION=zip   # Compress rotated logs
   ```

2. **Review metrics collection** - May need sampling for high-traffic apps

## Development Issues

### Tests Failing

**Error:** Database connection errors in tests

**Solutions:**

1. **Ensure test database exists:**
   ```bash
   psql -U postgres
   CREATE DATABASE fastapi_template_tests;
   ```

2. **Check `TEST_DB_NAME` in `.env`** matches test database

3. **Run tests with pytest:**
   ```bash
   pytest
   # or
   poe test
   ```

### Pre-commit Hooks Failing

**Solutions:**

1. **Install prek hooks:**
   ```bash
   prek install
   ```

2. **Update hooks:**
   ```bash
   prek update
   ```

3. **Skip hooks temporarily** (not recommended):
   ```bash
   git commit --no-verify
   ```

## Still Having Issues?

If your problem isn't listed here:

1. **Check application logs** at `LOG_PATH` (default: `./logs/api.log`)
2. **Enable DEBUG logging** temporarily:
   ```bash
   LOG_LEVEL=DEBUG
   LOG_CATEGORIES=ALL
   ```
3. **Review the [configuration guide](usage/configuration/environment.md)** for all settings
4. **Open an issue** on [GitHub](https://github.com/seapagan/fastapi-template/issues) with:
   - Error message (full traceback)
   - Relevant log entries
   - Your environment (OS, Python version)
   - Steps to reproduce
