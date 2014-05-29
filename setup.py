import os
from distutils.core import setup

setup(
    name = "environments",
    version = "0.1",
    author = "Fabien Benureau",
    author_email = "fabien.benureau@inria.fr",
    description = ("Environments for exploration"),
    license = "Open Science.",
    keywords = "exploration learning algorithm",
    url = "flowers.inria.fr",
    packages=['environments', 'environments.envs',
             ],
    requires=['forest'],
    classifiers=[],
)
