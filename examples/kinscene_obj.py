import pygame
import sys

from environments import tools
from environments.envs import KinScene2D

cfg = KinScene2D.defcfg._deepcopy()

cfg.dim = 7
cfg.arm_origin = (300.0, 300.0, 0.0)
cfg.limits = (-150.0, 150.0)
cfg.lengths = 200.0/cfg.dim
cfg.headless = False

cfg.m_prims.init_pos = [0.0]*7
cfg.m_prims.angular_step = 0.01

cfg.tip.mass   = 1.0
cfg.tip.radius = 3.0

cfg.objects.ball = KinScene2D.objcfg._deepcopy()
cfg.objects.ball.radius = 5.0
cfg.objects.ball.mass   = 1.0
cfg.objects.ball.pos    = (495.0, 315.0)
cfg.objects.ball.track  = True



ks = KinScene2D(cfg)

for t in range(1):
    m_signal = tools.random_signal(ks.m_channels)
    print(m_signal)
    m_signal = {'j{}'.format(i): 20 for i in range(cfg.dim)}
    s_signal = ks.execute(m_signal)

