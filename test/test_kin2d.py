from __future__ import print_function, division, absolute_import
import unittest
import collections
import random
import math

import numpy as np

import dotdot
from environments import Environment
from environments import tools
from environments.envs import KinematicArm2D, KinArmSynergies2D

random.seed(0)

def near(a, b, rtol=1e-5, atol=1e-8):
    return abs(a - b) < (atol + rtol * abs(b))

class TestKin(unittest.TestCase):

    # def test_zero(self):

    #     cfg = KinematicArm2D.defcfg._deepcopy()
    #     cfg.dim = 500
    #     cfg.limits = (-150.0, 150.0)
    #     cfg.lengths = 1/cfg.dim
    #     cfg.collision_fail = True

    #     kin_env = Environment.create(cfg)

    #     m_signal = {'j{}'.format(i): 0.0 for i in range(kin_env.cfg.dim)}
    #     s_signal = kin_env.execute(m_signal)['s_signal']

    #     self.assertTrue(near(s_signal['x'], 1.0))
    #     self.assertTrue(near(s_signal['y'], 0.0))


    # def test_collision(self):

    #     cfg = KinematicArm2D.defcfg._deepcopy()
    #     cfg.dim = 20
    #     cfg.limits = (-150.0, 150.0)
    #     cfg.lengths = 1/cfg.dim
    #     cfg.collision_fail = True

    #     kin_env = Environment.create(cfg)

    #     colliding = [{'j8': 103.15734402188917, 'j9': 42.04002359559448, 'j4': 109.20298892551108, 'j5': -110.08586002756141, 'j6': 95.89003186600124, 'j7': -139.616757246914, 'j0': 126.20595484547243, 'j1': -113.9813710046603, 'j2': -134.25673529475216, 'j3': -9.273788683880525, 'j18': 12.2261198602408, 'j19': 21.89250121653575, 'j16': 148.79594739864172, 'j17': 37.382456193064456, 'j14': -91.99918868420295, 'j15': -108.78716088993792, 'j12': 116.42805255322025, 'j13': -109.42049137843304, 'j10': 6.743587550815903, 'j11': 144.66905010569923},
    #                  {'j8': 18.265131982105757, 'j9': -44.333706688559715, 'j4': -76.1766529080314, 'j5': 62.61825883174785, 'j6': 2.3131529001568794, 'j7': 55.615036706342266, 'j0': 53.54114189833348, 'j1': -19.136639274598267, 'j2': -73.49414347534932, 'j3': -64.91177940110978, 'j18': 48.42349565367962, 'j19': -1.099387101983055, 'j16': -7.609047991267403, 'j17': -79.90409344781865, 'j14': -6.895302694132184, 'j15': 75.11874720355348, 'j12': 77.2716807837171, 'j13': -55.40652691596209, 'j10': 62.50306792078149, 'j11': 87.22413528722353},
    #                  {'j8': 43.44305776901811, 'j9': 79.06452684080591, 'j4': -49.512389850739915, 'j5': -76.65165588931086, 'j6': -43.50232991325673, 'j7': 43.55862843017883, 'j0': 88.28374460807507, 'j1': -66.72601438954622, 'j2': -25.795590807992028, 'j3': -65.68255246230548, 'j18': 40.639316776007036, 'j19': 24.622057910581603, 'j16': 12.276471385854578, 'j17': -79.33521986667932, 'j14': 89.93164442174839, 'j15': 68.55484507111507, 'j12': 60.97684456297492, 'j13': 48.743386493679424, 'j10': 30.128952123557326, 'j11': 7.006479491817004},
    #                 ]

    #     non_colliding = [{'j8': 69.84548245533759, 'j9': 60.69508506596159, 'j4': -22.79835533741101, 'j5': -81.81339420388498, 'j6': 64.59275235157097, 'j7': 12.493335821046898, 'j0': -79.30756124905898, 'j1': 35.03650359702138, 'j2': 85.04428290319646, 'j3': -38.655911683957086, 'j18': -87.88886946746618, 'j19': 84.71817606853912, 'j16': 70.2466964672285, 'j17': 6.694368751244113, 'j14': -22.8064436228223, 'j15': -27.728200782361036, 'j12': 47.709409182744594, 'j13': -3.0531128340647626, 'j10': 21.978487930203613, 'j11': -78.82140503060407},
    #                      {'j8': -2.5016665816534953, 'j9': -53.92719428445995, 'j4': 58.39202918458838, 'j5': 40.84594712807825, 'j6': 73.69545254186653, 'j7': -56.28688169763158, 'j0': 55.338087451699636, 'j1': -70.58040178585713, 'j2': -71.51224462621354, 'j3': -17.60432468048326, 'j18': 41.76442186489183, 'j19': 53.721664414023365, 'j16': 50.025898781710794, 'j17': 44.82337835790821, 'j14': -76.05642742261251, 'j15': 18.014173661135843, 'j12': -13.208991544232376, 'j13': 4.41036252652539, 'j10': -52.0485479657503, 'j11': -28.89885995571337},
    #                     ]

    #     for m_signal in colliding:
    #         with self.assertRaises(kin_env.OrderNotExecutableError):
    #             kin_env.execute(m_signal)

    #     for m_signal in non_colliding:
    #         kin_env.execute(m_signal)

    def test_synergies(self):

        cfg = KinArmSynergies2D.defcfg._deepcopy()
        cfg.dim = 3
        cfg.limits = (-180.0, 180.0)
        cfg.lengths = 1.0
        cfg.syn_span = 3
        cfg.syn_res  = 3

        kin_env = Environment.create(cfg)
        m_signal = {'j0': 0.0, 'j1': 0.0, 'j2': 0.0, 's0': 1.0}

        feedback = kin_env.execute(m_signal)
        s_signal = feedback['s_signal']
        self.assertTrue(near(s_signal['y'],  0.0))
        self.assertTrue(near(s_signal['x'], -1.0))

if __name__ == '__main__':
    unittest.main()
