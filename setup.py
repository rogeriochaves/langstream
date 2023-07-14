from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="litechain",
    version="0.1.2",
    packages=find_packages(),
    install_requires=requirements,
    author="Rogerio Chaves",
    author_email="rogeriocfj@gmail.com",
    description="Build robust LLM applications with true composability 🔗",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="chain llm ai stream functional programming",
    url="https://github.com/rogeriochaves/litechain",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    project_urls={
        "Documentation": "https://rogeriochaves.github.io/litechain/",
        "Source Code": "https://github.com/rogeriochaves/litechain",
        "Issue Tracker": "https://github.com/rogeriochaves/litechain/issues",
    },
    include_package_data=True,
)
