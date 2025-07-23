# pgAdmin Connection Settings for StreamWorks-KI

## pgAdmin Access
- **URL**: http://localhost:8080
- **Email**: `admin@example.com`
- **Password**: `admin123`

## PostgreSQL Server Configuration

### Add New Server
1. Right-click on "Servers" → "Register" → "Server..."

2. **General Tab:**
   - Name: `StreamWorks Dev`

3. **Connection Tab:**
   - Host: `streamworks-ki-postgres-simple`
   - Port: `5432`
   - Maintenance database: `streamworks_ki_dev`
   - Username: `streamworks`
   - Password: `streamworks_dev_2025`
   - Save password: ✓

4. Click "Save"

## Alternative Connection Methods

If the above doesn't work, try these hosts:
- `postgres`
- `172.19.0.2` (may change after container restart)
- `localhost` (if pgAdmin is running outside Docker)

## Direct Database Access

For command-line access:
```bash
docker exec -it streamworks-ki-postgres-simple psql -U streamworks -d streamworks_ki_dev
```

## Connection Details Summary
- **Database**: `streamworks_ki_dev`
- **Username**: `streamworks`
- **Password**: `streamworks_dev_2025`
- **Port**: `5432`