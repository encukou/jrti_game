from pyglet import gl

from jrti_game.flippable import Flippable
from jrti_game.data import sprites, spritesheet_data
from jrti_game.util import draw_rect_xy
from jrti_game.state import state
from jrti_game.text import draw_string
from jrti_game.util import clamp


class Adjuster(Flippable):
    endgen = None

    def draw(self, zoom, **kwargs):
        gl.glColor3f(1, 1, 1)
        if zoom > 1:
            draw_rect_xy(11, 12, 1, 80)
        elif zoom > 1/64:
            gl.glBegin(gl.GL_LINES)
            gl.glVertex2f(12, 12)
            gl.glVertex2f(12, 12+80)
            gl.glEnd()
        if zoom > 1/64:
            pos = state.key_config[self.index]
            sprites['adjuster'].blit(0, pos*8)

    def hit_test(self, x, y):
        pos = state.key_config[self.index]
        return 0 < x < 24 and 0 < y-pos*8 < 24

    def hit_test_grab(self, x, y):
        pos = state.key_config[self.index]
        return spritesheet_data[3*8+1+int(y-pos*8)][96+int(x)]

    def grab_move(self, dx, dy):
        pos = state.key_config[self.index]
        pos = clamp(pos + dy*16, 0, 9)
        state.key_config[self.index] = pos
        return True

    def draw_grab(self, *args, **kwargs):
        pass
