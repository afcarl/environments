import abc

from .environment import Environment

class MotorPrimitive(object):
    """Should expose motor channels through `m_channels` attribute"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process_motor_signal(self, m_signal):
        """Process motor signal into raw motor commands"""
        pass


class SensoryPrimitive(object):
    """Should expose sensory channels through `s_channels` attribute"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process_raw_sensors(self, raw_sensors):
        """Process raw sensors into sensory signal"""
        pass


class ConcatSPrimitive(SensoryPrimitive):
    """Return the concatened signal of multiple sensory primitives"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        self.s_prims = []
        self.s_channels = []
        self.s_names = set()

    def add_s_prim(self, s_prim):
        self.s_prims.append(s_prim)
        for c in s_prim.s_channels:
            if c.name in self.s_names:
                raise ValueError('channel name {} already present in {}'.format(c.name, self.s_names))
        self.s_channels += s_prim.s_channels

    def process_raw_sensors(self, raw_sensors):
        """Process raw sensors into sensory signal"""
        s_signal = {}
        for sp in self.s_prims:
            sp_signal = sp.process_raw_sensors(raw_sensors)
            s_signal.update(sp_signal)
        return s_signal


class PrimitiveEnvironment(Environment):

    def __init__(self, cfg):
        super(PrimitiveEnvironment, self).__init__(cfg)

        self._create_primitives(cfg)

    @property
    def m_channels(self):
        return self.m_prim.m_channels

    @property
    def s_channels(self):
        return self.s_prim.s_channels

    @abc.abstractmethod
    def _create_primitives(self, cfg):
        """Create a motor and sensory primitive."""
        pass

    def _execute(self, m_signal, meta=None):
        meta = {} if meta is None else meta
        meta['m_signal'] = m_signal
        m_command = self.m_prim.process_motor_signal(m_signal)
        raw_sensors = self._execute_raw(m_command, meta=meta)
        return self.s_prim.process_raw_sensors(raw_sensors)

    @abc.abstractmethod
    def _execute_raw(self, motor_signal, meta=None):
        """Receive a raw command and returns raw sensory data"""
        pass
