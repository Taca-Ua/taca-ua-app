# Developer Setup Guide - TACA Messaging Package

## Quick Start

### 1. Install the Messaging Package (Required)

From the project root, install the `taca-messaging` package in editable mode:

```bash
pip install src/shared
```

This allows all microservices to import from `taca_messaging` directly.

### 2. Verify Installation

```bash
python -c "from taca_messaging import rabbitmq_service; print('Package installed successfully')"
```

## Package Structure

```
src/shared/
├── setup.py              # Package setup configuration
├── pyproject.toml        # Modern Python packaging config
├── README.md            # Package documentation
└── taca_messaging/      # Main package directory
    ├── __init__.py
    └── rabbitmq_service.py
```

## How It Works

```python
from taca_messaging.rabbitmq_service import RabbitMQService  # Clean, proper import
```

## Docker Build Context

All Dockerfiles now copy and install the shared package:

```dockerfile
# Install messaging package
COPY ../../../shared /tmp/taca-messaging
RUN pip install --no-cache-dir /tmp/taca-messaging && rm -rf /tmp/taca-messaging

# Then install service requirements
COPY src/microservices/matches-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

This ensures the `taca_messaging` package is available when the service starts.

## Development Workflow

### Adding New Modules

1. Create new Python file in `src/shared/taca_messaging/`
2. Export from `src/shared/taca_messaging/__init__.py`
3. Use in services: `from taca_messaging import your_new_module`

## Usage in Services

### Import the Service

```python
from taca_messaging.rabbitmq_service import RabbitMQService
```

## Troubleshooting

### Import Error: "No module named 'taca_messaging'"

**Solution**: Install the package in editable mode:
```bash
pip install src/shared
```

### Changes Not Reflected

Need to reinstall the package after changes:

```bash
pip uninstall taca-messaging
pip install src/shared
```

### Docker Build Fails

**Solution**: Ensure the build context includes the shared directory. Check your `docker-compose.yml`:
```yaml
services:
  my-service:
    build:
      context: .  # Should be ., not src/microservices/my-service/
      dockerfile: src/microservices/my-service/Dockerfile
```

## Benefits

✅ **IDE support** - Full autocomplete and type checking
✅ **Editable installs** - Changes immediately reflected
✅ **Docker compatible** - Easy to include in containers
✅ **Version management** - Can version and publish if needed
✅ **Professional** - Follows Python best practices

## Next Steps

1. **Install the package**: `pip install -e src/shared`
2. **Read the docs**: Check `src/shared/taca_messaging/README.md` for API details
3. **See examples**: Look at `src/shared/taca_messaging/example_usage.py`
4. **Start coding**: Import `from taca_messaging import ...` in your services
