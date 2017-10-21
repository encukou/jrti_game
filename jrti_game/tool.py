import math

from pyglet import gl

from jrti_game.data import sprites
from jrti_game.state import state
from jrti_game.util import clamp, interp
from jrti_game.coords import tool_to_main_screen, tool_to_logical


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
                        if obj.unlocked:
                            obj.unlocked.anim_start = state.time
                            continue
                        self.grabbing = obj
                        break
                else:
                    self.deactivate()

    def move(self, dx, dy):
        if self.grabbing:
            scale = state.zoom
            g = self.grabbing
            obj = g.parent
            while obj:
                scale *= obj.scale
                obj = obj.parent

        if self.grabbing and self.grabbing.grab_move(dx/scale, dy/scale):
            pass
        elif self.grabbing:
            gdx = dx
            gdy = dy

            # Find appropriate distances to all siblings
            # - If negative - overlapping, don't care
            # - If distance is less than dN, limit dN to that
            e0 = -0.0001
            for sibling in g.parent.children:
                x = (g.x - sibling.x) / sibling.scale
                y = (g.y - sibling.y) / sibling.scale
                w = g.width * g.scale / sibling.scale
                h = g.height * g.scale / sibling.scale
                if gdx < 0:
                    dist = sibling.hit_test_overlap(x, y, y+h, 'x+')
                    dist *= sibling.scale
                    if e0 <= dist <= -gdx:
                        gdx = -dist
                if gdx > 0:
                    dist = sibling.hit_test_overlap(x+w, y, y+h, 'x-')
                    dist *= sibling.scale
                    if e0 <= dist <= gdx:
                        gdx = dist
                if gdy < 0:
                    dist = sibling.hit_test_overlap(y, x, x+w, 'y+')
                    dist *= sibling.scale
                    if e0 <= dist <= -gdy:
                        gdy = -dist
                if gdy > 0:
                    dist = sibling.hit_test_overlap(y+h, x, x+w, 'y-')
                    dist *= sibling.scale
                    if e0 <= dist <= gdy:
                        gdy = dist

            g.x = clamp(g.x + gdx / scale, 0,
                        g.parent.width - g.width * g.scale)
            g.y = clamp(g.y + gdy / scale,
                        0, g.parent.height - g.height * g.scale)

            if gdx or gdy and g.hides_bugs:
                if (state.time - g.last_moved) > 0.5:
                    g.num_hiding_bugs += (state.time - g.last_moved) ** (1/3)
                g.last_moved = state.time

                hb = g.num_hiding_bugs
                db = abs(gdx + gdy) / self.scale
                left = clamp(hb - db, 0, 10)
                for i in range(int(left), int(hb)):
                    g.parent.spawn_bug(g, s_to_homing=4)
                g.num_hiding_bugs = left

        super().move(dx, dy)
        x, y = tool_to_main_screen(state.tool_x, state.tool_y)
        for obj, x, y in state.main_screen.hit_test_all(x, y):
            if obj is self.grabbing and obj.hit_test(x, y):
                break
        else:
            self.deactivate()


class Key(Tool):
    size = 7
    scale = 3
    anim_start = 0
    name = 'key'
    locked = None
    locking = False
    unlocked = False
    lock = None
    visible_len = 19
    fully_inserted = False
    lock_zoom = 0
    open_anim_start = 0

    def draw(self):
        anim = clamp((state.time - self.anim_start) * 4, 0, 1)
        length = self.visible_len
        if not self.locking:
            anim = 1-anim
        if self.unlocked:
            anim = 1
        gl.glRotatef(anim * 180, 1, 0, 0)
        if self.fully_inserted:
            gl.glColor3f(0.1, 0.9, 0.1 + anim*0.9)
        else:
            t = (self.visible_len-9) / 10
            gl.glColor3f(0.9, 0.9 - t*0.8, 0.1)
        texture = sprites['key']
        if length < 15:
            texture = texture.get_region(0, 0, width=min(length, 15), height=8)
        texture.blit(-4.5, -4.5)
        for i, num in enumerate(state.key_config):
            if i + 15 > length:
                break
            if i + 16 > length:
                width = length % 1
            else:
                width = 1
            if num < 5:
                y = -0.75+(num-5)/2
                height = 1-(num-5)/2+.25
            else:
                y = -0.75
                height = 1+(num-5)/2
            sprites['square'].blit(x=15-4.5+i, y=y, width=width, height=height)

    def turn(self):
        if self.anim_start < state.time - 1/4:
            self.locking = not self.locked
            self.anim_start = state.time

    def tick(self, dt):
        if self.anim_start:
            t = state.time - self.anim_start
            if self.locking:
                accepts = not self.lock or self.lock.accepts_key(self)
                if t > 1/4 and accepts:
                    if self.lock and self.fully_inserted:
                        self.lock.unlock(self)
                        self.unlocked = True
                        self.anim_start = self.open_anim_start = state.time
                        state.tool = Tool()
                    else:
                        self.locking = False
                        self.anim_start = state.time
                elif t > 1/16 and (not accepts or not self.fully_inserted):
                    if self.lock and self.visible_len < 19:
                        self.locking = False
                        self.anim_start = state.time - (1/4-t)

    def deactivate(self):
        self.lock = None
        self.visible_len = 19
        self.fully_inserted = False

    def move(self, dx, dy):
        if self.unlocked:
            return

        if dx < 0 or dy:
            self.deactivate()

        if dx > 0:
            if not self.lock:
                x, y = tool_to_main_screen(state.tool_x+14.5*3, state.tool_y)
                for obj, x, y in state.main_screen.hit_test_all(x, y):
                    if obj.keyhole and not obj.unlocked:
                        zoom = state.zoom
                        par = obj
                        while par:
                            zoom *= par.scale
                            par = par.parent
                        self.lock_zoom = zoom
                        kx, ky, kw, kh = obj.keyhole
                        kx -= dx / zoom
                        kw += dx / zoom
                        kmin, kmax = obj.keyhole_params
                        if (kx < x < kx+kw and ky < y < ky+kh and
                                kmin < kh * zoom < kmax):
                            self.lock = obj
                            break
            if self.lock:
                kx, ky, kw, kh = self.lock.keyhole
                x, y = tool_to_logical(state.tool_x+4.5*3, state.tool_y)
                parents = []
                obj = self.lock
                while obj:
                    parents.append(obj)
                    obj = obj.parent
                for obj in reversed(parents):
                    x = (x - obj.x) / obj.scale
                    y = (y - obj.y) / obj.scale

                insert_remaining = (kx+kw - x)*self.lock_zoom
                if dx > insert_remaining:
                    dx = insert_remaining
                    self.fully_inserted = True
                    self.obj_pos = x, y, self.lock_zoom
                elif y < ky+kh/2:
                    dy += min(dx, abs(ky+kh/2 - y)*self.lock_zoom)
                elif y > ky+kh/2:
                    dy -= min(dx, abs(ky+kh/2 - y)*self.lock_zoom)
                insert_remaining = (kx+kw - x)*self.lock_zoom - dx
                self.visible_len = 9 + insert_remaining / 3

        super().move(dx, dy)

    def draw_stuck(self):
        gl.glPushMatrix()
        x, y, z = self.obj_pos
        gl.glTranslatef(x, y, 0)
        gl.glScalef(3/z, 3/z, 1)
        gl.glColor3f(
            clamp((state.time - self.anim_start)*2, 0.1, 1),
            clamp((state.time - self.anim_start)*2, 0.9, 1),
            clamp((state.time - self.anim_start)*2, 0.9, 1),
        )
        sprites['key_head'].blit(-9, -4.5)
        gl.glPopMatrix()
