from setuptools import find_packages, setup

setup(
    name="taca-events",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.9",
)
