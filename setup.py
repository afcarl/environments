import os
from setuptools import setup

setup(
    name = "environments",
    version = "1.0",
    author = "Fabien Benureau",
    author_email = "fabien.benureau@inria.fr",
    url='flowers.inria.fr',
    maintainer='Fabien Benureau',
    description = "Blackbox environment interface and implementations for autonomous exploration of sensorimotor spaces",
    license = "Open Science License (see fabien.benureau.com/openscience.html)",
    keywords = "exploration algorithm blackbox",
    download_url='https://github.com/humm/environments/tarball/1.0',
    packages=['environments', 'environments.envs',
             ],
    dependency_links=[
        "https://github.com/flowersteam/forest/tarball/master#egg=forest-1.0",
    ],
    requires=['forest', 'numpy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Science/Research',
    ]
)
