from setuptools import find_packages, setup

setup(
    name="taca-storage",
    version="0.1.0",
    description="Shared storage and MinIO configuration for TACA services",
    author="TACA Team",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "minio>=7.1.0",
        "filetype>=1.2.0",
    ],
    python_requires=">=3.9",
    zip_safe=False,
)