import math

from pyglet import gl

from jrti_game.data import sprites
from jrti_game.state import state
from jrti_game.util import clamp

class Tool:
    size = 0
    scale = 0
    speed = 0

    def draw(self):
        pass


class Grabby(Tool):
    size = 8*2-2
    scale = 3

    def draw(self):
        gl.glRotatef(90 + self.speed/2, 0, 0, 1)

        gl.glColor3f(0.9, 0.1, 0.4)
        sprites['grabby'].blit(0, 0)
        gl.glRotatef(90, 0, 0, 1)
        sprites['grabby'].blit(0, 0)
        gl.glRotatef(90, 0, 0, 1)
        sprites['grabby'].blit(0, 0)
        gl.glRotatef(90, 0, 0, 1)
        sprites['grabby'].blit(0, 0)
        gl.glRotatef(90, 0, 0, 1)

        gl.glColor3f(0.9, 0.4, 0.1)
        tr = (abs(math.sin(state.time * 3)) * 2 - 1)

        sprites['grabtooth'].blit(tr, tr)
        gl.glRotatef(90, 0, 0, 1)
        sprites['grabtooth'].blit(tr, tr)
        gl.glRotatef(90, 0, 0, 1)
        sprites['grabtooth'].blit(tr, tr)
        gl.glRotatef(90, 0, 0, 1)
        sprites['grabtooth'].blit(tr, tr)
        gl.glRotatef(90, 0, 0, 1)


class Key(Tool):
    size = 7
    scale = 3

    def draw(self):
        gl.glColor3f(0.4, 0.9, 0.1)
        sprites['key'].blit(-4.5, -4.5)
