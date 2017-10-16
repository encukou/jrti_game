from pyglet import gl
import math

from jrti_game.flippable import Flippable
from jrti_game.data import sprites
from jrti_game import game

class Bug(Flippable):
    def __init__(self, **kwargs):
        kwargs.setdefault('width', 15)
        kwargs.setdefault('height', 15)
        kwargs.setdefault('instructions', 'Bug')
        self.rotation = 1
        super().__init__(**kwargs)

    def draw(self):
        gl.glPushMatrix()
        gl.glTranslatef(7.5, 7.5, 0)
        gl.glRotatef(game.state.time*32, 0, 0, 1)
        sprites['bug'].blit(-5.5, -5.5)

        leg = math.sin(game.state.time*32) * 0.5
        sprites['bugleg'].blit(-3.5+leg, -5.5)
        gl.glScalef(1, -1, 1)
        sprites['bugleg'].blit(-3.5-leg, -5.5)
        gl.glPopMatrix()
