from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='litechain',
    version='0.1',
    packages=find_packages(),
    install_requires=requirements,
    author='Rogerio Chaves',
    author_email='rogeriocfj@gmail.com',
    description='Build robust LLM applications with true composability 🔗',
    license='MIT',
    keywords='chain llm ai stream functional programming',
    url='https://github.com/rogeriochaves/litechain',
)