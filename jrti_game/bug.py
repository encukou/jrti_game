import math
import random

from pyglet import gl

from jrti_game.flippable import Flippable
from jrti_game.data import sprites
from jrti_game import game

MIN_SPEED = 190

class Bug(Flippable):
    transparent = True

    def __init__(self, **kwargs):
        kwargs.setdefault('width', 15)
        kwargs.setdefault('height', 15)
        kwargs.setdefault('instructions', 'Bug')
        self.rotation = 1
        self.speed = MIN_SPEED
        self.moment = random.uniform(-20, 20)
        super().__init__(**kwargs)
        self.x = random.uniform(0, self.parent.width - self.width * self.scale)
        self.y = random.uniform(0, self.parent.height - self.height * self.scale)

    def draw(self):
        gl.glPushMatrix()
        gl.glTranslatef(7.5, 7.5, 0)
        gl.glRotatef(self.rotation, 0, 0, 1)
        sprites['bug'].blit(-5.5, -5.5)

        leg = math.sin(game.state.time*32) * 0.5
        sprites['bugleg'].blit(-3.5+leg, -5.5)
        gl.glScalef(1, -1, 1)
        sprites['bugleg'].blit(-3.5-leg, -5.5)
        gl.glPopMatrix()

    def tick(self, dt):
        self.rotation += self.moment * dt
        if random.uniform(0, 1) < dt:
            self.rotation = -self.rotation + random.uniform(-90, 90)

        if self.flip_params is None:
            s = dt * self.speed
            angle = math.radians(self.rotation)
            dx = math.cos(angle) * self.speed * dt
            dy = math.sin(angle) * self.speed * dt
            nx = self.x + dx
            ny = self.y + dy
            self.moment += random.uniform(-dt, dt)
            if (0 <= nx < (self.parent.width - self.width*self.scale) and
                    0 <= ny < (self.parent.height - self.height*self.scale)):
                self.x = nx
                self.y = ny
            else:
                self.x -= dx
                self.y -= dy

                if not (0 <= self.x < (self.parent.width - self.width*self.scale) and
                        0 <= self.y < (self.parent.height - self.height*self.scale)):
                    self.die()

                self.rotation += 180
                self.moment += random.uniform(-90, 90)

                if abs(self.moment) > 180:
                    self.moment *= 1/2

                self.speed += random.uniform(-MIN_SPEED/4, MIN_SPEED/4)
                if abs(self.speed) > MIN_SPEED*2:
                    self.speed *= 1/2
                if self.speed < MIN_SPEED:
                    self.speed = MIN_SPEED
