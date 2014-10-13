from __future__ import print_function, division, absolute_import
import numbers
import collections

import numpy as np
try:
    import pygame
except ImportError:
    pass

import forest

from .. import MotorPrimitive, SensoryPrimitive, PrimitiveEnvironment, Channel
from .. import tools

from .kinchain import KinematicArm2D
from . import physicx

_objcfg = forest.Tree()
_objcfg._describe('radius', instanceof=numbers.Real)
_objcfg._describe('mass', instanceof=numbers.Real)
_objcfg._describe('pos', instanceof=collections.Iterable)
_objcfg._describe('track', instanceof=bool)


_mp_cfg = forest.Tree()
_mp_cfg._describe('init_pos', instanceof=collections.Iterable)
_mp_cfg._describe('steps', instanceof=numbers.Integral)
_mp_cfg._describe('angular_step', instanceof=numbers.Real)

class MotorSteps(MotorPrimitive):

    def __init__(self, cfg):
        self.cfg = cfg

        assert len(self.cfg.m_prims.init_pos) == self.cfg.dim

        limits = self.cfg.limits
        if not isinstance(limits[0], collections.Iterable):
            limits = tuple(limits for _ in range(self.cfg.dim))
        assert len(limits) == self.cfg.dim
        self.m_channels = [Channel('j{}'.format(i), bounds=limits[i]) for i, l_i in enumerate(limits)]

        self.step = self.cfg.m_prims.angular_step

    def process_motor_signal(self, m_signal):
        m_vector = np.array(tools.to_vector(m_signal, self.m_channels))
        init_pos = np.array(self.cfg.m_prims.init_pos)
        signs    = np.sign(m_vector-init_pos)
        step     = np.array([self.step]*len(init_pos))
        max_t    = int(max(np.abs(m_vector-init_pos))/self.step) + 1

        traj = tuple(tuple(init_pos + signs*np.fmin(np.abs(m_vector-init_pos), t*step)) for t in range(max_t))
        return traj


_sp_cfg = forest.Tree()

class Displacement(SensoryPrimitive):

    def __init__(self, cfg):
        self.s_channels = (Channel('x', bounds=(-100, 100)), Channel('y', bounds=(-100, 100)))
        self.object_name = 'tip'

    def process_raw_sensors(self, raw_sensors):
        s_vector = raw_sensors['{}_pos'.format(self.object_name)][-1] # - raw_sensors['tip_pos'][0]
        return tools.to_signal(s_vector, self.s_channels)


_defcfg = KinematicArm2D.defcfg._copy(deep=True)
_defcfg._describe('headless', instanceof=bool, default=False)
_defcfg._describe('dt', instanceof=numbers.Real, default=0.01)
_defcfg._branch('tip')
_defcfg._describe('tip.mass', instanceof=numbers.Real)
_defcfg._describe('tip.radius', instanceof=numbers.Real)

_defcfg.classname = 'environments.envs.KinScene2D'

_defcfg._branch('objects')
_defcfg.objects._strict(False)

_defcfg._branch('m_prims')
_defcfg.m_prims._update(_mp_cfg)

_defcfg._branch('s_prims')
_defcfg.s_prims._update(_sp_cfg)



class KinScene2D(PrimitiveEnvironment):

    defcfg = _defcfg
    objcfg = _objcfg

    def __init__(self, cfg):
        super(KinScene2D, self).__init__(cfg)
        self.kinarm = KinematicArm2D(cfg)
        self.dim = self.kinarm.dim
        self.screen = None
        if not self.cfg.headless:
            self.screen = pygame.display.set_mode((600,600))

    def draw_pygame(self, world):
        if not self.cfg.headless:
            self.screen.fill((255, 255, 255))
            for obj in world.objects:
                obj.pygame_draw(self.screen)
#                pygame.draw.circle(self.screen, (100, 100, 100), (int(obj.pos[0]),int(obj.pos[1])), int(obj.radius), int(obj.radius/10.0))
            pygame.display.update()

    def _create_primitives(self, cfg):
        assert self.cfg is cfg

        self.m_prim = MotorSteps(self.cfg)
        self.s_prim = Displacement(self.cfg)

    def _tip_pose(self, arm_pose):
        return (arm_pose['x{}'.format(self.dim)],
                arm_pose['y{}'.format(self.dim)])

    def _execute_raw(self, motor_cmd, meta=None):
        w = physicx.World(dt=self.cfg.dt)
        self.objects = {}

        # arm
        arm_pose = self.kinarm._multiarm.forward_kin(motor_cmd[0])
        tip_xy   = self._tip_pose(arm_pose)
        tip = physicx.Ball(self.cfg.dt, self.cfg.tip.radius, self.cfg.tip.mass, tip_xy, static=True, color=(214,129,137))
        tip.name = 'tip'
        self.objects['tip'] = tip
        w.add(tip)
        if not self.cfg.headless:
            self.joints = []
            for i in range(self.dim):
                joint_xy = (arm_pose['x{}'.format(i)],
                            arm_pose['y{}'.format(i)])
                joint = physicx.Ball(self.cfg.dt, self.cfg.tip.radius, 0.0, joint_xy, static=True, color=(198,229,217))
                w.add(joint, passive=True)
                self.joints.append(joint)
                if i > 0:
                    w.add(physicx.Segment(self.joints[-1], self.joints[-2], color=(198,229,217)), passive=True)
                if i == self.dim-1:
                    w.add(physicx.Segment(self.joints[-1], tip, color=(198,229,217)), passive=True)
        self.draw_pygame(w)

        # objects
        for obj_name, obj_cfg in self.cfg.objects._children_items():
            obj = physicx.Ball(self.cfg.dt, obj_cfg.radius, obj_cfg.mass, obj_cfg.pos, static=False, color=(233,78,119))
            obj.name = obj_name
            w.add(obj)
            self.objects[obj_name] = obj
            if obj_cfg.track:
                self.s_prim.object_name = obj_name


        for t, pose in enumerate(motor_cmd):
            # forward kin
            arm_pose = self.kinarm._multiarm.forward_kin(pose)
            tip_xy = self._tip_pose(arm_pose)
            # update ball pos
            tip.positions.append(np.array(tip_xy))
            w.step()
            if t % 10 == 0:
                if not self.cfg.headless:
                    for i in range(self.dim):
                        joint_xy = (arm_pose['x{}'.format(i)],
                                    arm_pose['y{}'.format(i)])
                        self.joints[i].positions.append(np.array(joint_xy))
                self.draw_pygame(w)

        # apply sprim on tracked object
        raw_sensors = {'{}_pos'.format(obj_name): obj.positions for obj_name, obj in self.objects.items()}
        return raw_sensors

