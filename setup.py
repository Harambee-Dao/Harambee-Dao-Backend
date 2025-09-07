from setuptools import setup, find_packages

setup(
    name="harambee-backend",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.30.0",
        "pydantic>=2.8.2",
        "pydantic-settings>=2.4.0",
        "python-dotenv>=1.0.1",
        "requests>=2.32.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=5.0.0",
            "httpx>=0.27.0",
            "ruff>=0.5.5",
            "mypy>=1.10.0",
        ]
    },
)
