from __future__ import print_function, division, absolute_import
import numbers
import math

from ..environment import Channel, Environment


defcfg = Environment.defcfg._copy(deep=True)
defcfg._describe('xmin',      instanceof=numbers.Real)
defcfg._describe('xmax',      instanceof=numbers.Real)
defcfg._describe('obj_x',     instanceof=numbers.Real)
defcfg._describe('obj_width', instanceof=numbers.Real)
defcfg._describe('obj_y',     instanceof=numbers.Real)
defcfg.classname = 'environments.envs.PushArrayStraightCollides'
defcfg._freeze(True)


class PushArrayStraightCollides(Environment):

    defcfg = defcfg

    def __init__(self, cfg):
        super(PushArrayStraightCollides, self).__init__(cfg)
        self.cfg.s_channels = [Channel('obj_x', (self.cfg.xmin, self.cfg.xmax)),
                               Channel('obj_y', (0, 100)),
                               Channel('obj_col', bounds=(0, 100), fixed=100)]
        self.cfg.m_channels = [Channel('x', (self.cfg.xmin, self.cfg.xmax)),
                               Channel('y', (0, 10)),
                               Channel('speed', (0, 10))]
        self.m_channels = self.cfg.m_channels
        self.s_channels = self.cfg.s_channels
        self._obj_xmin = self.cfg.obj_x - self.cfg.obj_width/2
        self._obj_xmax = self.cfg.obj_x + self.cfg.obj_width/2

    def _execute(self, m_signal, meta=None):
        if (self._obj_xmin <= m_signal['x'] <= self._obj_xmax and
            self.cfg['obj_y'] <= m_signal['y']): # collision
            obj_x = self.cfg['obj_x']
            obj_y = self.cfg['obj_y'] + m_signal['speed']
            s_signal = {'obj_x': obj_x, 'obj_y': obj_y, 'obj_col': 100}
        else:
            s_signal = {'obj_x': self.cfg.obj_x, 'obj_y': self.cfg.obj_y, 'obj_col': 0}

        return s_signal


defcfg2 = defcfg._deepcopy()
defcfg2._freeze(False)
defcfg2.classname = 'environments.envs.PushArrayStraight'
defcfg2._freeze(True)


class PushArrayStraight(PushArrayStraightCollides):

    defcfg = defcfg2

    def __init__(self, cfg):
        super(PushArrayStraight, self).__init__(cfg)
        self.cfg.s_channels = self.cfg.s_channels[:2]
        self.s_channels = self.s_channels[:2]

    def _execute(self, m_signal, meta=None):
        s_signal = super(PushArrayStraight, self)._execute(m_signal)
        s_signal.pop('obj_col')
        return s_signal


defcfg3 = defcfg._deepcopy()
defcfg3._freeze(False)
defcfg3.classname = 'environments.envs.PushArrayAngle'
defcfg3._freeze(True)


class PushArrayAngle(PushArrayStraight):

    def _execute(self, m_signal, meta=None):
        if (self._obj_xmin <= m_signal['x'] <= self._obj_xmax and
            self.cfg['obj_y'] <= m_signal['y']): # collision
            theta = math.atan2(self.cfg['obj_x'] - m_signal['x'], self.cfg['obj_y'])
            obj_x = self.cfg['obj_x'] + math.sin(theta)*m_signal['speed']
            obj_y = self.cfg['obj_y'] + math.cos(theta)*m_signal['speed']
            s_signal = {'obj_x': obj_x, 'obj_y': obj_y}
        else:
            s_signal = {'obj_x': self.cfg.obj_x, 'obj_y': self.cfg.obj_y}
        return s_signal
