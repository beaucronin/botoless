from setuptools import setup, find_packages

version = open('VERSION').read().strip()
license = open('LICENSE').read().strip()

setup(
    name = 'botoless',
    version = version,
    license = license,
    author = 'Beau Cronin',
    author_email = 'beau.cronin@gmail.com',
    description = 'A smaller view of boto3, intended for serverless application development',
    long_description = open('README.md').read().strip(),
    packages = find_packages(),
    install_requires=[
        # put packages here
        'six',
    ],
    # test_suite = 'tests',
    entry_points = {
	    'console_scripts': [
	        'botoless = botoless.__main__:main',
	    ]
	}
)