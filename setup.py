from setuptools import setup, find_packages

setup(
    name='quiffen',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        # Your library dependencies
        "python >= 3.8",
        "pydantic >= 1.10.2",
        "pandas >= 1.5.1",
        "python-dateutil >= 2.8.2",
        "babel >= 2.13.1"
    ],
)