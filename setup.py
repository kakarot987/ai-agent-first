"""Setuptools package definition for the AI chat CLI."""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="ai-agent",
    version="0.2.0",
    description="An extensible OpenAI chat CLI with conversation persistence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kakarot987/ai-agent-first",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    install_requires=[
        "openai>=1.12.0,<3",
        "python-dotenv>=0.19.0",
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "pre-commit>=2.20.0",
        ]
    },
    entry_points={"console_scripts": ["ai-agent=ai_agent.cli.main:cli"]},
)
