import random
import contextlib
import math

from pyglet import gl
import pyglet.text
from attr import attrs, attrib

from jrti_game.data import spritesheet_texture, spritesheet_data
from jrti_game.data import instruction_font_name
from jrti_game.instructions import get_instruction_text
from jrti_game.util import clamp, reify, draw_rect, draw_keyhole
from jrti_game.state import state

tau = math.pi*2


@attrs(repr=False)
class Flippable:
    transparent = False

    x = attrib(0)
    y = attrib(0)
    width = attrib(8)
    height = attrib(8)
    scale = attrib(1)
    parent = attrib(None)
    color = attrib((1, 1, 1))
    bgcolor = attrib((0, 0, 0, 1))
    instructions_color=attrib((0.4, 0.9, 1))
    instructions = attrib('None')
    margin = attrib(1)

    drag_info = None, None
    flip_params = None
    flip_direction = None
    open_child_counter = 0
    close_speed = 0
    light_seed = 0

    hides_bugs = False
    num_hiding_bugs = 0
    last_moved = 0

    keyhole = None
    unlocked = None
    keyhole_params = 10, 400
    flip_locked = False

    children = attrib(convert=list)

    @children.default
    def _default(self):
        return []

    def __attrs_post_init__(self):
        if self.parent:
            self.parent.add_child(self)

    def __repr__(self):
        return '<{}: {}>'.format(type(self).__name__, self.instructions)

    def draw(self, zoom, children=True, **kwargs):
        if children:
            for child in self.children:
                child.draw_outer(zoom=zoom*child.scale, **kwargs)

    def tick(self, dt):
        if (self.flip_params and
                self.drag_info[0] is not self and
                not self.flip_locked):
            self.close_speed += (dt * 500000 / (self.width * self.height)**.5 /
                                 self.scale / state.zoom)
            angle = dt * self.close_speed
            x, y, rx, ry = self.flip_params
            if abs(rx) < angle and abs(ry) < angle:
                obj = self
                if obj is self:
                    while obj:
                        obj.open_child_counter -= 1
                        obj = obj.parent
                self.flip_params = None
            else:
                if rx > 0:
                    rx -= angle
                elif rx < 0:
                    rx += angle
                elif ry > 0:
                    ry -= angle
                elif ry < 0:
                    ry += angle
                self.flip_params = x, y, rx, ry

        for child in self.children:
            child.tick(dt)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def die(self):
        self.parent.children.remove(self)
        self.parent = None

    def spawn_bug(self, *args, **kwargs):
        pass

    def grab_move(self, dx, dy):
        pass

    def mouse_press(self, x, y, **kwargs):
        if self.drag_info[0] or self.unlocked:
            self.mouse_release()
        self.drag_start(x, y, **kwargs)
        self.mouse_drag(x, y, **kwargs)

    def mouse_drag(self, x, y, *, zoom=1, **kwargs):
        obj, start = self.drag_info
        if obj is self:
            pass
        elif obj is not None:
            obj.mouse_drag((x - obj.x) / obj.scale, (y - obj.y) / obj.scale,
                           zoom=zoom * obj.scale,
                           **kwargs)
            return
        else:
            return

        if self.drag_info[1]:
            sx, sy = self.drag_info[1]
            dx = abs(sx - x)
            dy = abs(sy - y)
            if self.flip_direction is None:
                if dx > dy:
                    direction = sx - x, 0
                else:
                    direction = 0, sy - y
                if dx > 4/zoom or dy > 4/zoom:
                    self.flip_direction = direction
            else:
                direction = self.flip_direction
            if direction[0]:
                mouse = x
                start = sx
                dim = self.width
                vdir = direction[0]
            else:
                mouse = y
                start = sy
                dim = self.height
                vdir = direction[1]
            if vdir < 0 and mouse < start:
                mouse = start
            if vdir > 0 and mouse > start:
                mouse = start
            if mouse < start:
                axis = 0
                factor = -1
            else:
                axis = dim
                factor = 1
            if start == axis:
                angle = 0
            elif mouse == axis:
                angle = 90 * factor
            else:
                ratio = ((mouse - axis) / (start - axis))
                ratio = clamp(ratio, -1, 1)
                angle = math.degrees(math.acos(ratio) * factor)

            z = zoom
            if abs(angle) > 5 and (
                    z*self.width >= 800 or z*self.height >= 600
                    or self.unlocked):
                self.mouse_release()
                if self.unlocked:
                    self.unlocked.anim_start = state.time
                angle = clamp(angle, -5, 5)

            if direction[0]:
                self.flip_params = axis, 0, -angle, 0
            else:
                self.flip_params = 0, axis, 0, -angle

    def mouse_release(self, **kwargs):
        obj, start = self.drag_info
        if obj and obj is not self:
            obj.mouse_release()
        self.flip_direction = None
        self.drag_info = None, None
        self.close_speed = 0

    def hit_test(self, x, y):
        return (0 <= x < self.width) and (0 <= y < self.height)

    def hit_test_grab(self, x, y):
        return False

    def hit_test_slab(self, x, y, w, h):
        for ex in range(int(x), int(x) + int(math.ceil(w)) or 1):
            for ey in range(int(y), int(y) + int(math.ceil(h)) or 1):
                if self.hit_test(ex, ey) and self.hit_test_grab(ex, ey):
                    return True
        return False

    def hit_test_overlap(self, x, a, b, mode):
        return -100

    def hit_test_all(self, x, y):
        if self.hit_test(x, y):
            for child in reversed(self.children):
                yield from child.hit_test_all((x - child.x) / child.scale,
                                              (y - child.y) / child.scale)
            yield self, x, y

    def draw_grab(self, **kwargs):
        parents = []
        obj = self
        while obj:
            parents.append(obj)
            obj = obj.parent
        with contextlib.ExitStack() as stack:
            for obj in reversed(parents):
                stack.enter_context(obj.draw_context(bg=False))
            if self.bgcolor[:3] == (0, 0, 0):
                gl.glColor4f(0.0, 0.2, 0.1, 1 / 3)
                draw_rect(self.width, self.height)
            self.draw_outline((0.1, 0.9, 0.4), 0.7)

    def drag_start(self, x, y, zoom, **kwargs):
        self.flip_locked = False
        for child in reversed(self.children):
            cx = (x - child.x) / child.scale
            cy = (y - child.y) / child.scale
            if child.hit_test(cx, cy):
                child.mouse_press(cx, cy, zoom=zoom*child.scale, **kwargs)
                self.drag_info = child, (x, y)
                return

        self.drag_info = self, (x, y)
        self.flip_direction = None
        self.light_seed = random.randint(0, 2**32)

        if state.tool.grabbing is self:
            state.tool.deactivate()

        obj = self
        while obj:
            obj.open_child_counter += 1
            obj = obj.parent

    @contextlib.contextmanager
    def draw_context(self, bg=True, flipping=False, **kwargs):
        gl.glPushMatrix()
        try:
            gl.glTranslatef(self.x, self.y, 0)
            gl.glScalef(self.scale, self.scale, self.scale)

            if flipping and self.flip_params:
                x, y, rx, ry = self.flip_params
                gl.glTranslatef(x, y, 0)
                gl.glRotatef(-ry, 1, 0, 0)
                gl.glRotatef(rx, 0, 1, 0)
                gl.glTranslatef(-x, -y, 0)

            if bg and self.bgcolor:
                gl.glColor4f(*self.bgcolor)
                draw_rect(self.width, self.height)

            gl.glColor3f(*self.color)

            yield
        finally:
            gl.glPopMatrix()

    def draw_outer(self, **kwargs):
        with self.draw_context(bg=False, **kwargs):
            if not self.flip_params:
                self.draw(**kwargs)
                if self.unlocked:
                    self.unlocked.draw_stuck()

    def draw_flipping(self, zoom, **kwargs):
        if self.flip_params:
            with self.draw_context(zoom=zoom, **kwargs):
                self.draw_light(zoom=zoom, **kwargs)
                self.draw_instructions(zoom=zoom, **kwargs)
            with self.draw_context(flipping=True, bg=True, zoom=zoom,
                                   **kwargs):
                self.draw(zoom=zoom, **kwargs)
                if self.unlocked:
                    self.unlocked.draw_stuck()
                self.draw_outline(zoom=zoom, **kwargs)

                gl.glEnable(gl.GL_CULL_FACE)
                gl.glColor4f(*self.instructions_color,
                             clamp(random.normalvariate(3/4, 1/120), 0, 1))
                draw_rect(self.width, self.height)
                gl.glDisable(gl.GL_CULL_FACE)

        if self.children and self.open_child_counter:
            with self.draw_context(bg=False, flipping=self.flip_params,
                                   zoom=zoom):
                for obj in self.children:
                    obj.draw_flipping(zoom=zoom*obj.scale, **kwargs)

    def draw_instructions(self, **kwargs):
        gl.glColor4f(*self.instructions_color,
                     clamp(random.normalvariate(1, 1/120), 0, 1))
        draw_rect(self.width, self.height)

        gl.glColor3f(0, 0, 0)
        if self.instruction_label:
            scale = self.instruction_label._jrti_scale
            gl.glScalef(1/scale, 1/scale, 1)
            self.instruction_label.draw()
        gl.glBindTexture(gl.GL_TEXTURE_2D, spritesheet_texture.id)

    @reify
    def instruction_label(self):
        scale = 1
        while self.width * scale < 400 and self.height * scale < 300:
            scale *= 1.1
        document = pyglet.text.document.UnformattedDocument(
            get_instruction_text(self.instructions)
        )
        document.set_style(0, 0, {
            'color': (0, 0, 0, 255),
            'font_name': instruction_font_name,
            'font_size': 25,
        })
        if self.width < self.margin*3 or self.height < self.margin*3:
            return None
        layout = pyglet.text.layout.TextLayout(
            document,
            width=(self.width - self.margin*2) * scale,
            height=(self.height - self.margin*2) * scale,
            multiline=True,
        )
        layout.x = self.margin * scale
        layout.y = self.margin * scale
        for size in range(25, 1, -1):
            if (layout.content_width > layout.width or
                    layout.content_height > layout.height):
                document.set_style(0, 0, {'font_size': size})
        for size in range(10, 1, -1):
            if (layout.content_width > layout.width or
                    layout.content_height > layout.height):
                document.set_style(0, 0, {'font_size': size/10})
        layout._jrti_scale = scale
        return layout

    def update_instructions(self):
        try:
            del self.instruction_label
        except AttributeError:
            pass
        for child in self.children:
            child.update_instructions()

    def draw_light(self, **kwargs):
        if self.flip_params:
            x, y, rx, ry = self.flip_params
            angle = abs(rx + ry)
            if angle < 90:
                wph = self.width + self.height
                N = 80 / (angle+1) * 20 * self.scale + 2
                if N > 50:
                    N = 50
                r = random.Random()
                r.seed(self.light_seed)
                for i in range(int(N)):
                    p = (angle / 60 / N * i) ** 1.1 / 5
                    diag_angle = tau/8
                    diag_angle += r.normalvariate(0, tau/16)
                    diag_angle += random.normalvariate(0, tau/256)
                    pw = p * wph * math.cos(diag_angle)
                    ph = p * wph * math.sin(diag_angle)
                    points = self.get_light_points(rx, ry, pw, ph)
                    gl.glColor4f(*self.instructions_color,
                                 (1 - angle / 60) / N * 2)
                    gl.glBegin(gl.GL_TRIANGLE_FAN)
                    for point in points:
                        gl.glVertex2f(*point)
                    gl.glVertex2f(*points[0])
                    gl.glEnd()

    def get_light_points(self, rx, ry, pw, ph):
        w = self.width
        h = self.height
        if rx:
            if rx > 0:
                return [
                    (0, h),
                    (w+pw, h+ph),
                    (w+pw, -ph),
                    (0, 0),
                ]
            else:
                return [
                    (w, 0),
                    (-pw, -ph),
                    (-pw, h+ph),
                    (w, h),
                ]
        elif ry:
            if ry > 0:
                return [
                    (0, 0),
                    (-pw, h+ph),
                    (w+pw, h+ph),
                    (w, 0),
                ]
            else:
                return [
                    (w, h),
                    (w+pw, -ph),
                    (-pw, -ph),
                    (0, h),
                ]
        else:
            return [
                (-pw, -ph),
                (-pw, h+ph),
                (w+pw, h+ph),
                (w+pw, -ph),
            ]

    def draw_outline(self, color=None, alpha=1/2, **kwargs):
        if self.flip_params is None:
            dx = dy = 0
        elif self.flip_direction is None:
            dummy, rummy, dx, dy = self.flip_params
        else:
            dx, dy = self.flip_direction
        points = self.get_light_points(dx, dy, 0, 0)
        gl.glColor4f(*(color or self.instructions_color), alpha)
        gl.glBegin(gl.GL_LINE_STRIP)
        for point in points:
            gl.glVertex2f(*point)
        if dx == dy == 0:
            gl.glVertex2f(*points[0])
        gl.glEnd()

    def accepts_key(self, key):
        return bool(self.keyhole)

    def unlock(self, key):
        if self.keyhole:
            self.unlocked = key


Layer = Flippable


@attrs(repr=False)
class Sprite(Flippable):
    u = attrib(0)
    v = attrib(0)
    texture_width = attrib()
    texture_height = attrib()

    @texture_width.default
    def _default_w(self):
        return self.width

    @texture_height.default
    def _default_h(self):
        return self.height

    def draw(self, zoom, **kwargs):
        try:
            texture = self.texture
        except AttributeError:
            texture = spritesheet_texture.get_region(
                self.u, self.v, self.texture_width, self.texture_height-1)
            self.texture = texture

        texture.blit(0, 0, width=self.width, height=self.height-1)

        super().draw(zoom=zoom, **kwargs)

    def pixel(self, x, y):
        return spritesheet_data[self.v+y][self.u+x]

    def hit_test_grab(self, x, y):
        return self.pixel(int(x), int(y))

    def hit_test_overlap(self, s, a, b, mode):
        dists = []
        a += 0.0001
        a -= 1
        b -= 0.0001
        for x in range(self.width):
            for y in range(self.height):
                if self.pixel(x, y):
                    if mode == 'x+':
                        if a <= y < b:
                            dists.append(s-x-1)
                    elif mode == 'x-':
                        if a <= y < b:
                            dists.append(x-s)
                    elif mode == 'y+':
                        if a <= x < b:
                            dists.append(s-y-1)
                    elif mode == 'y-':
                        if a <= x < b:
                            dists.append(y-s)
        if not dists:
            return -100
        else:
            return min(dists)
