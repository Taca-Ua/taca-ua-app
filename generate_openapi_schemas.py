"""
Script to generate and save OpenAPI schemas for both APIs
"""

import json
import os
import sys
from pathlib import Path


def generate_competition_api_schema():
    """Generate schema for Competition API (Django)"""
    print("Generating Competition API schema...")

    # Add the competition-api to Python path
    competition_api_path = Path(__file__).parent / "src" / "apis" / "competiotion-api"
    sys.path.insert(0, str(competition_api_path))

    # Set Django settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "competition_api.settings")

    # Setup Django
    import django

    django.setup()

    # Generate schema
    from drf_spectacular.generators import SchemaGenerator

    generator = SchemaGenerator()
    schema = generator.get_schema()

    # Save to file
    output_file = Path(__file__).parent / "docs" / "openapi_competition_api.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    print(f"✓ Competition API schema saved to: {output_file}")
    return schema


def generate_public_api_schema():
    """Generate schema for Public API (FastAPI)"""
    print("\nGenerating Public API schema...")

    # Add the public-api to Python path
    public_api_path = Path(__file__).parent / "src" / "apis" / "public-api"
    if str(public_api_path) not in sys.path:
        sys.path.insert(0, str(public_api_path))

    # Import FastAPI app
    from app.main import app

    # Get OpenAPI schema
    schema = app.openapi()

    # Save to file
    output_file = Path(__file__).parent / "docs" / "openapi_public_api.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    print(f"✓ Public API schema saved to: {output_file}")
    return schema


if __name__ == "__main__":
    try:
        competition_schema = generate_competition_api_schema()
        print(f"  - Endpoints: {len(competition_schema.get('paths', {}))}")

        public_schema = generate_public_api_schema()
        print(f"  - Endpoints: {len(public_schema.get('paths', {}))}")

        print("\n✓ All OpenAPI schemas generated successfully!")
        print("\nYou can view the schemas at:")
        print("  - docs/openapi_competition_api.json")
        print("  - docs/openapi_public_api.json")

    except Exception as e:
        print(f"\n✗ Error generating schemas: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
