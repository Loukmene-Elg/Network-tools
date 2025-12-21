from setuptools import setup, find_packages

setup(
    name="netmon",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "netmon=netmon.cli:main",
        ],
    },
)