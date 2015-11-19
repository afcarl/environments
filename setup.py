import os
from setuptools import setup

import versioneer

VERSION = '1.0.1'

setup(
    name         = 'environments',
    version      = VERSION,
    cmdclass     = versioneer.get_cmdclass(),
    author       = 'Fabien Benureau',
    author_email = 'fabien.benureau@inria.fr',
    url          = 'github.com/humm/environments.git',
    maintainer   = 'Fabien Benureau',
    description  = 'Blackbox environment interface and implementations for autonomous exploration of sensorimotor spaces',
    license      = 'Open Science License (see fabien.benureau.com/openscience.html)',
    keywords     = 'exploration algorithm blackbox',
    download_url = 'https://github.com/humm/environments/tarball/{}'.format(VERSION),
    packages     = ['environments',
                    'environments.envs',
                    'environments.mprims',
                   ],
    requires     = ['scicfg', 'numpy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Science/Research',
    ]
)
