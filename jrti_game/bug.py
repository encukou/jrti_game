import math
from math import pi
import random
import colorsys

from pyglet import gl

from jrti_game.flippable import Flippable, Layer
from jrti_game.text import Letter
from jrti_game.data import sprites, spritesheet_data
from jrti_game.util import reify, draw_rect, clamp
from jrti_game.state import state

tau = pi*2


class Bug(Flippable):
    transparent = True
    homing = False
    homed = False
    s_to_homing = 30

    def __init__(self, **kwargs):
        kwargs.setdefault('width', 15)
        kwargs.setdefault('height', 15)
        kwargs.setdefault('instructions', 'Bug')
        kwargs.setdefault('color', colorsys.hsv_to_rgb(
            random.uniform(0, 1),
            random.uniform(0.2, 0.4),
            random.uniform(0.8, 0.9),
        ))
        self.rotation = random.uniform(-180, 180)
        self.speed = self.min_speed = 190
        self.moment = random.uniform(-20, 20)
        super().__init__(**kwargs)
        self.x = random.uniform(
            0, self.parent.width - self.width * self.scale)
        self.y = random.uniform(
            0, self.parent.height - self.height * self.scale)

    def draw(self, **kwargs):
        gl.glPushMatrix()
        gl.glTranslatef(7.5, 7.5, 0)
        gl.glRotatef(self.rotation, 0, 0, 1)
        sprites['bug'].blit(-5.5, -5.5)

        if self.min_speed > 100:
            leg_time = state.time*32
        else:
            leg_time = state.time*16

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

        ox, oy = self.parent.o_coords
        if (((self.y - oy)/1.5) ** 2 + (self.x - ox) ** 2) < 16**2:
            self.parent.at_o(self)
            if not self.parent:
                return

        hx, hy = self.parent.home_coords
        d = (self.y - hy) ** 2 + (self.x - hx) ** 2
        self.home_distance2 = d
        homed = d < 7**2
        if homed:
            if not self.homed:
                self.homed = True
                self.speed = 1
        if (((self.y - hy) / 1.5) ** 2 + (self.x - hx) ** 2) < 5**2:
            self.min_speed = self.speed = 5
        elif self.homing:
            a = (angle - math.atan2(self.y - hy, self.x - hx) + pi) % tau - pi
            self.moment *= 0.075 ** dt
            if a > tau/180:
                self.moment += math.degrees(a) * dt * 5
            self.rotation += clamp(
                math.degrees(a * dt * 3 * (math.exp(-d/5000))),
                -abs(a), abs(a))

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

                ms = self.min_speed
                self.speed += random.uniform(-ms/4, ms/4)
                if abs(self.speed) > ms*2:
                    self.speed *= 1/2
                if self.speed < ms:
                    self.speed = ms
        else:
            if random.uniform(0, 1/10) < dt:
                self.rotation += random.uniform(-5, 5)

        if random.uniform(0, self.s_to_homing) < dt:
            self.homing = True

    def hit_test_grab(self, x, y):
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


class BugArena(Layer):
    def draw(self, **kwargs):
        gl.glColor3f(.1, .1, .1)
        draw_rect(self.width, self.height)
        super().draw(**kwargs)

    def add_child(self, child):
        super().add_child(child)
        if isinstance(child, Letter):
            child.hides_bugs = True
            child.num_hiding_bugs = 2
            child.bgcolor = self.bgcolor

    def spawn_bug(self, letter=None, s_to_homing=30):
        orig_letter = letter
        while not isinstance(letter, Letter):
            letter = random.choice(self.children)

        closest = 1000
        closest_i = 0
        num_close_bugs = 0
        for i, child in enumerate(self.children):
            dist2 = getattr(child, 'home_distance2', 1000)
            if dist2 < 8**2:
                num_close_bugs += 1
                if dist2 < closest:
                    closest = dist2 + i/10
                    closest_i = i

        if num_close_bugs > 15:
            self.children[closest_i].die()
        bug = Bug(parent=self)
        while True:
            if letter.scale < 8 and random.randrange(0, 6):
                continue
            x = random.randrange(0, letter.width)
            y = random.randrange(0, letter.height)
            if all(letter.pixel(x+xx, y+yy)
                    for xx in (0, 1) for yy in (0, 1)):
                bug.x = letter.x + x * letter.scale
                bug.y = letter.y + y * letter.scale
                if orig_letter is None:
                    bug.rotation = random.normalvariate(90, 30)
                else:
                    bug.rotation = random.uniform(0, 180)
                if random.randrange(2):
                    bug.rotation = -bug.rotation
                if letter is self.o_letter:
                    bug.x += math.sin(math.radians(bug.rotation)) * 16
                    bug.y += math.sin(math.radians(bug.rotation)) * 24
                bug.s_to_homing = s_to_homing
                self.children.sort(key=lambda c: -isinstance(c, Bug))
                return bug

    def tick(self, dt):
        super().tick(dt)
        num_bugs = len([c for c in self.children
                        if isinstance(c, Bug) and not c.homed])
        s_to_bug = clamp((num_bugs-1/2)*4, 1, 100)
        if random.uniform(0, s_to_bug) < dt:
            self.spawn_bug()

    @property
    def o_coords(self):
        l = self.o_letter
        return l.x + l.scale * 2.5, l.y + l.scale * 3

    @reify
    def home_coords(self):
        return self.o_coords

    @reify
    def o_letter(self):
        for child in self.children:
            if child.instructions == 'O':
                child.num_hiding_bugs += 10
                return child

    def hit_test_overlap(self, s, a, b, mode):
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

    def at_o(self, bug):
        bug.die()
        self.o_letter.num_hiding_bugs = clamp(
            self.o_letter.num_hiding_bugs + 1, 0, 20)
