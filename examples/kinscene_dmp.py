import sys
import random

import dotdot
import environments
from environments import tools
from environments.envs import KinScene2D
from environments import mprims

cfg = KinScene2D.defcfg._deepcopy()

cfg.dim = 7
cfg.arm_origin = (300.0, 300.0, 0.0)
cfg.limits = (-150.0, 150.0)
cfg.lengths = 200.0/cfg.dim
cfg.headless = False

fps = 50

cfg._update(mprims.DmpSharedWidth.defcfg)
cfg.mprims.dt            = 1.0/fps
cfg.mprims.traj_end      = 10*fps
cfg.mprims.target_end    =  5*fps
cfg.mprims.sim_end       = 10*fps
cfg.mprims.context       = {}
cfg.mprims.max_speed     = 180.0
cfg.mprims.n_basis       = 2

cfg.mprims.init_states   = (0.0,)*cfg.dim
cfg.mprims.target_states = (0.0,)*cfg.dim


# cfg.mprims.init_states   = (-135.0, 135.0, -135.0, 135.0, -135.0, 100.0, -30.0)
# cfg.mprims.target_states = (-135.0, 135.0, -135.0, 135.0, -135.0, 100.0, -30.0)
cfg.mprims.angle_ranges  = ((150, 150),)*cfg.dim


cfg.tip.mass   = 1.0
cfg.tip.radius = 3.0

cfg.objects.ball = KinScene2D.objcfg._deepcopy()
cfg.objects.ball.radius = 5.0
cfg.objects.ball.mass   = 20.0
cfg.objects.ball.pos    = (480.0, 300.0)
cfg.objects.ball.track  = True

bpos = cfg.objects.ball.pos
size = 200
cfg.s_prims.x_limits = (int(bpos[0]-size), int(bpos[0]+size))
cfg.s_prims.y_limits = (int(bpos[1]-size), int(bpos[1]+size))


ks = environments.Environment.create(cfg)
print(ks.s_channels)

random.seed(0)
collisions = 0
n = 25
for t in range(n):
    m_signal = tools.random_signal(ks.m_channels)
    feedback = ks.execute(m_signal)
    if feedback['s_signal'] != {'y': cfg.objects.ball.pos[1], 'x': cfg.objects.ball.pos[0]}:
        collisions += 1
    print(feedback['s_signal'])

print('{}/{} ({:.2f}%)'.format(collisions, n, 100.0*collisions/n))
