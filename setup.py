# setup.py

from setuptools import setup, find_packages

setup(
    name="PyAkka",
    version="0.1.0",
    description="A Python library for actor-based concurrency inspired by Akka.NET and Akka.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Matin Karbasioun",
    author_email="mkarbasioun@gmail.com",
    url="https://github.com/matinkarbasioun/pyakka",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=[
        "asyncio",
        "pykka"
    ],
)
