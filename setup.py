from setuptools import setup

setup(
    name='proxcon',
    version='1',
    description='A utility for quickly switching proxychains proxies',
    author='James Conlan',
    url='https://github.com/JamesConlan96/proxcon',
    license='GPL-3.0',
    py_modules=[
        'proxcon'
    ],
    install_requires=[
        'tabulate'
    ],
    python_requires='>=3.0.0',
    entry_points={
        'console_scripts': [
            'proxcon = proxcon:main'
        ]
    }
)