from setuptools import setup, find_packages

def readme():
    with open('README.rst') as fp:
        return fp.read()

setup(
    name='configlines',
    version='0.2',
    description="Add line number information to ConfigParser options",
    long_description=readme(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    url='https://github.com/benfogle/configlines',
    author='Benjamin Fogle',
    author_email='benfogle@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires = [
        'six',
    ],
    test_suite='configlines.tests',
    package_data={
        'configlines.tests': ['*.cfg'],
    },
    include_package_data=True,
)
