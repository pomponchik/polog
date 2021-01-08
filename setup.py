from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["polog>=0.0.9", "pyTelegramBotAPI>=3.7.4"]

setup(
    name="telegram_polog_handler",
    version="0.1.0",
    author="hgreenfe",
    author_email="hgreenfe@student.21-school.ru",
    description="telegram handler for polog",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Bce-OK/telegram_polog_handler",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
)
