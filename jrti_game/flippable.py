import random
import contextlib
import math

from pyglet import gl
from attr import attrs, attrib

from jrti_game.data import spritesheet_texture, letter_uvwh, text_width, kerns


def draw_rect(w, h):
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(0, 0)
    gl.glVertex2f(0, h)
    gl.glVertex2f(w, h)
    gl.glVertex2f(w, 0)
    gl.glVertex2f(0, 0)
    gl.glEnd()


def clamp(value, minimum=0, maximum=1):
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


@attrs()
class Flippable:
    x = attrib(0)
    y = attrib(0)
    width = attrib(8)
    height = attrib(8)
    scale = attrib(1)
    parent = attrib(None)
    color = attrib((1, 1, 1))
    bgcolor = attrib((0, 0, 0))

    drag_info = None, None
    flip_params = (0, 0, 0, 0)
    flip_direction = None
    light_seed = 0

    def __attrs_post_init__(self):
        if self.parent:
            self.parent.children.append(self)

    def draw(self):
        """Draw this. Needs to be reimplemented in subclasses."""

    def mouse_press(self, x, y):
        if self.drag_info[0]:
            self.mouse_release()
        self.drag_start(x, y)
        self.mouse_drag(x, y)

    def mouse_drag(self, x, y):
        if self.drag_info[1]:
            sx, sy = self.drag_info[1]
            dx = abs(sx - x)
            dy = abs(sy - y)
            if self.flip_direction is None:
                direction = abs(sx - x) > abs(sy - y)
                if dx > 4 or dy > 4:
                    self.flip_direction = direction
            else:
                direction = self.flip_direction
            if direction:
                mouse = x
                start = sx
                d = dx
                dim = self.width
            else:
                mouse = y
                start = sy
                d = dy
                dim = self.height
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
                if ratio > 1:
                    ratio = 1
                if ratio < -1:
                    ratio = -1
                angle = math.degrees(math.acos(ratio) * factor)
            if direction:
                self.flip_params = axis, 0, -angle, 0
            else:
                self.flip_params = 0, axis, 0, angle

    def mouse_release(self):
        obj, start = self.drag_info
        if obj and obj is not self:
            obj.mouse_release()
        self.flip_params = None
        self.flip_direction = None
        self.drag_info = None, None

    def hit_test(self, x, y):
        return (0 <= x < self.width) and (0 <= y < self.height)

    def drag_start(self, x, y):
        self.drag_info = self, (x, y)
        self.flip_direction = None
        self.light_seed = random.randint(0, 2**32)

    @contextlib.contextmanager
    def draw_context(self, bg=True, flipping=False):
        try:
            gl.glPushMatrix()
            gl.glTranslatef(self.x, self.y, 0)
            gl.glScalef(self.scale, self.scale, 1)

            if flipping and self.drag_info[0] == self:
                x, y, rx, ry = self.flip_params
                gl.glTranslatef(x, y, 0)
                gl.glRotatef(ry, 1, 0, 0)
                gl.glRotatef(rx, 0, 1, 0)
                gl.glTranslatef(-x, -y, 0)

            if 0*1:  # XXX: debug
                try:
                    r, g, b = self.bgcolor
                except AttributeError:
                    r = random.uniform(0, 1)
                    g = random.uniform(0, 1) * (1-r)
                    b = 1 - r - g
                    self.bgcolor = r, g, b
                if self.drag_info[0] == self:
                    gl.glColor4f(r, g, b, 1)
                elif self.drag_info[0]:
                    gl.glColor4f(r, g, b, 1/2)
                else:
                    gl.glColor4f(r, g, b, 1/4)
                draw_rect(self.width, self.height)

            if bg and self.bgcolor:
                gl.glColor3f(*self.bgcolor)
                draw_rect(self.width, self.height)

            gl.glColor3f(*self.color)

            yield
        finally:
            gl.glPopMatrix()

    def draw_outer(self):
        obj, start = self.drag_info
        with self.draw_context():
            if obj is self:
                self.draw_instructions()
            else:
                self.draw()

    def draw_flipping(self):
        obj, start = self.drag_info
        if obj is self:
            with self.draw_context():
                self.draw_light()
                self.draw_instructions()
            with self.draw_context(flipping=True):
                self.draw()
                self.draw_outline()

                gl.glEnable(gl.GL_CULL_FACE)
                gl.glColor4f(0, 1, 1,
                             clamp(random.normalvariate(3/4, 1/120), 0, 1))
                draw_rect(self.width, self.height)
                gl.glDisable(gl.GL_CULL_FACE)

    def draw_instructions(self):
        gl.glColor4f(0, 1, 1,
                     clamp(random.normalvariate(1, 1/120), 0, 1))
        draw_rect(self.width, self.height)

    def draw_light(self):
        if self.flip_params:
            x, y, rx, ry = self.flip_params
            angle = abs(rx + ry)
            if angle < 90:
                wph = self.width + self.height
                N = wph / 8 * angle / 20 + 2
                if N > 50:
                    N = 50
                r = random.Random()
                r.seed(self.light_seed)
                for i in range(int(N)):
                    p = (angle / 60 / N * i) ** 1.1 / 5
                    diag_angle = math.tau/8
                    diag_angle += r.normalvariate(0, math.tau/16)
                    diag_angle += random.normalvariate(0, math.tau/256)
                    pw = p * wph * math.cos(diag_angle)
                    ph = p * wph * math.sin(diag_angle)
                    points = self.get_light_points(rx, ry, pw, ph)
                    gl.glColor4f(0, 1, 1, (1 - angle / 60) / N * 2)
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
                    (w, h),
                    (w+pw, -ph),
                    (-pw, -ph),
                    (0, h),
                ]
            else:
                return [
                    (0, 0),
                    (-pw, h+ph),
                    (w+pw, h+ph),
                    (w, 0),
                ]
        else:
            return [
                (-pw, -ph),
                (-pw, h+ph),
                (w+pw, h+ph),
                (w+pw, -ph),
            ]

    def draw_outline(self):
        x, y, rx, ry = self.flip_params
        points = self.get_light_points(rx, ry, 0, 0)
        gl.glColor4f(0, 1, 1, 1/2)
        gl.glBegin(gl.GL_LINE_STRIP)
        for point in points:
            gl.glVertex2f(*point)
        if not rx and not ry:
            gl.glVertex2f(*points[0])
        gl.glEnd()


@attrs()
class Layer(Flippable):
    children = attrib(convert=list)

    @children.default
    def _default(self):
        return []

    def drag_start(self, x, y):
        for child in self.children:
            if child.hit_test(x - child.x, y - child.y):
                child.mouse_press(x - child.x, y - child.y)
                self.drag_info = child, (x, y)
                return
        self.drag_info = self, (x, y)

    def draw(self):
        for child in self.children:
            child.draw_outer()

    def draw_flipping(self):
        obj, start = self.drag_info
        if obj is self:
            super().draw_flipping()
        elif obj:
            with self.draw_context(bg=False):
                obj.draw_flipping()

    def mouse_drag(self, x, y):
        obj, start = self.drag_info
        if obj is self:
            super().mouse_drag(x, y)
        elif obj is not None:
            obj.mouse_drag(x - obj.x, y - obj.y)


@attrs()
class Sprite(Flippable):
    u = attrib(0)
    v = attrib(0)
    texture_width = attrib()
    texture_height = attrib()

    @texture_width.default
    def _default(self):
        return self.width

    @texture_height.default
    def _default(self):
        return self.height

    def draw(self):
        try:
            texture = self.texture
        except AttributeError:
            texture = spritesheet_texture.get_region(
                self.u, self.v, self.texture_width, self.texture_height)
            self.texture = texture

        texture.blit(0, 0, width=self.width, height=self.height)

class Letter(Sprite):
    def __init__(self, letter, **kwargs):
        number = ord(letter)
        u, v, width, height = letter_uvwh(letter)
        kwargs.update(
            texture_width=width,
            texture_height=height,
            u=u,
            v=v,
        )
        if 'width' not in kwargs:
            kwargs['width'] = (kwargs['height'] // 8 * width) or 1
        super().__init__(**kwargs)


def letters(string, x=0, y=0, height=8, center=False):
    scale = height // 8
    if center:
        x -= scale * (text_width(string) // 2)
    starting_x = x
    last_char = None
    for character in string:
        if character == '\n':
            y -= height
            x = starting_x
        else:
            x += kerns.get((last_char, character), 0) * scale
            letter = Letter(character, x=x, y=y, height=height)
            x += letter.width
            if character != ' ':
                yield letter
        last_char = character
