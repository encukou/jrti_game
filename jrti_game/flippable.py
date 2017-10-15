from attr import attrs, attrib

from jrti_game.data import spritesheet_texture, letter_uvwh, text_width
from jrti_game.data import RED


@attrs()
class Flippable:
    x = attrib(0)
    y = attrib(0)
    width = attrib(8)
    height = attrib(8)

    def draw(self):
        ...


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
        print(kwargs)
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
