from setuptools import find_packages, setup

setup(
    name="taca-logging",
    version="0.1.0",
    description="Shared structured logging configuration for TACA services",
    author="TACA Team",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "structlog>=24.1.0",
        "python-logging-loki>=0.3.1",
    ],
    python_requires=">=3.9",
    zip_safe=False,
)
