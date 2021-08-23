from setuptools import setup, find_packages

with open("README.md", "r") as rf:
    long_description = rf.read()

setup(
    name="hue",
    version="0.2.0",
    author="John Stanco",
    description="REST API for communicating with Philips Hue bulbs",
    entry_points={"console_scripts": ["hue=hue.cli:main"]},
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
)
