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
        state.main_screen.update_instructions()
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
        state.zoom_easing = 0.7
        prev_zoom = state.target_zoom

        state.target_zoom = 1
        while state.zoom != state.target_zoom:
            yield

        if prev_zoom != 1:
            target = state.time + 0.25
            while state.time < target:
                yield

        state.target_zoom = 0.5
        while state.zoom != state.target_zoom:
            yield

        state.zoom_easing = 1
        angle = 0
        speed = 0
        state.main_screen.flip_locked = True
        while angle < 150:
            angle = clamp(angle+speed, 0, 150)
            speed += (yield) * 5
            state.main_screen.flip_params = 0, 0, angle, 0

    def accepts_key(self, key):
        return all(int(a) == int(b)
                   for a, b
                   in zip(state.key_config, state.code))
