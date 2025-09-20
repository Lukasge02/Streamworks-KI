# Streamworks Backend SQL Migrations

All raw SQL migrations now live in this directory. Files are ordered by their
numeric prefix so they can be applied deterministically (e.g. via `psql` or the
helper scripts under `backend/`). Former files from `backend/database/migrations`
have been merged here to keep a single source of truth.

## Applying migrations

1. Ensure the `SUPABASE_DB_URL` environment variable is set.
2. Apply each script in ascending order, for example:

```bash
for file in backend/migrations/*.sql; do
  psql "$SUPABASE_DB_URL" -f "$file"
done
```

The manual `create_*` helper scripts continue to work and will reference the
same SQL files stored in this directory.
