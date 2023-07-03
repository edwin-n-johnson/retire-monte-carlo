from setuptools import setup

setup(
    name='retire',
    version='0.1.0',
    py_modules=['retire'],
    install_requires=[
        'Click',
        'numpy',
        'matplotlib'
    ],
    entry_points={
        'console_scripts': [
            'retire = retire:cli',
        ],
    },
)