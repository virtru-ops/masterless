from setuptools import setup, find_packages

VERSION = '0.1.0'

LONG_DESCRIPTION = open('README.rst').read()

setup(
    name='masterless',
    version=VERSION,
    description="Masterless - masterless preparer for salt",
    long_description=LONG_DESCRIPTION,
    keywords='',
    author='Reuven V. Gonzales',
    author_email='reuven@virtru.com',
    url="https://github.com/virtru/salt-masterless-preparer",
    license='MIT',
    platforms='*nix',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyyaml==3.11',
        'sarge>=0.1',
        'python-json-logger'
    ],
    entry_points={
        'console_scripts': [
            'masterless=masterless.cli:run',
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Build Tools',
    ],
)
