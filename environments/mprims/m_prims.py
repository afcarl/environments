"""
Computing motor primitives from high-level orders.
"""
from __future__ import print_function, division, absolute_import
import math
import bisect
import numbers
import collections

import numpy as np

import scicfg

from . import dmp

from .. import MotorPrimitive
from .. import Channel
from .. import tools


mprims = {}

def create_mprim(cfg):
    motor_class = mprims[cfg.mprims.name]
    motor_prim = motor_class(cfg)
    return motor_prim

_defcfg = scicfg.SciConfig(strict=True)
_defcfg._branch('mprims')
_defcfg._describe('mprims.name', instanceof=str, default='dmp_sharedwidth')
_defcfg._describe('mprims.dt', instanceof=numbers.Real, default=0.010)
_defcfg._describe('mprims.traj_end', instanceof=numbers.Integral, default=1000)
_defcfg._describe('mprims.target_end', instanceof=numbers.Integral, default=500)
_defcfg._describe('mprims.sim_end', instanceof=numbers.Integral, default=1000)
_defcfg._describe('mprims.max_speed', instanceof=numbers.Real, default=180.0)
_defcfg._describe('mprims.n_basis', instanceof=numbers.Integral, default=2)

_defcfg._describe('mprims.context', instanceof=dict)
_defcfg._describe('mprims.init_states', instanceof=collections.Iterable)
_defcfg._describe('mprims.target_states', instanceof=collections.Iterable)
_defcfg._describe('mprims.angle_ranges', instanceof=collections.Iterable)


class DmpSharedWidth(MotorPrimitive):

    defcfg = _defcfg

    def __init__(self, cfg):
        self.cfg = self.defcfg._deepcopy()
        self.cfg.mprims._update(cfg.mprims)
        self.size     = len(self.cfg.mprims.init_states)
        self.n_basis  = self.cfg.mprims.n_basis
        self.sim_end  = self.cfg.mprims.sim_end
        self.traj_end = self.cfg.mprims.traj_end - (cfg.mprims.traj_end % 2)
        assert len(self.cfg.mprims.init_states) == len(self.cfg.mprims.target_states) == self.size

        self.dmps = []
        for i, (init_state, target_state) in enumerate(zip(self.cfg.mprims.init_states, self.cfg.mprims.target_states)):
            d = dmp.DMP(self.cfg.mprims.dt)
            total_time = self.traj_end/self.cfg.mprims.target_end
            d.dmp.set_timesteps(self.traj_end, 0.0, total_time)
            d.lwr_meta_params(self.n_basis)
            d.dmp.set_initial_state([self.deg_angle2dmp(i, init_state)])
            d.dmp.set_attractor_state([self.deg_angle2dmp(i, target_state)])

            self.dmps.append(d)

        self.m_channels = []
        for motor in range(self.size):
            for i in range(self.n_basis):
                self.m_channels += [Channel('slope{}.{}'.format(motor, i), (-400, 400)),
                                    Channel('offset{}.{}'.format(motor, i), (-400, 400))]
        for i in range(self.n_basis):
            self.m_channels += [Channel('width{}'.format(i), (0.05/self.n_basis, 1.0/self.n_basis))]


    def process_context(self, context):
        pass

    def process_motor_signal(self, m_signal):
        assert len(m_signal) == self.n_basis*(2*self.size+1)

        traj = []
        m_vector = tools.to_vector(m_signal, self.m_channels)

        widths = m_vector[-self.n_basis:]
        centers = tuple(np.linspace(0.0, 1.0, num=self.n_basis+2)[1:-1])

        for i, d in enumerate(self.dmps):
            slopes, offsets = [], []
            for j in range(self.n_basis):
                cursor = 2 * (self.n_basis * i + j)
                slope, offset = m_vector[cursor:cursor + 2]
                slopes.append(slope)
                offsets.append(offset)

            d.lwr_model_params(centers, widths, slopes, offsets)
            ts, ys, yds = d.trajectory()
            ts = self.cfg.mprims.target_end*self.cfg.mprims.dt*np.array(ts)
            ys = self.dmp2angle_deg(i, np.array(ys))

            traj.append(ys)
            # traj_i = Trajectory(ts, ys, self.cfg.mprims.max_speed)
            # traj.append(traj_i)

        traj = list(zip(*traj))
        return traj

    def dmp2angle_deg(self, i, ys):
        """In radians"""
        assert self.cfg.mprims.angle_ranges[i][0] == self.cfg.mprims.angle_ranges[i][1], "angles range of {}th motor are not symmetric: {}".format(i, self.cfg.mprims.angle_ranges[i])
        r = self.cfg.mprims.angle_ranges[i][1]
        return r/5.0 * ys

    def deg_angle2dmp(self, i, a):
        """In radians"""
        assert self.cfg.mprims.angle_ranges[i][0] == self.cfg.mprims.angle_ranges[i][1]
        r = self.cfg.mprims.angle_ranges[i][1]
        return 5.0/r * a


mprims['dmp_sharedwidth'] = DmpSharedWidth



ms_cfg = scicfg.SciConfig()
ms_cfg._branch('mprims')
ms_cfg._describe('mprims.name', instanceof=str, default='motorsteps')
ms_cfg._describe('mprims.dim', instanceof=numbers.Integral)
ms_cfg._describe('mprims.limits', instanceof=collections.Iterable)
ms_cfg._describe('mprims.init_pos', instanceof=collections.Iterable)
ms_cfg._describe('mprims.steps', instanceof=numbers.Integral)
ms_cfg._describe('mprims.angular_step', instanceof=numbers.Real)

class MotorSteps(MotorPrimitive):

    defcfg = ms_cfg

    def __init__(self, cfg):
        cfg._update(self.defcfg, overwrite=False)
        self.cfg = cfg

        assert len(self.cfg.mprims.init_pos) == self.cfg.mprims.dim

        limits = self.cfg.mprims.limits
        if not isinstance(limits[0], collections.Iterable):
            limits = tuple(limits for _ in range(self.cfg.mprims.dim))
        assert len(limits) == self.cfg.mprims.dim
        self.m_channels = [Channel('j{}'.format(i), bounds=limits[i]) for i, l_i in enumerate(limits)]

        self.step = self.cfg.mprims.angular_step

    def process_motor_signal(self, m_signal):
        m_vector = np.array(tools.to_vector(m_signal, self.m_channels))
        init_pos = np.array(self.cfg.mprims.init_pos)
        signs    = np.sign(m_vector-init_pos)
        step     = np.array([self.step]*len(init_pos))
        max_t    = int(max(np.abs(m_vector-init_pos))/self.step) + 1

        traj = tuple(tuple(init_pos + signs*np.fmin(np.abs(m_vector-init_pos), t*step)) for t in range(max_t))
        return traj


mprims['motorsteps'] = MotorSteps
