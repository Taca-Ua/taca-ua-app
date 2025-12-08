#!/usr/bin/env python3
"""
Script to initialize MinIO buckets and policies
Run this after MinIO is up and running
"""

import os
import sys

from minio import Minio
from minio.error import S3Error


def init_minio():
    """Initialize MinIO with required buckets and policies"""

    # Get credentials from environment
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
    secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")

    print(f"Connecting to MinIO at {endpoint}...")

    # Initialize MinIO client
    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )

    # Define buckets to create
    buckets = [
        {
            "name": "regulations",
            "description": "Storage for regulation documents",
        },
        {
            "name": "tournament-images",
            "description": "Storage for tournament images",
        },
        {
            "name": "team-logos",
            "description": "Storage for team logos",
        },
    ]

    # Create buckets
    for bucket in buckets:
        try:
            if not client.bucket_exists(bucket["name"]):
                client.make_bucket(bucket["name"])
                print(f"✓ Created bucket: {bucket['name']} - {bucket['description']}")
            else:
                print(f"✓ Bucket already exists: {bucket['name']}")
        except S3Error as e:
            print(f"✗ Error creating bucket {bucket['name']}: {e}")
            sys.exit(1)

    # Set public read policy for specific buckets
    public_buckets = ["regulations", "team-logos", "tournament-images"]

    for bucket_name in public_buckets:
        try:
            policy = f"""{{
    "Version": "2012-10-17",
    "Statement": [
        {{
            "Effect": "Allow",
            "Principal": {{"AWS": ["*"]}},
            "Action": ["s3:GetObject"],
            "Resource": ["arn:aws:s3:::{bucket_name}/*"]
        }}
    ]
}}"""
            client.set_bucket_policy(bucket_name, policy)
            print(f"✓ Set public read policy for: {bucket_name}")
        except S3Error as e:
            print(f"⚠ Warning: Could not set policy for {bucket_name}: {e}")

    print("\n✓ MinIO initialization completed successfully!")
    print(f"\nAccess MinIO Console at: http://{endpoint.split(':')[0]}:9001")
    print(f"Username: {access_key}")
    print(f"Password: {secret_key}")


if __name__ == "__main__":
    try:
        init_minio()
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        sys.exit(1)
