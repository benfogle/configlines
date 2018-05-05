from setuptools import setup, find_packages

setup(
    name='configlines',
    version='0.1',
    packages=find_packages(),
    install_requires = [
        'six',
    ],
    test_suite='configlines.tests',
    package_data={
        'configlines.tests': ['*.cfg'],
    },
)
