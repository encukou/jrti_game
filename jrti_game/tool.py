import math

from pyglet import gl

from jrti_game.data import sprites
from jrti_game.state import state
from jrti_game.util import clamp, interp


class Tool:
    size = 0
    scale = 0
    speed = 0
    name = 'none'

    def draw(self):
        pass

    def deactivate(self):
        pass

    def tick(self, dt):
        pass


class Grabby(Tool):
    size = 8*2-2
    scale = 3
    active = False
    grab_time = 0
    name = 'grabby'
    grab_duration = 1/8

    def draw(self):
        gt = clamp((state.time - self.grab_time) / self.grab_duration, 0, 1)
        if not self.active:
            gt = 1-gt

        gl.glRotatef(90 + self.speed/2 + gt * 45, 0, 0, 1)

        gl.glColor3f(
            interp(0.9, 0.1, gt**(2)),
            interp(0.1, 0.9, gt**(1/2)),
            0.4 + 0.06 * 4 * gt * (1-gt)
        )
        for i in range(4):
            sprites['grabby'].blit(0, 0)
            gl.glRotatef(90, 0, 0, 1)

        gl.glColor3f(interp(0.9 * abs(math.cos(state.time * 3)), 0.1, gt),
                     interp(0.1 * math.sin(state.time * 3)**2, 0.9, gt),
                     0.2 * math.sin(state.time * 3)**2)
        tr = interp(
            (abs(math.sin(state.time * 3)) * 2 - 1),
            (-4.5),
            gt,
        )
        for i in range(4):
            sprites['grabtooth'].blit(tr, tr)
            gl.glRotatef(90, 0, 0, 1)

    def deactivate(self):
        if self.active:
            self.active = False
            if self.grab_time < state.time - self.grab_duration:
                self.grab_time = state.time

    def grab(self):
        self.active = not self.active
        if self.grab_time < state.time - self.grab_duration:
            self.grab_time = state.time

    def tick(self, dt):
        if self.grab_time < state.time - self.grab_duration and self.active:
            self.deactivate()


class Key(Tool):
    size = 7
    scale = 3

    def draw(self):
        gl.glColor3f(0.4, 0.9, 0.1)
        sprites['key'].blit(-4.5, -4.5)
