"""Setup script for mazegen package."""

from setuptools import find_packages, setup

setup(
    name="mazegen",
    version="1.0.0",
    description="A standalone, reusable maze generator and solver with 42 pattern support",
    author="Hanna Schulze, Miroslau Ilnicki",
    packages=find_packages(include=["mazegen", "mazegen.*"]),
    package_data={"mazegen": ["py.typed"]},
    python_requires=">=3.10",
)
