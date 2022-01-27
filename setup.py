from setuptools import setup, find_packages

VERSION = '1.2.1'
DESCRIPTION = 'Quiffen'
with open('README.rst', 'r') as f:
    LONG_DESCRIPTION = f.read()

# Setting up
setup(
    name="quiffen",
    version=VERSION,
    author="Isaac Harris-Holt",
    author_email="isaac@harris-holt.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    install_requires=[],
    keywords=['qif', 'finance', 'data processing'],
    license='GNU GPLv3',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ],
    python_requires='>=3'
)
