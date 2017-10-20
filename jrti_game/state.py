import types

import pyglet


state = types.SimpleNamespace(
    zoom=1,
    target_zoom=1,
    alt_zoom_start=None,
    last_drag_pos=None,
    center=[0, 0],
    last_mouse_pos=(400, 300),
    time=0,
    tool=None,
    tool_x=0,
    tool_y=0,
    reassign_state=None,
    reassign_anim_start=0,
    keymap={
        pyglet.window.key.LEFT: 'View Left',
        pyglet.window.key.UP: 'View Up',
        pyglet.window.key.DOWN: 'View Down',
        pyglet.window.key.RIGHT: 'View Right',
        pyglet.window.key.ESCAPE: 'Exit',
        pyglet.window.key.X: 'Exit',
        pyglet.window.key.R: 'Reassign',
        pyglet.window.key.G: 'Grabby',
        pyglet.window.key.K: 'Key',
        pyglet.window.key.O: 'Zoom Out',
        pyglet.window.key.P: 'Zoom In',
        pyglet.window.key.W: 'Tool Up',
        pyglet.window.key.A: 'Tool Left',
        pyglet.window.key.S: 'Tool Down',
        pyglet.window.key.D: 'Tool Right',
    },
)
