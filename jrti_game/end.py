from pyglet import gl

from jrti_game.flippable import Sprite
from jrti_game.data import sprites, spritesheet_data
from jrti_game.util import draw_rect_xy
from jrti_game.state import state
from jrti_game.text import draw_string
from jrti_game.util import clamp


class Keyhole(Sprite):
    keyhole = 2, 18, 6.5, 13
    keyhole_params = 10, 800
    endgen = None

    def unlock(self, key):
        super().unlock(key)
        self.endgen = self.end_animation()
        next(self.endgen)
        state.ending = True
        state.end_time = state.time
        print('Done! Time = ', state.end_time)

    def tick(self, dt):
        super().tick(dt)
        if self.endgen:
            try:
                self.endgen.send(dt)
            except StopIteration:
                self.endgen = False
                state.ending = False


    def end_animation(self):
        yield
        state.min_zoom = 0.5
        state.target_zoom = 0.5
        while state.zoom != state.target_zoom:
            yield
        angle = 0
        state.main_screen.flip_locked = True
        while angle < 150:
            state.main_screen.flip_params = 0, 0, angle, 0
            angle += (yield) * 90
