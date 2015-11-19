""" DMP class to generate trajectories

    dmp = DMP()
    dmp.lwr_meta_params(2)
    dmp.lwr_model_params(slopes = [0.0, -500.0], offsets = [-500.0, 0.0], centers = [0.0, 0.5], widths = [1.0, 1.0])
"""
from __future__ import print_function, division, absolute_import

import numpy as np

try:
    import pydmp
except ImportError:
    pass


class DMP(object):

    def __init__(self, dt):
        try:
            pydmp
        except NameError:
            raise ImportError('`pydmp` could not be imported. Verify pydmp install.')

        self.dmp = pydmp.PyDMP(1)
        duration = 2.0

        self.dmp.set_timesteps(int(1000/dt*duration), 0.0, duration)
        self.dmp.set_initial_state([0.0])
        self.dmp.set_attractor_state([1.0])

        self.centers = None
        self.widths  = None
        self.slopes  = None
        self.offsets = None

        self.lwr_meta_params(1, 0.1)

    def trajectory(self):
        traj = self.dmp.generate_trajectory()
        return traj[::3], traj[1::3], traj[2::3]

    def lwr_meta_params(self, n_bases, overlap=0.01):
        self.n_bases = n_bases
        self.dmp.set_lwr_meta_parameters(1, n_bases, overlap)

        self.centers = list(np.linspace(0.0, 1.0, num=n_bases+2))[1:-1]
        self.widths  = [0.5/n_bases + 2*overlap]*n_bases
        self.slopes  = [0.0]*n_bases
        self.offsets = [0.0]*n_bases

        self.dmp.set_lwr_model_parameters(self.centers, self.widths, self.slopes, self.offsets)

    def lwr_model_params(self, centers = None, widths = None,
                               slopes = None, offsets = None):
        assert self.centers is not None, "you must set lwr_meta_parameters before set_lwr_model_parameters."
        self.centers = centers if centers is not None else self.centers
        self.widths  = widths  if widths  is not None else self.widths
        self.slopes  = slopes  if slopes  is not None else self.slopes
        self.offsets = offsets if offsets is not None else self.offsets

        #print(self.centers, self.widths, self.slopes, self.offsets)
        assert self.n_bases == len(self.centers) == len(self.widths) == len(self.slopes) == len(self.offsets)
        self.dmp.set_lwr_model_parameters(list(self.centers), list(self.widths),
                                          list(self.slopes), list(self.offsets))



