from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ['pony==0.7.13', 'ujson==3.0.0']

setup(
    name="polog",
    version="0.0.7",
    author="Evgeniy Blinov",
    author_email="zheni-b@yandex.ru",
    description="Polog - ультимативный логгер для баз данных.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/pomponchik/polog",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
)
