import pygame
import sys

import dotdot
from environments.envs import physicx

pygame.init()
screen = pygame.display.set_mode((600,600))

dt = 0.01
w = physicx.World(dt=dt)
b1 = physicx.Ball(dt, 10.0, 1.0, (200.0, 305.0), init_vel=(2.0, 0.0), friction=0.00)
b2 = physicx.Ball(dt, 10.0, 1.0, (300.0, 300.0), init_vel=(0.0, 0.0), friction=0.00)
w.add(b1)
w.add(b2)

def draw_pygame(world):
    screen.fill((255, 255, 255))
    for obj in world.objects:
        pygame.draw.circle(screen, (100, 100, 100), (int(obj.pos[0]),int(obj.pos[1])), int(obj.radius), 1)
    pygame.display.update()

for t in range(100000):
    w.step()
    if t % 100 == 0:
        draw_pygame(w)

