import math
from math import tau, pi
import random

from pyglet import gl

from jrti_game.flippable import Flippable, Layer
from jrti_game.data import sprites
from jrti_game.util import reify, draw_rect, clamp
from jrti_game.state import state

MIN_SPEED = 190

class Bug(Flippable):
    transparent = True
    homing = False

    def __init__(self, **kwargs):
        kwargs.setdefault('width', 15)
        kwargs.setdefault('height', 15)
        kwargs.setdefault('instructions', 'Bug')
        self.rotation = random.uniform(-180, 180)
        self.speed = MIN_SPEED
        self.moment = random.uniform(-20, 20)
        super().__init__(**kwargs)
        self.x = random.uniform(0, self.parent.width - self.width * self.scale)
        self.y = random.uniform(0, self.parent.height - self.height * self.scale)

    def draw(self):
        #if self.homing:
        #    gl.glColor3f(1, 0, 0)
        gl.glPushMatrix()
        gl.glTranslatef(7.5, 7.5, 0)
        gl.glRotatef(self.rotation, 0, 0, 1)
        sprites['bug'].blit(-5.5, -5.5)

        leg_time = state.time*32

        legx = math.sin(leg_time) * 0.5
        legy = 0
        if self.flip_params:
            legx /= 2
            legy = math.cos(leg_time * 8/7) * 0.25
        sprites['bugleg'].blit(-3.5+legx, -5.5+legy)
        gl.glScalef(1, -1, 1)
        sprites['bugleg'].blit(-3.5-legx, -5.5+legy)
        gl.glPopMatrix()

    def tick(self, dt):
        super().tick(dt)
        angle = math.radians(self.rotation)

        hx, hy = self.parent.home_coords
        d = (self.y - hy) ** 2 + (self.x - hx) ** 2
        if d < 16**2:
            self.homing = False
            self.homed()
            if not self.parent:
                return
        if self.homing:
            a = (angle - math.atan2(self.y - hy, self.x - hx) + pi) % tau - pi
            self.moment *= 0.075 ** dt
            self.moment += math.degrees(a) * dt * 5
            self.rotation += math.degrees(a * dt * 3 * (math.exp(-d/1000)))

        if not self.flip_params:
            if random.uniform(0, 2) < dt:
                self.rotation = -self.rotation + random.uniform(-90, 90)
            if random.uniform(0, 0.4) < dt:
                self.moment += random.uniform(-30, 30)
            if random.uniform(0, 0.8) < dt:
                self.moment += random.uniform(-90, 90)
            self.rotation += self.moment * dt
            s = dt * self.speed
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
        else:
            if random.uniform(0, 1/10) < dt:
                self.rotation += random.uniform(-5, 5)

    def homed(self):
        pass


class RangingBug(Bug):
    def tick(self, dt):
        super().tick(dt)
        if random.uniform(0, 10) < dt:
            self.homing = True

    def homed(self):
        self.die()


class BugArena(Layer):
    def draw(self):
        super().draw()
        letter = self.o_letter
        scale = letter.scale
        gl.glColor3f(0, 0, 0)
        gl.glPushMatrix()
        gl.glTranslatef(letter.x + scale * 3, letter.y + scale * 2, 0)
        draw_rect(scale * 1,
                  scale * 4)
        gl.glPopMatrix()

    @property
    def home_coords(self):
        l = self.o_letter
        return l.x + l.scale * 3.5, l.y + l.scale * 4

    @reify
    def o_letter(self):
        for child in self.children:
            if child.instructions == 'O':
                return child
