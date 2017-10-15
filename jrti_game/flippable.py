import random

from pyglet import gl
from attr import attrs, attrib

from jrti_game.data import spritesheet_texture, letter_uvwh, text_width


@attrs()
class Flippable:
    x = attrib(0)
    y = attrib(0)
    width = attrib(8)
    height = attrib(8)
    parent = attrib(None)

    def __attrs_post_init__(self):
        if self.parent:
            self.parent.children.append(self)

    def draw(self):
        ...


@attrs()
class Layer(Flippable):
    scale = attrib(1)
    children = attrib(convert=list)

    @children.default
    def _default(self):
        return []

    def draw(self):
        try:
            gl.glPushMatrix()
            gl.glTranslatef(self.x, self.y, 0)
            gl.glScalef(self.scale, self.scale, 1)

            print(self.width, self.height)
            gl.glColor3f(random.uniform(0, 1)/2, random.uniform(0, 1)/2, random.uniform(0, 1)/2)
            gl.glBegin(gl.GL_TRIANGLE_FAN)
            gl.glVertex2f(0, 0)
            gl.glVertex2f(0, self.height)
            gl.glVertex2f(self.width, self.height)
            gl.glVertex2f(self.width, 0)
            gl.glVertex2f(0, 0)
            gl.glEnd()

            gl.glColor3f(1., 1., 1.)
            for child in self.children:
                child.draw()
        finally:
            gl.glPopMatrix()


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

        texture.blit(self.x, self.y, width=self.width, height=self.height)

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
    if center:
        x -= height // 8 * (text_width(string) // 2)
    starting_x = x
    for character in string:
        if character == ' ':
            x += height // 8 * 6
        elif character == '\n':
            y -= height
            x = starting_x
        else:
            letter = Letter(character, x=x, y=y, height=height)
            x += letter.width
            yield letter
