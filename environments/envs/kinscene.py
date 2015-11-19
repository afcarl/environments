from __future__ import print_function, division, absolute_import
import numbers
import collections

import numpy as np
try:
    import pygame
except ImportError:
    pass

import scicfg

from .. import MotorPrimitive, SensoryPrimitive, PrimitiveEnvironment, Channel
from .. import tools
from .. import mprims


from .kinchain import KinematicArm2D
from . import physicx

_objcfg = scicfg.SciConfig()
_objcfg._describe('radius', instanceof=numbers.Real)
_objcfg._describe('mass', instanceof=numbers.Real)
_objcfg._describe('pos', instanceof=collections.Iterable)
_objcfg._describe('track', instanceof=bool)


_sp_cfg = scicfg.SciConfig()
_sp_cfg._describe('x_limits', instanceof=collections.Iterable, default=(-1000, 1000))
_sp_cfg._describe('y_limits', instanceof=collections.Iterable, default=(-1000, 1000))

class Displacement(SensoryPrimitive):

    def __init__(self, cfg):
        self.s_channels = (Channel('x', bounds=cfg.s_prims.x_limits), Channel('y', bounds=cfg.s_prims.y_limits))
        self.object_name = 'tip'

    def process_raw_sensors(self, raw_sensors):
        s_vector = raw_sensors['{}_pos'.format(self.object_name)][-1] # - raw_sensors['tip_pos'][0]
        return tools.to_signal(s_vector, self.s_channels)


_defcfg = KinematicArm2D.defcfg._deepcopy()
_defcfg.classname = 'environments.envs.KinScene2D'

_defcfg._describe('headless', instanceof=bool, default=False)
_defcfg._describe('dt', instanceof=numbers.Real, default=0.01)
_defcfg._branch('tip')
_defcfg._describe('tip.mass', instanceof=numbers.Real)
_defcfg._describe('tip.radius', instanceof=numbers.Real)


_defcfg._branch('objects')
_defcfg.objects._strict(False)

_defcfg._branch('mprims')

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
            self.screen = pygame.display.set_mode((self.cfg.s_prims.x_limits[1] - self.cfg.s_prims.x_limits[0],
                                                   self.cfg.s_prims.y_limits[1] - self.cfg.s_prims.y_limits[0]))

    def draw_pygame(self, world):
        if not self.cfg.headless:
            self.screen.fill((255, 255, 255))
            for obj in world.objects:
                obj.pygame_draw(self.screen)
#                pygame.draw.circle(self.screen, (100, 100, 100), (int(obj.pos[0]),int(obj.pos[1])), int(obj.radius), int(obj.radius/10.0))
            pygame.display.update()

    def _create_primitives(self, cfg):
        assert self.cfg is cfg

        self.m_prim = mprims.create_mprim(self.cfg)
        self.s_prim = Displacement(self.cfg)

    def _tip_pose(self, arm_pose):
        return (arm_pose['x{}'.format(self.dim)],
                arm_pose['y{}'.format(self.dim)])

    def _execute_raw(self, motor_cmd, meta=None):
        w = physicx.World(dt=self.cfg.dt, limits=(self.cfg.s_prims.x_limits, self.cfg.s_prims.y_limits))
        self.objects = {}

        # arm
        arm_pose = self.kinarm._multiarm.forward_kin(motor_cmd[0])
        tip_xy   = self._tip_pose(arm_pose)
        tip = physicx.Ball(self.cfg.dt, self.cfg.tip.radius, self.cfg.tip.mass, tip_xy, static=True, color=(123, 184, 249))
        tip.name = 'tip'
        self.objects['tip'] = tip
        w.add(tip)
        if not self.cfg.headless:
            self.joints = []
            for i in range(self.dim):
                joint_xy = (arm_pose['x{}'.format(i)],
                            arm_pose['y{}'.format(i)])
                joint = physicx.Ball(self.cfg.dt, 2, 0.0, joint_xy, static=True, color=(220, 220, 220))
                w.add(joint, passive=True)
                self.joints.append(joint)
                if i > 0:
                    w.add(physicx.Segment(self.joints[-1], self.joints[-2], color=(220, 220, 220)), passive=True)
                if i == self.dim-1:
                    w.add(physicx.Segment(self.joints[-1], tip, color=(220, 220, 220)), passive=True)
        self.draw_pygame(w)

        # objects
        for obj_name, obj_cfg in self.cfg.objects._children_items():
            color =  (232,74,5) if obj_cfg.track else (11,72,107)
            obj = physicx.Ball(self.cfg.dt, obj_cfg.radius, obj_cfg.mass, obj_cfg.pos, static=False, color=color)
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
