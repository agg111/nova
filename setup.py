"""
Setup script for Nova package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nova",
    version="1.0.0",
    author="Nova Team",
    author_email="team@nova.dev",
    description="A modern CAD file locking system for team collaboration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/nova",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "flask-socketio>=5.0.0",
        "psutil>=5.8.0",
        "python-socketio>=5.0.0",
        "eventlet>=0.30.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "nova=backend.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "backend": ["web/templates/*.html"],
    },
    keywords="nova, cad, file-locking, solidworks, inventor, autocad, collaboration, engineering",
    project_urls={
        "Bug Reports": "https://github.com/your-org/nova/issues",
        "Source": "https://github.com/your-org/nova",
        "Documentation": "https://nova.readthedocs.io/",
    },
)
