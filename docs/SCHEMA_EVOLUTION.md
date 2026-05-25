# Schema Evolution Guide

Your event system already has versioning built in (e.g., `nucleo.created.v1`).
Here's how to evolve schemas:

### **1. Adding a New Field (Backward Compatible)**

**Step 1:** Update the schema in modalities.py:

```python
# Old schema v1
NUCLEO_CREATED_V1 = {
    "required": ["nucleo_id", "name", "abbreviation", "created_at"],
    "properties": {
        "nucleo_id": {"type": "string", "format": "uuid"},
        "name": {"type": "string"},
        "abbreviation": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"}
    }
}

# Updated schema v1 - NEW FIELD IS OPTIONAL
NUCLEO_CREATED_V1 = {
    "required": ["nucleo_id", "name", "abbreviation", "created_at"],
    "properties": {
        "nucleo_id": {"type": "string", "format": "uuid"},
        "name": {"type": "string"},
        "abbreviation": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "description": {"type": "string"}  # ✅ NEW optional field
    }
}
```

**Step 2:** Update the producer (e.g., `nucleo_routes.py`):
```python
emit_event(
    db=db,
    event_type=EventType.NUCLEO_CREATED,
    aggregate_type="nucleo",
    aggregate_id=nucleo.id,
    data={
        "nucleo_id": str(nucleo.id),
        "name": nucleo.name,
        "abbreviation": nucleo.abbreviation,
        "created_at": nucleo.created_at.isoformat(),
        "description": nucleo.description,  # ✅ NEW field
    },
)
```

**Step 3:** Update consumers to handle optional field:
```python
@rabbitmq_service.event_handler(RoutingKeys.NUCLEO_CREATED)
def handle_nucleo_created(event_data: Dict[str, Any]):
    nucleo_id = event_data.get("nucleo_id")
    name = event_data.get("name")
    abbreviation = event_data.get("abbreviation")
    description = event_data.get("description", "")  # ✅ Default if missing
```

---

### **2. Removing a Field (Requires New Version)**

**Step 1:** Create v2 schema in modalities.py:

```python
# Keep v1 for backward compatibility
NUCLEO_CREATED_V1 = { ... }

# Create v2 without the field
NUCLEO_CREATED_V2 = {
    "required": ["nucleo_id", "name", "created_at"],  # removed abbreviation
    "properties": {
        "nucleo_id": {"type": "string", "format": "uuid"},
        "name": {"type": "string"},
        # ❌ abbreviation removed
        "created_at": {"type": "string", "format": "date-time"}
    }
}
```

**Step 2:** Add v2 to EventType in types.py:
```python
class EventType:
    NUCLEO_CREATED = "nucleo.created.v1"
    NUCLEO_CREATED_V2 = "nucleo.created.v2"  # ✅ NEW version
```

**Step 3:** Register v2 in __init__.py:
```python
ALL_SCHEMAS = {
    "nucleo.created.v1": NUCLEO_CREATED_V1,
    "nucleo.created.v2": NUCLEO_CREATED_V2,  # ✅ NEW
}
```

**Step 4:** Update producers to use v2:
```python
emit_event(
    db=db,
    event_type=EventType.NUCLEO_CREATED_V2,  # ✅ Use v2
    aggregate_type="nucleo",
    aggregate_id=nucleo.id,
    data={
        "nucleo_id": str(nucleo.id),
        "name": nucleo.name,
        "created_at": nucleo.created_at.isoformat(),
    },
)
```

**Step 5:** Update consumers to handle both versions:
```python
@rabbitmq_service.event_handler(RoutingKeys.NUCLEO_CREATED)
def handle_nucleo_created_v1(event_data: Dict[str, Any]):
    """Handle v1 events (legacy)"""
    # Process with abbreviation
    pass

@rabbitmq_service.event_handler(RoutingKeys.NUCLEO_CREATED_V2)
def handle_nucleo_created_v2(event_data: Dict[str, Any]):
    """Handle v2 events"""
    # Process without abbreviation
    pass
```

**Step 6:** Migration period - run both handlers until all v1 events are processed

**Step 7:** Eventually deprecate v1 and remove the handler

---

### **3. Changing a Field Type (Requires New Version)**

```python
# v1 - score as integer
MATCH_RESULT_V1 = {
    "properties": {
        "score": {"type": "integer"}
    }
}

# v2 - score as object with more detail
MATCH_RESULT_V2 = {
    "properties": {
        "score": {
            "type": "object",
            "properties": {
                "points": {"type": "integer"},
                "sets_won": {"type": "integer"}
            }
        }
    }
}
```

Follow the same version migration steps as removing a field.

---

### **4. Best Practices**

✅ **Never break existing consumers** - Always add new optional fields or create new versions

✅ **Keep old schemas** - Don't delete v1 schemas even after migration

✅ **Semantic versioning** - v1, v2, v3 (not v1.1, v1.2)

✅ **Document changes** - Add comments explaining what changed between versions

✅ **Migration window** - Support old versions for at least 2-4 weeks during transition

✅ **Monitor adoption** - Track which consumers are still using old versions

✅ **Event replay** - If you need to replay old events, keep all schemas

---

### **5. RoutingKeys Setup**

Make sure your routing keys are set up in types.py:

```python
class RoutingKeys:
    # v1 routing
    NUCLEO_CREATED = "nucleo.created.v1"

    # v2 routing (if creating new version)
    NUCLEO_CREATED_V2 = "nucleo.created.v2"
```

This approach ensures **zero-downtime schema evolution** while maintaining backward compatibility! 🎯

Sources that inspired this guide:
- [How to Evolve your Microservice Schemas | Designing Event-Driven Microservices](https://youtu.be/XG-EVX6PEFo)
- [Schema Evolution with Zero Down Time | Designing Event-Driven Microservices
](https://youtu.be/kIC6QZbbXjc)
