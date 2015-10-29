import os
from setuptools import setup

import versioneer

setup(
    name         = 'environments',
    version      = '1.0',
    cmdclass     = versioneer.get_cmdclass(),
    author       = 'Fabien Benureau',
    author_email = 'fabien.benureau@inria.fr',
    url          = 'github.com/humm/environments.git',
    maintainer   = 'Fabien Benureau',
    description  = 'Blackbox environment interface and implementations for autonomous exploration of sensorimotor spaces',
    license      = 'Open Science License (see fabien.benureau.com/openscience.html)',
    keywords     = 'exploration algorithm blackbox',
    download_url = 'https://github.com/humm/environments/tarball/1.0',
    packages     = ['environments',
                    'environments.envs',
                    'environments.mprims',
                   ],
    requires     = ['forest', 'numpy'],
    dependency_links=[
        "https://github.com/flowersteam/forest/tarball/master#egg=forest-1.0",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Science/Research',
    ]
)
