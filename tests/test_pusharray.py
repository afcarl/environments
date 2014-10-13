from __future__ import print_function, division, absolute_import
import unittest
import collections
import random
import math

import numpy as np

import dotdot
from environments.envs.pusharray import PushArrayStraight
from environments.envs.pusharray import PushArrayAngle


random.seed(0)

class TestPush(unittest.TestCase):

    def test_pushstraight(self):
        cfg = PushArrayStraight.defcfg._copy()
        cfg._freeze(False)
        cfg.xmin      = 0
        cfg.xmax      = 1000
        cfg.obj_x     = 350
        cfg.obj_y     = 5
        cfg.obj_width = 100

        pas = PushArrayStraight(cfg)

        for _ in range(1000):
            order = collections.OrderedDict((c.name, random.uniform(*c.bounds)) for c in pas.m_channels)
            effect = pas.execute(order)['s_signal']
            self.assertEqual(effect['obj_x'], 350)
            self.assertTrue(effect['obj_y'] >= 5)

        order = collections.OrderedDict((('x', 310), ('y', 10), ('speed', 10)))
        effect = pas.execute(order)['s_signal']
        self.assertEqual(effect['obj_y'], 15)

    def test_pushangle(self):
        cfg = PushArrayStraight.defcfg._copy()
        cfg._freeze(False)
        cfg.xmin      = 0
        cfg.xmax      = 1000
        cfg.obj_x     = 350
        cfg.obj_y     = 5
        cfg.obj_width = 100

        pas = PushArrayAngle(cfg)

        for _ in range(1000):
            order = collections.OrderedDict((c.name, random.uniform(*c.bounds)) for c in pas.m_channels)
            effect = pas.execute(order)

        order = collections.OrderedDict((('x', 350), ('y', 10), ('speed', 10)))
        effect = pas.execute(order)['s_signal']
        self.assertEqual(effect['obj_x'], 350)
        self.assertEqual(effect['obj_y'], 15)

        order = collections.OrderedDict((('x', 345), ('y', 10), ('speed', 10)))
        effect = pas.execute(order)['s_signal']
        self.assertEqual(effect['obj_x'], 350 + 10*math.cos(math.atan2(5, 5)))
        self.assertEqual(effect['obj_y'], 5   + 10*math.cos(math.atan2(5, 5)))

        for _ in range(1000):
            order = collections.OrderedDict((('x', 350 + random.uniform(0, 50)), ('y', 10), ('speed', 10)))
            effect = pas.execute(order)['s_signal']
            self.assertTrue(effect['obj_x'] < 350)
            self.assertTrue(effect['obj_y'] > 5)

            order = collections.OrderedDict((('x', 350 - random.uniform(0, 50)), ('y', 10), ('speed', 10)))
            effect = pas.execute(order)['s_signal']
            self.assertTrue(effect['obj_x'] > 350)
            self.assertTrue(effect['obj_y'] > 5)

if __name__ == '__main__':
    unittest.main()
