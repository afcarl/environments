from __future__ import print_function, division, absolute_import
import collections

from ..environment import Channel, Environment
from .. import tools


defcfg = Environment.defcfg._copy(deep=True)
defcfg._describe('x_coo',  instanceof=collections.Iterable, default=(0.5, 1.0),
                 docstring='coordinates of the cube along the x axis')
defcfg._describe('y_coo',  instanceof=collections.Iterable, default=(0.5, 1.0),
                 docstring='coordinates of the cube along the y axis')
defcfg.classname = 'environments.envs.FirstSquare2D'

class FirstSquare2D(Environment):

    defcfg = defcfg

    def __init__(self, cfg):
        super(FirstSquare2D, self).__init__(cfg)
        self.m_channels = [Channel('a', (0., 1.)), Channel('b', (0., 1.)),
                           Channel('c', (0., 1.)), Channel('d', (0., 1.))]
        self.s_channels = [Channel('x', (0., 1.)), Channel('y', (0., 1.))]

    def _inside_square(self, a, b):
        return (self.cfg.x_coo[0] <= a <= self.cfg.x_coo[1] and
                self.cfg.y_coo[0] <= b <= self.cfg.y_coo[1])

    def _transform(self, c, d):
        return (0.5 + c*0.5, 0.5 + d*0.5)

    def _execute(self, order, meta=None):
        s_vector = (0.0, 0.0)
        if self._inside_square(order['a'], order['b']):
            s_vector = self._transform(order['c'], order['d'])
        return tools.to_signal(s_vector, self.s_channels)


defcfg2 = defcfg._deepcopy()
defcfg2.classname = 'environments.envs.SecondSquare2D'

class SecondSquare2D(FirstSquare2D):

    defcfg = defcfg2

    def _transform(self, c, d):
        return (1/(10*c + d), (c**2)*d)
