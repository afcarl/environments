import pygame
import sys

import dotdot
from environments.envs import physicx

# pygame.init()
# screen = pygame.display.set_mode((640,480))

dt = 0.05
w = physicx.World(dt=dt)
b1 = physicx.Ball(dt, 10.0, 1.0, (100.0, 105.0),  (50.0, 0.0))
b2 = physicx.Ball(dt, 10.0, 1.0, (130.0, 100.0),  (0.0, 0.0))
w.add(b1, b2)

def draw_pygame(world):
    screen.fill((255, 255, 255))
    for obj in world.objects:
        pygame.draw.circle(screen, (100, 100, 100), (int(obj.pos[0]),int(obj.pos[1])), int(obj.radius), 1)
    pygame.display.update()

for t in range(100000):
    w.step()
    # print(b1.pos)
    # draw_pygame(w)

