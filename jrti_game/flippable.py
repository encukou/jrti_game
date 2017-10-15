import random

from pyglet import gl
from attr import attrs, attrib

from jrti_game.data import spritesheet_texture, letter_uvwh, text_width, kerns


@attrs()
class Flippable:
    x = attrib(0)
    y = attrib(0)
    width = attrib(8)
    height = attrib(8)
    scale = attrib(1)
    parent = attrib(None)
    color = attrib((1, 1, 1))

    drag_info = None, None

    def __attrs_post_init__(self):
        if self.parent:
            self.parent.children.append(self)

    def draw(self):
        """Draw this. Needs to be reimplemented in subclasses."""

    def mouse_press(self, x, y):
        if self.drag_info[0]:
            self.mouse_release()
        return self.drag_start(x, y)

    def mouse_drag(self, x, y):
        pass

    def mouse_release(self):
        obj, start = self.drag_info
        if obj and obj is not self:
            obj.mouse_release()
        self.drag_info = None, None

    def hit_test(self, x, y):
        return (0 <= x < self.width) and (0 <= y < self.height)

    def drag_start(self, x, y):
        self.drag_info = self, (x, y)
        return True

    def draw_outer(self):
        try:
            gl.glPushMatrix()
            gl.glTranslatef(self.x, self.y, 0)
            gl.glScalef(self.scale, self.scale, 1)

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
            gl.glBegin(gl.GL_TRIANGLE_FAN)
            gl.glVertex2f(0, 0)
            gl.glVertex2f(0, self.height)
            gl.glVertex2f(self.width, self.height)
            gl.glVertex2f(self.width, 0)
            gl.glVertex2f(0, 0)
            gl.glEnd()

            gl.glColor3f(*self.color)
            self.draw()
        finally:
            gl.glPopMatrix()


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
                return True
        self.drag_info = self, (x, y)
        return True

    def draw(self):
        for child in self.children:
            child.draw_outer()


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
