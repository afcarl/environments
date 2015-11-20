from __future__ import division

import numbers

import numpy as np
from bokeh import plotting, objects

import dotdot
from environments import Environment, tools
from environments.envs import KinematicArm2D

cfg = KinematicArm2D.defcfg._deepcopy()
cfg.dim = 20
cfg.limits = (-150.0, 150.0)
cfg.lengths = 1/cfg.dim
cfg.collision_fail = True

kin_env = Environment.create(cfg)

c = 0
n = 100
for _ in range(100):
    m_signal = tools.random_signal(kin_env.m_channels)
    try:
        kin_env.execute(m_signal)
    except kin_env.OrderNotExecutableError:
        c += 1

print('{}/{} collisions'.format(c, n))
