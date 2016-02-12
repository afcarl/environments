import collections
import math

import numpy as np

from .. import Environment, Channel, tools


defcfg = Environment.defcfg._deepcopy()
defcfg._describe('dim', instanceof=int, default=6)
defcfg._describe('limits', instanceof=collections.Iterable, default=(-150, 150))
defcfg._describe('lengths', instanceof=(float, collections.Iterable), default=1.0)
defcfg._describe('arm_origin', instanceof=collections.Iterable, default=(0.0, 0.0))
defcfg.classname = 'environments.envs.KinArmEuclidean'


class KinArmEuclidean(Environment):

    defcfg = defcfg

    def __init__(self, cfg, **kwargs):
        super(KinArmEuclidean, self).__init__(cfg)

        self.dim = self.cfg.dim
        self.lengths = self.cfg.lengths
        if not isinstance(self.lengths, collections.Iterable):
            self.lengths = tuple(self.lengths for _ in range(self.dim))
        self.limits = self.cfg.limits
        if not isinstance(self.limits[0], collections.Iterable):
            self.limits = tuple(self.limits for _ in range(self.dim))

        self.posture = None # last executed posture

        self.m_channels = [Channel('j{}'.format(i), bounds=b_i)
                           for i, b_i in enumerate(self.limits)]
        s_bounds = (-sum(self.lengths), sum(self.lengths))
        self.s_channels = [Channel('x', bounds=s_bounds),
                           Channel('y', bounds=s_bounds)]

    def _execute(self, m_signal, meta=None):
        angles = tools.to_vector(m_signal, self.m_channels)
        angles = list(reversed(angles))

        u, v = self._forward(angles)

        return tools.to_signal((u, v), self.s_channels)

    def _forward(self, angles):
        u, v, sum_a = 0, 0, 0
        self.posture = [(u, v)]
        for a, length in zip(angles, self.lengths):
            sum_a += np.radians(a)
            # at zero pose, the tip is at x=1,y=0.
            u, v = u + length*np.cos(sum_a), v + length*np.sin(sum_a)
            self.posture.append((u, v))
        return u, v


defcfg = KinArmEuclidean.defcfg._deepcopy()
defcfg.classname = 'environments.envs.KinArmPolar'


class KinArmPolar(KinArmEuclidean):

    defcfg = defcfg

    def __init__(self, cfg, **kwargs):
        super(KinArmPolar, self).__init__(cfg, **kwargs)
        self.span = sum(self.lengths)
        self.kin_s_channels = self.s_channels
        self.plr_s_channels = [Channel('r', bounds=(0, 1.25*self.span)),
                               Channel('theta', bounds=(-math.pi, math.pi))]
        self.s_channels = self.plr_s_channels

    def _execute(self, m_signal, meta=None):
        self.s_channels = self.kin_s_channels
        s_signal = super(KinArmPolar, self)._execute(m_signal, meta=meta)
        self.s_channels = self.plr_s_channels
        x = s_signal['x']
        y = s_signal['y']
        s_signal = {'r': (x*x + y*y)**0.5, 'theta': math.atan2(y, x)}
        return s_signal
