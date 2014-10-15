"""kinematic physic engine, meant as being as simple as possible while mimicking a simple 2D physic engine."""

import collections

import numpy as np
try:
    import pygame.gfxdraw
except ImportError:
    pass

class Ball(object):

    def __init__(self, dt, radius, mass, pos, init_vel=(0.0, 0.0), friction=0.0, static=False, color=(128, 128, 128)):
        self.radius    = radius
        self.mass      = mass
        self.friction  = friction*dt
        self.static    = static
        self.dt        = dt

        self.positions = [np.array(pos)-self.dt*np.array(init_vel), np.array(pos)]
        self.updated   = True

        self.name      = ''
        self.color     = color

    @property
    def pos(self):
        return self.positions[-1]

    @property
    def vel(self):
        return (self.positions[-1]-self.positions[-2])/self.dt

    @property
    def step_vel(self):
        return self.positions[-1]-self.positions[-2]

    def pygame_draw(self, screen):
        pygame.gfxdraw.aacircle(screen, int(self.pos[0]), int(self.pos[1]), int(self.radius), self.color)

class Segment(object):

    def __init__(self, obj1, obj2, color=(128, 128, 128), static=True):
        self.obj1   = obj1
        self.obj2   = obj2
        self.color  = color
        self.static = static

    def pygame_draw(self, screen):
        pygame.gfxdraw.line(screen, int(self.obj1.pos[0]), int(self.obj1.pos[1]),
                                    int(self.obj2.pos[0]), int(self.obj2.pos[1]), self.color)

class World(object):

    def __init__(self, dt=1.0):
        self.dt = dt
        self.date = 0
        self.objects     = []
        self.collidables = []
        self.collisions  = []

    def step(self):
        for ball in self.objects:
            ball.updated = ball.static or False

        for i, ball in enumerate(self.collidables):
            for j in range(i+1, len(self.collidables)):
                if self.check_collision(ball, self.collidables[j]):
                    self.resolve_collision(ball, self.collidables[j])
        self.date += self.dt

        for ball in self.collidables:
            if not ball.updated:
                ball.positions.append(ball.pos + max(0.0, 1.0-ball.friction)*ball.step_vel)
                ball.updated = True

    def add(self, obj, passive=False):
        self.objects.append(obj)
        if not passive:
            self.collidables.append(obj)

    @classmethod
    def check_collision(cls, ball1, ball2):
        """Return true if colliding with another ball"""
        norm = (ball1.positions[-1] - ball2.positions[-1])**2
        norm = norm[0]+norm[1]
        return not(ball1.static and ball2.static) and norm < (ball1.radius + ball2.radius)**2

    def resolve_collision(self, ball1, ball2):
        """Elastic collision between two balls."""

        v1 = ball1.vel
        v2 = ball2.vel
        u12 = ball1.pos-ball2.pos
        u12_normsq = u12**2
        u12_normsq = u12_normsq[0]+u12_normsq[1]

        d12 = 2/(ball1.mass + ball2.mass)*np.dot(v1-v2, u12)/u12_normsq*u12

        if not ball1.static:
            ball1.positions.append(ball1.positions[-1] + self.dt*(v1 - ball1.mass*d12))
            ball1.updated = True
        if not ball2.static:
            ball2.positions.append(ball2.positions[-1] + self.dt*(v2 + ball2.mass*d12))
            ball2.updated = True

        self.collisions.append((self.date, (ball2.positions[-2] - ball1.positions[-2])*ball1.radius + ball1.positions[-2]))


def draw_pygame(screen, world):
    screen.fill((255, 255, 255))
    for obj in world.objects:
        pygame.draw.circle(screen, (100, 100, 100), (int(obj.pos[0]),int(obj.pos[1])), int(obj.radius), 1)
    pygame.display.update()
