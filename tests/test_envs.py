from __future__ import print_function, division, absolute_import
import unittest
import random

import dotdot
import environments
from environments.envs import FirstSquare2D, SecondSquare2D
from environments.envs import KinematicArm2D
from environments.envs import VowelModel
from environments import tools


random.seed(0)

class TestSquare2D(unittest.TestCase):

    def test_first(self):
        cfg = FirstSquare2D.defcfg._copy()
        cfg.x_coo = (0.5, 1.0)
        cfg.y_coo = (0.5, 1.0)

        sq = FirstSquare2D(cfg)

        for _ in range(1000):
            m_signal = tools.random_signal(sq.m_channels)
            m_signal['a'] = random.uniform(0.0, 0.5)
            m_signal['b'] = random.uniform(0.0, 0.5)
            feedback = sq.execute(m_signal)
            s_signal = feedback['s_signal']
            self.assertEqual(s_signal['x'], 0.0)
            self.assertEqual(s_signal['y'], 0.0)

        for _ in range(1000):
            m_signal = tools.random_signal(sq.m_channels)
            m_signal['a'] = random.uniform(0.5, 1.0)
            m_signal['b'] = random.uniform(0.5, 1.0)
            feedback = sq.execute(m_signal)
            s_signal = feedback['s_signal']
            self.assertTrue(s_signal['x'] != 0.0)
            self.assertTrue(s_signal['y'] != 0.0)


class TestVowelModel(unittest.TestCase):

    def test_create(self):
        cfg = VowelModel.defcfg._copy()
        cfg.classname = 'environments.envs.VowelModel'
        vm = environments.Environment.create(cfg)

    def test_random(self):
        cfg = VowelModel.defcfg._copy()
        vm = VowelModel(cfg)

        for _ in range(1000):
            m_signal = tools.random_signal(vm.m_channels)
            feedback = vm.execute(m_signal)
            self.assertEqual(set(feedback['s_signal'].keys()), set(c.name for c in vm.s_channels))

class TestKinematicArm2D(unittest.TestCase):

    def test_random(self):
        cfg = KinematicArm2D.defcfg._copy()
        cfg.dim = 5
        cfg.lengths = 10.0
        cfg.limits  = (-150, 150)
        vm = KinematicArm2D(cfg)

        for _ in range(1000):
            m_signal = tools.random_signal(vm.m_channels)
            feedback = vm.execute(m_signal)
            self.assertEqual(set(feedback['s_signal'].keys()), set(c.name for c in vm.s_channels))

if __name__ == '__main__':
    unittest.main()
