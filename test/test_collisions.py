from __future__ import print_function, division, absolute_import
import unittest
import random

import dotdot
from environments.envs.collision2d import Segment, segment_intersection


class TestCollision(unittest.TestCase):

    def test_0(self):
        s1 = Segment(0, 0, 0, 1)
        s2 = Segment(1, 0, 1, 1)

        self.assertTrue(not segment_intersection(s1, s2))
        self.assertTrue(not segment_intersection(s1, s1))
        self.assertTrue(not segment_intersection(s2, s2))

        s1 = Segment(0, 0, 1, 1)
        s2 = Segment(0, 1, 1, 0)

        self.assertTrue(segment_intersection(s1, s2))


if __name__ == '__main__':
    unittest.main()
