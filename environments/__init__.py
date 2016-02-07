from __future__ import absolute_import


# versioneer
from ._version import get_versions
__version__ = get_versions()["version"]
__commit__ = get_versions()["full-revisionid"]
__dirty__ = get_versions()["dirty"]
del get_versions

__url__ = 'https://github.com/humm/environments'


# intra-package imports
from .environment import Channel
from .environment import Environment

from .prims import MotorPrimitive
from .prims import SensoryPrimitive
from .prims import ConcatSPrimitive
from .prims import PrimitiveEnvironment

from . import tools
