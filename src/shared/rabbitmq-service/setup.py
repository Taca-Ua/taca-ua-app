from setuptools import find_packages, setup

setup(
    name="taca-messaging",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aio-pika>=9.0.0",
    ],
)
