from __future__ import print_function, division, absolute_import
import unittest
import collections
import random
import math

import numpy as np

import dotdot
from environments.envs import physicx

random.seed(0)

def near(a, b, rtol=1e-5, atol=1e-8):
    return abs(a - b) < (atol + rtol * abs(b))

class TestKin(unittest.TestCase):

    def test_newton_1d(self):
        dt = 0.05
        w = physicx.World(dt=dt)
        b1 = physicx.Ball(dt, 1.0, 1.0, (0.0, 0.0),  (0.1, 0.0))
        b2 = physicx.Ball(dt, 0.0, 1.0, (10.0, 0.0), (0.0, 0.0))
        w.add(b1, b2)

        print(b1.pos)
        print(b2.pos)

        for i in range(5000):
            w.step()
            print(b1.pos)
            print(b2.pos)
#            self.assertTrue(i <= 10, len(w.collisions) == 0)

#        self.assertTrue(

if __name__ == '__main__':
    unittest.main()
