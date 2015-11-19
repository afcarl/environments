from __future__ import print_function, division, absolute_import
import unittest
import collections
import random
import math

import numpy as np

import dotdot
from environments import Environment
from environments.mprims import MotorSteps

random.seed(0)

def near(a, b, rtol=1e-5, atol=1e-8):
    return abs(a - b) < (atol + rtol * abs(b))

class TestKinObj(unittest.TestCase):

    def test_motorsteps(self):

        cfg = MotorSteps.defcfg._deepcopy()
        cfg.mprims.dim          = 4
        cfg.mprims.limits       = (-20.0, 20.0)
        cfg.mprims.init_pos     = (3.0, 0.0, 0.0, -3.0)
        cfg.mprims.angular_step = 1.0

        ms = MotorSteps(cfg)

        traj = ms.process_motor_signal({'j0': 6.0, 'j1': 6.0, 'j2':-3.0, 'j3':-1.0})
        self.assertEqual(traj, ((3.0, 0.0, 0.0, -3.0), (4.0, 1.0, -1.0, -2.0), (5.0, 2.0, -2.0, -1.0), (6.0, 3.0, -3.0, -1.0), (6.0, 4.0, -3.0, -1.0), (6.0, 5.0, -3.0, -1.0), (6.0, 6.0, -3.0, -1.0)))

if __name__ == '__main__':
    unittest.main()
