import math

from pyglet import gl

from jrti_game.data import sprites
from jrti_game.state import state
from jrti_game.util import clamp, interp
from jrti_game.coords import tool_to_main_screen


class Tool:
    size = 0
    scale = 0
    speed = 0
    name = 'none'
    grabbing = None

    def draw(self):
        pass

    def deactivate(self):
        pass

    def tick(self, dt):
        pass

    def move(self, dx, dy):
        state.tool_x += dx
        state.tool_y += dy
        self.speed = dx + dy


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
            self.grabbing = False
            if self.grab_time < state.time - self.grab_duration:
                self.grab_time = state.time

    def grab(self):
        self.active = not self.active
        if not self.active:
            self.grabbing = False
        if self.grab_time < state.time - self.grab_duration:
            self.grab_time = state.time

    def tick(self, dt):
        if self.grab_time < state.time - self.grab_duration:
            if self.active and not self.grabbing:
                x, y = tool_to_main_screen(state.tool_x, state.tool_y)
                for obj, x, y in state.main_screen.hit_test_all(x, y):
                    if obj.hit_test_grab(x, y):
                        self.grabbing = obj
                        break
                else:
                    self.deactivate()

    def move(self, dx, dy, recursing=False):
        blocker = False
        if self.grabbing:
            moved = False
            scale = state.zoom
            g = self.grabbing
            obj = g.parent
            while obj:
                scale *= obj.scale
                obj = obj.parent
            new_x = g.x + dx / scale
            new_y = g.y + dy / scale
            gs = g.scale
            blocker = self.calc_hit(new_x, new_y)
            if not blocker:
                g.x += dx / scale
                g.y += dy / scale
                moved = True
        super().move(dx, dy)
        x, y = tool_to_main_screen(state.tool_x, state.tool_y)
        for obj, x, y in state.main_screen.hit_test_all(x, y):
            if obj is self.grabbing and obj.hit_test(x, y):
                break
        else:
            self.deactivate()
        return

    def calc_hit(self, new_x, new_y):
        g = self.grabbing
        children = g.parent.children
        for sibling in children:
            if sibling is not g:
                x = (new_x - sibling.x) / sibling.scale
                y = (new_y - sibling.y) / sibling.scale
                w = g.width * g.scale / sibling.scale
                h = g.height * g.scale / sibling.scale
                if sibling.hit_test_slab(x, y, w, h):
                    print('Hit', sibling, x, y, w, h)
                    return sibling
        return False

    def try_move(self, dx, dy, scale):
            g = self.grabbing


class Key(Tool):
    size = 7
    scale = 3

    def draw(self):
        gl.glColor3f(0.4, 0.9, 0.1)
        sprites['key'].blit(-4.5, -4.5)
