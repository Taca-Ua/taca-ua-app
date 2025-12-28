# Alembic Database Migrations

This document provides instructions on how to manage database schema migrations using Alembic in this project.

## Prerequisites

Alembic is already included in `requirements.txt`:
```
alembic==1.11.1
```

## Configuration

The database URL is read from the `DATABASE_URL` environment variable. Default:
```
postgresql://user:password@localhost:5432/taca_ua
```

In order to create and apply migrations, ensure that an instance of the database is accessible and the connection string is correct.
```bash
docker run -d --name taca-ua-db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=taca_ua -p 5432:5432 postgres:15-alpine
```

Update the db
```bash
cd src/microservices/<service-name>
alembic upgrade head
```

## Common Commands

### Create a new migration (auto-generate from models)
```bash
alembic revision --autogenerate -m "description of changes"
```

### Create a new empty migration
```bash
alembic revision -m "description of changes"
```

### Apply all pending migrations (upgrade to latest)
```bash
alembic upgrade head
```

### Apply migrations up to a specific revision
```bash
alembic upgrade <revision_id>
```

### Rollback one migration
```bash
alembic downgrade -1
```

### Rollback all migrations
```bash
alembic downgrade base
```

### Show current revision
```bash
alembic current
```

### Show migration history
```bash
alembic history
```

### Show pending migrations
```bash
alembic history --verbose
```

## Migration Files

Migration files are stored in `alembic/versions/` and follow the naming pattern:
```
<revision_id>_<description>.py
```

Each migration file contains:
- `upgrade()`: Apply the migration
- `downgrade()`: Rollback the migration

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (required)
  - Format: `postgresql://user:password@host:port/database`  # pragma: allowlist secret

## Tips

1. Always review auto-generated migrations before applying them
2. Test migrations on a development database first
3. Keep migrations small and focused
4. Never edit a migration that has been applied to production
5. Use descriptive migration messages

## Troubleshooting

### "Target database is not up to date"
Run `alembic upgrade head` to apply pending migrations.

### "Can't locate revision identified by..."
Ensure your database's `alembic_version` table is in sync with your migration files.

### Database connection errors
Check that `DATABASE_URL` is correctly set and the database is accessible.
