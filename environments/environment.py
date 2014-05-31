from __future__ import absolute_import, division, print_function
import abc
import uuid
import forest


class Channel(object):

    def __init__(self, name, bounds=(float('-inf'), float('+inf')),
                 fixed=None, unit=''):
        self.name   = name
        self.bounds = bounds
        self.fixed  = fixed
        self.unit   = unit

    def __repr__(self):
        return 'Channel({}, {})'.format(self.name, self.bounds)

    def __eq__(self, channel):
        return (self.name == channel.name and
                self.bounds == channel.bounds and
                self.fixed == channel.fixed)


class OrderNotExecutableError(Exception):
    pass


defcfg = forest.Tree()
defcfg._describe('classname', instanceof=str,
                 docstring='The name of the environment class. Only used with the create() class method.')


class Environment(object):
    __metaclass__ = abc.ABCMeta

    defcfg = defcfg

    OrderNotExecutableError = OrderNotExecutableError

    def __init__(self, cfg, **kwargs):
        """ You should define m_channels and s_channels, motor and sensory
            channels for the environment, here, as a list of Channel instances.
        """
        if isinstance(cfg, dict):
            cfg = forest.Tree(cfg)
        self.cfg = cfg
        self.cfg._update(self.defcfg, overwrite=False)

    def execute(self, m_signal, meta=None):
        return {'m_signal': m_signal,
                's_signal': self._execute(m_signal, meta=meta),
                'uuid'    : uuid.uuid4()}

    @abc.abstractmethod
    def _execute(self, m_signal, meta=None):
        """Should return the sensory feedback"""
        pass

    @classmethod
    def __subclasshook__(cls, C):
        check = NotImplemented
        if cls is Environment:
            check = True
            required = ['execute']
            for method in required:
                if not any(method in B.__dict__ for B in C.__mro__):
                    check = NotImplemented
        return check

    def close(self):
        """Override for any clean-up"""
        pass
