import math
from math import pi
import random

from pyglet import gl

from jrti_game.flippable import Flippable, Layer
from jrti_game.text import Letter
from jrti_game.data import sprites, spritesheet_data
from jrti_game.util import reify, draw_rect
from jrti_game.state import state

tau = pi*2
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
        self.x = random.uniform(
            0, self.parent.width - self.width * self.scale)
        self.y = random.uniform(
            0, self.parent.height - self.height * self.scale)

    def draw(self):
        gl.glPushMatrix()
        gl.glTranslatef(7.5, 7.5, 0)
        gl.glRotatef(self.rotation, 0, 0, 1)
        sprites['bug'].blit(-5.5, -5.5)

        leg_time = state.time*32

        legx = math.sin(leg_time) * 0.5
        legy = 0
        if self.flip_params or state.tool.grabbing is self:
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

        if not self.flip_params and state.tool.grabbing is not self:
            self.moment *= 0.25 ** dt
            if random.uniform(0, 0.1) < dt:
                self.moment += random.uniform(-60, 60)
            if random.uniform(0, 1) < dt:
                self.moment += random.uniform(-180, 180)
            self.rotation += self.moment * dt
            s = dt * self.speed
            dx = math.cos(angle) * s
            dy = math.sin(angle) * s
            nx = self.x + dx
            ny = self.y + dy
            self.moment += random.uniform(-dt, dt)

            max_x = self.parent.width - self.width*self.scale
            max_y = (self.parent.height - self.height*self.scale)

            if 0 <= nx < max_x and 0 <= ny < max_y:
                self.x = nx
                self.y = ny
            else:
                self.x -= dx
                self.y -= dy

                if not (0 <= self.x < max_x and 0 <= self.y < max_y):
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

    def hit_test_grab(self, x, y):
        print(x, y)
        x -= self.width / 2
        y -= self.height / 2
        s = math.sin(math.radians(self.rotation))
        c = math.cos(math.radians(self.rotation))
        x = x * c - y * s
        y = x * s + y * c
        x += self.width / 2 + 1
        y += self.height / 2 - 5

        if x > 11 or y > 11:
            return False
        return spritesheet_data[28 + int(y)][3*8+1 + int(x)]

    def hit_test_slab(self, x, y, w, h):
        return False

    def homed(self):
        pass


class RangingBug(Bug):
    def tick(self, dt):
        super().tick(dt)
        if random.uniform(0, 30) < dt:
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

    def spawn_bug(self):
        bug = RangingBug(parent=self)
        while True:
            letter = random.choice(self.children)
            if isinstance(letter, Letter):
                if letter.scale < 8 and random.randrange(0, 6):
                    continue
                x = random.randrange(0, letter.width)
                y = random.randrange(0, letter.height)
                if all(letter.pixel(x+xx, y+yy)
                       for xx in (0, 1) for yy in (0, 1)):
                    bug.x = letter.x + x * letter.scale
                    bug.y = letter.y + y * letter.scale
                    bug.rotation = random.normalvariate(90, 30)
                    if random.randrange(2):
                        bug.rotation = -bug.rotation
                    return bug

    @property
    def num_bugs(self):
        return len([c for c in self.children if isinstance(c, Bug)])

    @property
    def home_coords(self):
        l = self.o_letter
        return l.x + l.scale * 3.5, l.y + l.scale * 4

    @reify
    def o_letter(self):
        for child in self.children:
            if child.instructions == 'O':
                return child

    def draw(self):
        gl.glColor3f(.1, .1, .1)
        draw_rect(self.width, self.height)
        super().draw()

    def hit_test_overlap(self, s, a, b, mode):
      def d(s,a,b):
        a += 0.0001
        a -= 1
        b -= 0.0001
        if mode == 'x+':
            if a < self.height and 0 < b:
                return s-self.width-1
        elif mode == 'x-':
            if a < self.height and 0 <= b:
                return -s
        elif mode == 'y+':
            if a < self.width and 0 <= b:
                return s-self.height-1
        elif mode == 'y-':
            if a < self.width and 0 <= b:
                return -s
        return -100
      d= d(s,a,b)
      print(d,s,a,b)
      return d
