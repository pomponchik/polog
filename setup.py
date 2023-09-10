from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf8') as readme_file:
    readme = readme_file.read()

requirements = []

setup(
    name='polog',
    version='0.0.18',
    author='Evgeniy Blinov',
    author_email='zheni-b@yandex.ru',
    description='The new generation logger',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/pomponchik/polog',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
    ],
)
