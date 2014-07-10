from __future__ import absolute_import, print_function, division

import math
import sys
import random
import collections

from .. import environment as env
from .. import tools


class RevJoint(object):
    """RevoluteJoint. Has one parent, and possibly several descendants"""

    def __init__(self, length = 1.0, limits = (-150.0, 150.0), orientation = 0.0,
                       feats = (None, None, None)):
        """
        @param length       the length of the body attached to the joint
        @param orientation  the initial orientation of the joints.
                            Limits are enforced relative to the origin.
        @param limits       the possible angle range.
        @param feats        tuple of available feats for the joint (x, y, angle)
                            None if not available
        """
        self.length  = length
        self.origin  = orientation
        self.limits  = tuple(limits)
        self.nodes   = []
        #assert len(feats) == 3
        self.feats = feats

    def forward_kin(self, pos_ref, a):
        """Compute the position of the end of the body attached to the joint
        @param x_ref, y_ref, a_ref  position and orientation of the end of the parent.
        @param a                    the angle requested (to be checked against limits)
        """
        a_min, a_max = self.limits
        a_legal = min(max(a_min, a), a_max)

        x_ref, y_ref, a_ref = pos_ref
        a_end = a_legal + self.origin + a_ref
        x_end = x_ref + self.length*math.cos(math.radians(a_end))
        y_end = y_ref + self.length*math.sin(math.radians(a_end))

        pos_end = x_end, y_end, a_end

        reading = {} if self.feats is None else {f : pos_end[i] for i, f in enumerate(self.feats) if f is not None}

        return pos_end, reading

    def add_node(self, node):
        self.nodes.append(node)


class MultiArm2D(object):
    """MultiArm class. Can simulate any revolute, non-cyclic kinematic tree.
    Order can be shuffled. Features cannot be shuffled yet.
    """

    def __init__(self):
        self.root = None
        self.joints = []
        self.readings = {}
        self.bounds = ()
        self.motormap = []

    def add_joint(self, parent, joint):
        if parent is None:
            assert len(self.joints) == 0, 'Tried to create a root in a non-empty multiarm'
            self.root = joint
        else:
            parent.add_node(joint)
        self.joints.append(joint)
        self.motormap.append(-len(self.motormap)-1)
        self._update_bounds()
        return joint

    def add_joint_randomly(self, joint):
        if self.root is None:
            return self.add_joint(None, joint)
        else:
            parent = random.choice(self.joints)
            return self.add_joint(parent, joint)

    def _shuffle_motors(self):
        """Shuffle the motors, that is, to which joints order values are applied.
        (should be done once at start, to randomize structure)
        """
        random.shuffle(self.motormap)

    def _reorder_order(self, order):
        return [order[i] for i in self.motormap]

    def forward_kin(self, order):
        """Compute the position of the end effector"""
        assert len(order) == len(self.joints), 'Exepcted an order with {} values, got {}'.format(len(self.joints), len(order))
        order_ed = self._reorder_order(order)
        self.readings = {}
        assert len(self._forward_spider(order_ed, (0.0, 0.0, 0.0), self.root)) == 0
        return self.readings

    def _forward_spider(self, ordertail, pos_ref, joint):
        a = ordertail[0]
        ordertail = ordertail[1:]
        pos_end, reading = joint.forward_kin(pos_ref, a)
        self.readings.update(reading)
        for j in joint.nodes:
            ordertail = self._forward_spider(ordertail, pos_end, j)
        return ordertail

    def _update_bounds(self):
        self.bounds = self._bounds_spider(self.root)

    def _bounds_spider(self, joint):
        bounds = [joint.limits]
        for j in joint.nodes:
            bounds += self._bounds_spider(j)
        return bounds


defcfg = env.Environment.defcfg._copy(deep=True)
defcfg._describe('dim', instanceof=int, default=6)
defcfg._describe('limits', instanceof=collections.Iterable, default=(-150, 150))
defcfg._describe('lengths', instanceof=(float, collections.Iterable), default=1.0)
defcfg.classname = 'environments.envs.KinematicArm2D'


class KinematicArm2D(env.Environment):
    """Interface for the kinematics of an arm"""

    defcfg = defcfg

    def __init__(self, cfg):
        """\
        :param cfg:  Configuration parameters:
                     cfg.dim      the number of joints
                     cfg.limits   the max angles of each joints
                     cfg.lengths  the length of each joints
        """
        super(KinematicArm2D, self).__init__(cfg)

        self.dim      = self.cfg.dim
        sys.setrecursionlimit(10000)#self.dim+1)

        self._init_robot(self.cfg.lengths, self.cfg.limits)

        self.m_channels = [env.Channel('j{}'.format(i), bounds=b_i) for i, b_i in enumerate(self.limits)]
        s_bounds = (-sum(self.lengths), sum(self.lengths))
        self.s_channels = [env.Channel('x', bounds=s_bounds), env.Channel('y', bounds=s_bounds)]

    def _init_robot(self, lengths, limits):
        self._multiarm = MultiArm2D()

        # create self.lengths
        if not isinstance(lengths, collections.Iterable):
            lengths = tuple(lengths for _ in range(self.dim))
        assert len(lengths) == self.dim
        self.lengths = lengths

        # create self.limits
        if not isinstance(limits[0], collections.Iterable):
            limits = tuple(limits for _ in range(self.dim))
        assert len(limits) == self.dim
        assert all(len(l_i) == 2 for l_i in limits)
        self.limits = limits

        j = None
        for i in range(self.dim):
            feats = None if i < self.dim-1 else (0, 1, None) # x,y for the tip only
            j = self._multiarm.add_joint(j, RevJoint(length = self.lengths[i], limits = self.limits[i], orientation = 0.0, feats = feats))

    def _execute(self, m_signal, meta=None):
        m_vector = tools.to_vector(m_signal, self.m_channels)
        s_vector = self._multiarm.forward_kin(m_vector)
        s_vector = (s_vector[0], s_vector[1])
        return tools.to_signal(s_vector, self.s_channels)

    def __repr__(self):
        return "KinematicArm2D(dim = {}, lengths = {}, limits = {})".format(
               self.dim, self.lengths, self.limits)
